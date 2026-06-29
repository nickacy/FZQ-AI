# src/fzq_ai/llm/clients/glm_api.py
# V20 GLM API Client — unified chat interface

from __future__ import annotations
from typing import Any, Dict
import os
import aiohttp


class GLMAPI:
    """
    V20 GLM API 客户端
    Provider.run() 会调用本类的 chat()
    """

    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("ZHIPU_API_KEY")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

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

                # GLM 返回结构统一化
                content = data["choices"][0]["message"]["content"]

                usage = {
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                }

                return {
                    "content": content,
                    "usage": usage,
                }
