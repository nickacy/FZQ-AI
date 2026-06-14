from __future__ import annotations
from typing import Any
from openai import OpenAI

from fzq_ai.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
)


class DeepSeekClient:
    """
    DeepSeek API 的真实可用客户端
    """

    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置，请检查 .env 文件")

        # ⭐ DeepSeek 必须使用 /v1
        base_url = DEEPSEEK_BASE_URL.rstrip("/") + "/v1"

        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=base_url)
        self.model = DEEPSEEK_MODEL

    async def run(self, prompt: str, **kwargs: Any) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"[DeepSeek API Error] {str(e)}"
