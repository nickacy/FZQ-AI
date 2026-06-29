# src/fzq_ai/llm/clients/gemini_api.py
# V20 Gemini API Client — unified chat interface

from __future__ import annotations
from typing import Any, Dict
import os
import aiohttp


class GeminiAPI:
    """
    V20 Gemini API 客户端
    Provider.run() 会调用本类的 chat()
    """

    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def chat(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一 chat 接口
        Provider.run() 会调用这里
        """

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": req["messages"][-1]["content"]}
                    ]
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}?key={self.api_key}",
                json=payload,
            ) as resp:
                data = await resp.json()

                # Gemini 返回结构不同，需要统一格式
                content = data["candidates"][0]["content"]["parts"][0]["text"]

                usage = {
                    "prompt_tokens": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "completion_tokens": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                }

                return {
                    "content": content,
                    "usage": usage,
                }
