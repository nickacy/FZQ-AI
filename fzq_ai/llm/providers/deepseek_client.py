"""
DeepSeek Provider — production-ready async client.
Uses OpenAI-compatible SDK with proper async, error handling, and usage tracking.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from openai import AsyncOpenAI

from fzq_ai.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class DeepSeekClient:
    """Async DeepSeek API client with retry, usage tracking, and prompt cache support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required. Set it in .env or pass directly.")

        # Fix: never double-append /v1 — normalize once
        raw_url = (base_url or DEEPSEEK_BASE_URL).rstrip("/")
        # If the user already included /v1, keep it; otherwise append
        if not raw_url.endswith("/v1"):
            raw_url += "/v1"
        self.base_url = raw_url

        self.model = model or DEEPSEEK_MODEL
        self.timeout = timeout

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,  # We control retries ourselves
        )

        # Usage tracking
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cache_hit_tokens: int = 0

    # ── Core API ───────────────────────────────────────────────

    async def run(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
        retries: int = 3,
    ) -> str:
        """Async chat completion with retry and proper error handling."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Track usage
                if response.usage:
                    self.total_prompt_tokens += response.usage.prompt_tokens or 0
                    self.total_completion_tokens += response.usage.completion_tokens or 0
                    # DeepSeek-specific: prompt cache tokens
                    cache_hit = getattr(response.usage, "prompt_cache_hit_tokens", 0) or 0
                    self.total_cache_hit_tokens += cache_hit

                choice = response.choices[0]
                # Fix: use attribute access, not dict access
                content = choice.message.content or ""
                return content

            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    time.sleep(wait)  # non-blocking sleep for retry backoff

        # All retries exhausted — raise, don't swallow
        raise RuntimeError(
            f"DeepSeek API call failed after {retries} attempts: {last_error}"
        ) from last_error

    async def run_with_messages(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        retries: int = 3,
    ) -> str:
        """Async chat completion with full message list."""
        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if response.usage:
                    self.total_prompt_tokens += response.usage.prompt_tokens or 0
                    self.total_completion_tokens += response.usage.completion_tokens or 0
                    cache_hit = getattr(response.usage, "prompt_cache_hit_tokens", 0) or 0
                    self.total_cache_hit_tokens += cache_hit

                return response.choices[0].message.content or ""

            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    await _async_sleep(2 ** attempt)

        raise RuntimeError(
            f"DeepSeek API call failed after {retries} attempts: {last_error}"
        ) from last_error

    @property
    def usage_stats(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "cache_hit_tokens": self.total_cache_hit_tokens,
        }


async def _async_sleep(seconds: float) -> None:
    """Non-blocking async sleep."""
    import asyncio
    await asyncio.sleep(seconds)
