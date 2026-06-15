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
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.timeout = timeout

        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
        else:
            self.client = None

    async def run(
        self,
        """Async chat completion with retry."""
        if not self.client:
            raise RuntimeError("OpenAI API key not configured. Set OPENAI_API_KEY in .env")

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.model,
                return response.choices[0].message.content or ""

            except Exception as e:
                if attempt < retries - 1:

        raise RuntimeError(
            f"OpenAI API call failed after {retries} attempts: {last_error}"
