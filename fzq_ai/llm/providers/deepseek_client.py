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
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required. Set it in .env or pass directly.")

        # Fix: never double-append /v1 — normalize once
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

        # Usage tracking
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cache_hit_tokens: int = 0

    # ── Core API ───────────────────────────────────────────────

    async def run(
        self,
        """Async chat completion with retry and proper error handling."""
        if system_prompt:

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.model,

                # Track usage
                if response.usage:
                    self.total_prompt_tokens += response.usage.prompt_tokens or 0
                    self.total_completion_tokens += response.usage.completion_tokens or 0
                    # DeepSeek-specific: prompt cache tokens
                    self.total_cache_hit_tokens += cache_hit

                # Fix: use attribute access, not dict access
                return content

            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(wait)  # non-blocking sleep for retry backoff

        # All retries exhausted — raise, don't swallow
        raise RuntimeError(
            f"DeepSeek API call failed after {retries} attempts: {last_error}"

    async def run_with_messages(
        self,
        """Async chat completion with full message list."""

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.model,
                if response.usage:
                    self.total_prompt_tokens += response.usage.prompt_tokens or 0
                    self.total_completion_tokens += response.usage.completion_tokens or 0
                    self.total_cache_hit_tokens += cache_hit

                return response.choices[0].message.content or ""

            except Exception as e:
                if attempt < retries - 1:

        raise RuntimeError(
            f"DeepSeek API call failed after {retries} attempts: {last_error}"

    @property
    def usage_stats(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "cache_hit_tokens": self.total_cache_hit_tokens,

async def _async_sleep(seconds: float) -> None:
    """Non-blocking async sleep."""
