"""
Google Gemini Provider — real async client via google-genai SDK.
Used as second fallback.
"""

from __future__ import annotations

import os
from typing import Any, Optional


class GeminiClient:
    """Async Google Gemini API client with retry support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                self._client = None  # Will raise on first call

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
        if not self._client:
            if not self.api_key:
                raise RuntimeError("Gemini API key not configured. Set GEMINI_API_KEY in .env")
            raise RuntimeError(
                "google-genai SDK not installed. Run: pip install google-genai"
            )

        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                from google.genai import types as genai_types

                response = await self._client.aio.models.generate_content(
                    model=model or self.model,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                return response.text or ""

            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Gemini API call failed after {retries} attempts: {last_error}"
        ) from last_error
