"""
ModelClient - Unified LLM client adapter.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ModelClient:
    """Unified LLM client adapter for all providers."""

    _OPENAI_COMPATIBLE = {"deepseek", "openai", "glm-5.2", "qwen", "kimi", "minimax", "doubao"}

    _BASE_URLS: Dict[str, str] = {
        "deepseek": "https://api.deepseek.com",
        "openai": "https://api.openai.com/v1",
        "glm-5.2": "https://open.bigmodel.cn/api/paas/v4",
        "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "kimi": "https://api.moonshot.cn/v1",
        "minimax": "https://api.minimax.chat/v1",
    }

    _DEFAULT_MODELS: Dict[str, str] = {
        "deepseek": "deepseek-chat",
        "openai": "gpt-4o-mini",
        "glm-5.2": "glm-4-plus",
        "qwen": "qwen-plus",
        "kimi": "moonshot-v1-8k",
        "minimax": "abab6.5s-chat",
    }

    def __init__(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider
        self.model = model or self._DEFAULT_MODELS.get(provider, provider)
        self.api_key = api_key

    async def chat_async(self, prompt: str, **kwargs: Any) -> str:
        if self.api_key is None:
            self.api_key = self._resolve_api_key()
        if self.provider in self._OPENAI_COMPATIBLE:
            return await self._chat_openai_compatible(prompt, **kwargs)
        elif self.provider == "gemini":
            return await self._chat_gemini(prompt, **kwargs)
        else:
            logger.warning(f"Provider {self.provider} not natively supported; falling back to OpenAI-compatible.")
            return await self._chat_openai_compatible(prompt, **kwargs)

    def chat(self, prompt: str, **kwargs: Any) -> str:
        import requests
        api_key = self.api_key or self._resolve_api_key()
        base_url = self._BASE_URLS.get(self.provider, "https://api.openai.com/v1")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        try:
            resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"ModelClient.chat() failed for {self.provider}: {e}")
            return json.dumps({"error": str(e)})

    def _resolve_api_key(self) -> str:
        env_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "glm-5.2": "GLM_API_KEY",
            "qwen": "QWEN_API_KEY",
            "kimi": "KIMI_API_KEY",
            "minimax": "MINIMAX_API_KEY",
        }
        key_name = env_map.get(self.provider, f"{self.provider.upper().replace('-','_').replace('.','_')}_API_KEY")
        key = os.getenv(key_name, "")
        if not key:
            logger.warning(f"ModelClient: no API key found for {self.provider} ({key_name})")
        return key

    async def _chat_openai_compatible(self, prompt: str, **kwargs: Any) -> str:
        import aiohttp
        api_key = self.api_key or self._resolve_api_key()
        base_url = self._BASE_URLS.get(self.provider, "https://api.openai.com/v1")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"ModelClient.chat_async() failed for {self.provider}: {e}")
            return json.dumps({"error": str(e)})

    async def _chat_gemini(self, prompt: str, **kwargs: Any) -> str:
        try:
            import google.genai as genai
            api_key = self.api_key or self._resolve_api_key()
            client = genai.Client(api_key=api_key)
            response = await client.aio.models.generate_content(model=self.model, contents=prompt)
            return response.text
        except Exception as e:
            logger.error(f"ModelClient Gemini call failed: {e}")
            return json.dumps({"error": str(e)})
