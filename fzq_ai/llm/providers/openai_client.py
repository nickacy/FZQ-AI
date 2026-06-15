"""
OpenAI Provider — real async client via OpenAI SDK.
Used as fallback when DeepSeek is unavailable.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from openai import AsyncOpenAI


class OpenAIClient:
    """Async OpenAI API client with retry support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.timeout = timeout

        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=0,
            )
        else:
            self.client = None

    async def run(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        retries: int = 2,
    ) -> str:
        """Async chat completion with retry."""
        if not self.client:
            raise RuntimeError("OpenAI API key not configured. Set OPENAI_API_KEY in .env")

        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""

            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"OpenAI API call failed after {retries} attempts: {last_error}"
        ) from last_error
