# fzq_ai/llm/providers/minimax_client.py

import aiohttp
import os


class MiniMaxClient:
    """
    MiniMax LLM Provider（兼容 v6.0 架构）
    - 支持 async 调用
    - 支持 JSON mode
    - 与 OpenAI / DeepSeek 接口保持一致
    """

    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY", "")
        self.model = os.getenv("MINIMAX_MODEL", "abab6.5-chat")

        self.url = "https://api.minimax.chat/v1/text/chatcompletion"

    async def run(self, prompt: str, response_format=None) -> str:
        """
        统一接口：与 OpenAIClient / DeepSeekClient 完全一致
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        # ⭐ JSON mode 支持
        if response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                data = await resp.json()

                # MiniMax 返回格式：
                # {
                #   "choices": [
                #       {"message": {"content": "..."}}
                #   ]
                # }
                try:
                    return data["choices"][0]["message"]["content"]
                except Exception:
                    return str(data)
