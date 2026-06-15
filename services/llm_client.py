"""
Multi-model LLM client (standalone service layer).
Uses fzq_ai.llm for actual provider calls.
"""

from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

class LLMClient:
    """Standalone LLM client supporting DeepSeek, OpenAI, and Qwen."""

    def __init__(
        self,
        self.provider = provider.lower()

        if self.provider == "deepseek":
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
            self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            raw_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip("/")
            if not raw_url.endswith("/v1"):
                raw_url += "/v1"
            self.base_url = raw_url

        elif self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
            self.base_url = base_url or "https://api.openai.com/v1"

        elif self.provider == "qwen":
            self.api_key = api_key or os.getenv("QWEN_API_KEY", "")
            self.model = model or os.getenv("QWEN_MODEL", "qwen-plus")
            self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"

        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

        if not self.api_key:
            raise ValueError(f"API key not set for provider '{self.provider}'. Check .env file.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def ask(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Synchronous chat completion."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
            return response.choices[0].message.content or ""

        except Exception as e:
            raise RuntimeError(f"[LLM ERROR] {self.provider}: {e}") from e
