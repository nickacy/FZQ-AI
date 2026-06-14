# fzq_ai/llm/providers/openai_client.py

from __future__ import annotations
from typing import Any
import asyncio


class OpenAIClient:
    """
    OpenAI API 的最小可运行客户端。
    """

    async def run(self, prompt: str, **kwargs: Any) -> str:
        await asyncio.sleep(0.1)
        return f"[OpenAI mock response] {prompt[:200]}"
