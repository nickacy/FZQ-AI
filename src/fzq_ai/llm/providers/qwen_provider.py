import aiohttp
import os
from fzq_ai.schemas.llm import LLMRequestSchema


class QwenProvider:
    """Alibaba Qwen Provider"""

    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY", "")
        self.model = os.getenv("QWEN_MODEL", "qwen-max")
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    async def run(self, req: LLMRequestSchema) -> Dict[str, Any]:
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
                    content = data["choices"][0]["message"]["content"]
                except Exception:
                    content = str(data)
                return {
                    "content": content,
                    "provider": "qwen",
                    "model": self.model,
                    "usage": data.get("usage", {}),
                    "latency_ms": 0,
                    "finish_reason": data.get("choices", [{}])[0].get("finish_reason", "stop"),
                    "raw_response": data,
                    "error": None,
                }
