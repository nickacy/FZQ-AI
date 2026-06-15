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
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._client = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                self._client = None  # Will raise on first call

    async def run(
        self,
        """Async chat completion with retry."""
        if not self._client:
            if not self.api_key:
                raise RuntimeError("Gemini API key not configured. Set GEMINI_API_KEY in .env")
            raise RuntimeError(
                "google-genai SDK not installed. Run: pip install google-genai"

        for attempt in range(retries):
            try:

                response = await self._client.aio.models.generate_content(
                    model=model or self.model,
                return response.text or ""

            except Exception as e:
                if attempt < retries - 1:

        raise RuntimeError(
            f"Gemini API call failed after {retries} attempts: {last_error}"
