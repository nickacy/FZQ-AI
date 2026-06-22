import aiohttp
import os
from fzq_ai.schemas.llm import LLMRequestSchema


class GLMProvider:
    """Zhipu GLM 5.2 Provider"""

    def __init__(self):
        self.api_key = os.getenv("GLM_API_KEY", "")
        self.model = os.getenv("GLM_MODEL", "glm-4-flash")
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

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
