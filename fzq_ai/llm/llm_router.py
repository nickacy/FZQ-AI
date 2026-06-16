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

        # In-memory response cache (for run_cached)
        self._cache: dict[str, str] = {}

    # ── External API ──────────────────────────────────────────

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

    async def run_json(
        self,
        prompt: str,
        model: str = "deepseek",
        **kwargs: Any,
    ) -> dict:
        """Call LLM and parse JSON response with repair."""
        import json as _json
        text: str = ""
        try:
            text = await self.run(prompt, model=model, **kwargs)
            text_stripped: str = text.strip()
            if text_stripped.startswith("```"):
                lines: list[str] = text_stripped.split("\n")
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text_stripped = "\n".join(lines)
            return _json.loads(text_stripped)
        except _json.JSONDecodeError as e:
            return {"_raw": text, "_error": f"JSON parse error: {e}"}
        except RuntimeError as e:
            return {"_error": str(e)}
        except Exception as e:
            return {"_error": f"Unexpected: {e}"}

    async def run_cached(
        self,
        prompt: str,
        model: str = "deepseek",
        cache_key: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Call LLM with simple in-memory caching."""
        import hashlib
        key: str = cache_key or hashlib.sha256(
            (prompt + model).encode()
        ).hexdigest()
        if key in self._cache:
            return self._cache[key]
        result: str = await self.run(prompt, model=model, **kwargs)
        self._cache[key] = result
        if len(self._cache) > 100:
            self._cache.pop(next(iter(self._cache)))
        return result

    def check_availability(self) -> dict[str, bool]:
        """Check all providers; never raises, logs failures."""
        status: dict[str, bool] = {}
        for name, state in self._states.items():
            status[name] = state.healthy
        return status

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

    # ── v6.0: 智能路由 (任务类型 → 模型) ─────────────────────

    TASK_MODEL_MAP = {
        "event_extraction":      ["openai", "gemini"],
        "multilingual_summary":  ["gemini", "openai"],
        "deep_reasoning":        ["deepseek", "openai"],
        "structured_extraction": ["openai", "gemini"],
        "news_intel":            ["openai", "deepseek", "gemini"],
    }

    FALLBACK_CHAIN = ["openai", "deepseek", "gemini"]

    async def route(self, task_type: str, prompt: str, **kwargs) -> str:
        """
        v6.0: Task-based intelligent model routing.

        Args:
            task_type: event_extraction | multilingual_summary |
                       deep_reasoning | structured_extraction | news_intel
            prompt: The prompt to send
            **kwargs: temperature, max_tokens, system_prompt, retries

        Returns:
            LLM response text

        Raises:
            RuntimeError: If all providers in the routing chain fail
        """
        preferred_models = self.TASK_MODEL_MAP.get(
            task_type, self.FALLBACK_CHAIN
        )
        # Try preferred models first, then fallback chain
        ordered = list(preferred_models) + [
            m for m in self.FALLBACK_CHAIN if m not in preferred_models
        ]
        return await self._call_ordered(prompt, ordered, **kwargs)

    async def _call_ordered(
        self, prompt: str, model_order: list, **kwargs
    ) -> str:
        """Call providers in specified order with failover."""
        last_error = None
        for model_name in model_order:
            try:
                return await self._call_provider(prompt, model_name, **kwargs)
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(
            f"All providers failed in order {model_order}. "
            f"Last error: {last_error}"
        ) from last_error

    async def _call_provider(
        self, prompt: str, model_name: str, **kwargs
    ) -> str:
        """Call a specific provider by name."""
        provider = self._providers_map.get(model_name)
        if not provider:
            raise ValueError(f"Unknown provider: {model_name}")
        return await provider.run(
            prompt,
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 2000),
            system_prompt=kwargs.get("system_prompt", ""),
            retries=kwargs.get("retries", 1),
        )

    @property
    def _providers_map(self) -> dict:
        return {
            "deepseek": self.deepseek,
            "openai": self.openai,
            "gemini": self.gemini,
        }

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
