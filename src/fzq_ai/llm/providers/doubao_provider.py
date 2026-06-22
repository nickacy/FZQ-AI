import aiohttp
import os
from fzq_ai.schemas.llm import LLMRequestSchema


class DoubaoProvider:
    """ByteDance Doubao Provider"""

    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY", "")
        self.model = os.getenv("DOUBAO_MODEL", "doubao-pro-32k")
        self.url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    async def run(self, req: LLMRequestSchema) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": req.prompt}],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                data = await resp.json()
                try:
                    return data["choices"][0]["message"]["content"]
                except Exception:
                    return str(data)
