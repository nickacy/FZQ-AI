# src/fzq_ai/llm/clients/qwen_api.py
# V19 Qwen API Client — unified chat interface

from __future__ import annotations
from typing import Any, Dict
import os
import aiohttp


class QwenAPI:
    """
    V19 Qwen API 客户端
    Provider.run() 会调用本类的 chat()
    """

    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/chat/completions"

    async def chat(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一 chat 接口
        Provider.run() 会调用这里
        """

        payload = {
            "model": self.model,
            "input": {
                "messages": req["messages"]
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
            ) as resp:
                data = await resp.json()

                # Qwen 返回结构统一化
                content = data["output"]["choices"][0]["message"]["content"]

                usage = {
                    "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                }

                return {
                    "content": content,
                    "usage": usage,
                }
