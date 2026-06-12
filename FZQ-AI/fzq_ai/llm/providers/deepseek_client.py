# fzq_ai/llm/providers/deepseek_client.py

from __future__ import annotations
from typing import Any
import asyncio

class DeepSeekClient:
    """
    DeepSeek API 的最小可运行客户端。
    你后续可以替换为真实 API 调用。
    """

    async def run(self, prompt: str, **kwargs: Any) -> str:
        # 这里先返回 mock，后续 Phase 6 再接入真实 DeepSeek API
        await asyncio.sleep(0.1)
        return f"[DeepSeek mock response] {prompt[:200]}"
