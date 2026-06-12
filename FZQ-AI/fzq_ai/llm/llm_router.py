# fzq_ai/llm/llm_router.py

from __future__ import annotations
from typing import Optional, Dict, Any

from fzq_ai.llm.providers.deepseek_client import DeepSeekClient
from fzq_ai.llm.providers.openai_client import OpenAIClient
from fzq_ai.llm.providers.gemini_client import GeminiClient


class LLMRouter:
    """
    统一的 LLM 路由器：
    - 根据 model 名称自动选择 DeepSeek / OpenAI / Gemini
    - 所有 Agent 和 Pipeline 都通过它调用模型
    """

    def __init__(self):
        self.providers = {
            "deepseek": DeepSeekClient(),
            "openai": OpenAIClient(),
            "gemini": GeminiClient(),
        }

    async def run(
        self,
        prompt: str,
        model: str = "deepseek",
        **kwargs: Any,
    ) -> str:
        provider = self.providers.get(model)
        if not provider:
            raise ValueError(f"Unknown LLM provider: {model}")

        return await provider.run(prompt, **kwargs)
