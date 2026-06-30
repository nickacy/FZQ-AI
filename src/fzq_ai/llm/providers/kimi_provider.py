import aiohttp
from typing import Any, Dict, Union
import os
from fzq_ai.schemas.llm import LLMRequestSchema


class KimiProvider:
    """Moonshot KIMI Provider"""

    def __init__(self, model: str = None):
        self.api_key = os.getenv("KIMI_API_KEY", "")
        self.model = model or os.getenv("KIMI_MODEL", "moonshot-v1-32k")
        self.url = "https://api.moonshot.cn/v1/chat/completions"

    async def run(self, req: Union[LLMRequestSchema, Dict[str, Any]]) -> Dict[str, Any]:
        """统一接口：接受 LLMRequestSchema 或 dict。"""
        # 从 dict/Schema 中提取 prompt
        if isinstance(req, dict):
            if "messages" in req:
                prompt = ""
                for msg in req["messages"]:
                    if msg.get("role") == "user":
                        prompt = msg.get("content", "")
                        break
            else:
                prompt = req.get("prompt", "")
        else:
            prompt = req.prompt

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                data = await resp.json()
                try:
                    content = data["choices"][0]["message"]["content"]
                except Exception:
                    content = str(data)
                usage = data.get("usage", {})
                return {
                    "output": content,
                    "model": self.model,
                    "provider": "kimi",
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
