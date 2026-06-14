"""
LLM Router with automatic failover, health tracking, and fallback chain.
Primary: DeepSeek → Fallback 1: OpenAI → Fallback 2: Gemini
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

from fzq_ai.llm.providers.deepseek_client import DeepSeekClient
from fzq_ai.llm.providers.openai_client import OpenAIClient
from fzq_ai.llm.providers.gemini_client import GeminiClient


class ProviderState:
    """Runtime health tracking for a provider."""

    def __init__(self, name: str):
        self.name = name
        self.healthy = True
        self.consecutive_failures: int = 0
        self.total_calls: int = 0
        self.total_failures: int = 0
        self.last_health_check: float = 0.0

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.total_calls += 1
        self.healthy = True

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.total_calls += 1
        self.total_failures += 1
        if self.consecutive_failures >= 3:
            self.healthy = False


class LLMRouter:
    """
    Multi-provider LLM router with automatic failover.

    Priority chain: DeepSeek → OpenAI → Gemini
    Unhealthy providers are skipped until they recover.
    """

    def __init__(self):
        # Primary
        try:
            self.deepseek = DeepSeekClient()
            self._has_deepseek = True
        except ValueError:
            self.deepseek = None
            self._has_deepseek = False

        # Fallback 1
        self.openai = OpenAIClient()
        self._has_openai = bool(self.openai.api_key)

        # Fallback 2
        try:
            self.gemini = GeminiClient()
            self._has_gemini = bool(self.gemini.api_key)
        except Exception:
            self._has_gemini = False

        # Health states
        self._states: dict[str, ProviderState] = {
            "deepseek": ProviderState("deepseek"),
            "openai": ProviderState("openai"),
            "gemini": ProviderState("gemini"),
        }

        self._providers: list[tuple[str, Any]] = []
        if self._has_deepseek:
            self._providers.append(("deepseek", self.deepseek))
        if self._has_openai:
            self._providers.append(("openai", self.openai))
        if self._has_gemini:
            self._providers.append(("gemini", self.gemini))

        if not self._providers:
            raise RuntimeError(
                "No LLM provider configured. Set at least one of: "
                "DEEPSEEK_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY"
            )

    # ── External API (backward compatible) ─────────────────────

    async def run(
        self,
        prompt: str,
        model: str = "deepseek",
        **kwargs: Any,
    ) -> str:
        """
        Call LLM with automatic failover.

        Args:
            prompt: The user prompt
            model: Preferred provider hint ("deepseek", "openai", "gemini")
            **kwargs: temperature, max_tokens, system_prompt, retries

        Returns:
            LLM response text

        Raises:
            RuntimeError: If all providers fail
        """
        return await self._call_with_failover(prompt, preferred=model, **kwargs)

    # ── Core Logic ─────────────────────────────────────────────

    async def _call_with_failover(
        self,
        prompt: str,
        *,
        preferred: str = "deepseek",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
        retries: int = 3,
        **kwargs: Any,
    ) -> str:
        """
        Try preferred provider first, then fall through the chain.
        Skips unhealthy providers.
        """
        last_error: Optional[Exception] = None

        # Build ordered provider list: preferred first, then others
        ordered = []
        for name, client in self._providers:
            if name == preferred:
                ordered.insert(0, (name, client))
            else:
                ordered.append((name, client))

        for name, client in ordered:
            state = self._states[name]
            if not state.healthy:
                # Periodic health recheck
                if time.time() - state.last_health_check > 30:
                    state.last_health_check = time.time()
                    state.healthy = True  # Give it another chance
                else:
                    continue

            try:
                result = await client.run(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    retries=min(retries, 2),  # Per-provider retries
                )
                state.record_success()
                return result

            except Exception as e:
                state.record_failure()
                last_error = e

        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        ) from last_error

    # ── Health & Metrics ───────────────────────────────────────

    @property
    def metrics(self) -> dict:
        """Return per-provider health metrics for monitoring."""
        return {
            name: {
                "healthy": state.healthy,
                "total_calls": state.total_calls,
                "failures": state.total_failures,
                "failure_rate": (
                    round(state.total_failures / max(state.total_calls, 1), 4)
                ),
            }
            for name, state in self._states.items()
        }

    @property
    def primary_provider(self) -> str:
        return self._providers[0][0] if self._providers else "none"

    def __repr__(self) -> str:
        providers = [name for name, _ in self._providers]
        return f"LLMRouter(providers={providers})"
