# src/fzq_ai/llm/clients/openai_api.py
# V20 OpenAI API Client — unified chat interface

from __future__ import annotations
from typing import Any, Dict
import os
import aiohttp


class OpenAIAPI:
    """
    V20 OpenAI API 客户端
    Provider.run() 会调用本类的 chat()
    """

    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def chat(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一 chat 接口
        Provider.run() 会调用这里
        """

        payload = {
            "model": self.model,
            "messages": req["messages"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            ) as resp:
                data = await resp.json()

                return {
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data["usage"],
                }
