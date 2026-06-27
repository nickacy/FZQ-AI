from __future__ import annotations

import asyncio
from typing import Any, Dict

from fzq_ai.llm.model_selector import ModelSelector
from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
from fzq_ai.llm.providers.qwen_provider import QwenProvider
from fzq_ai.llm.providers.kimi_provider import KimiProvider
from fzq_ai.llm.providers.openai_provider import OpenAIProvider
from fzq_ai.llm.providers.gemini_provider import GeminiProvider

from fzq_ai.config.global_settings import settings


class Router:
    """
    v13 Router
    - Selects provider by priority + capability + metrics
    - Tries providers one by one (fallback)
    """

    PROVIDER_MAP = {
        "deepseek": DeepSeekProvider,
        "qwen": QwenProvider,
        "kimi": KimiProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
    }

    def __init__(self):
        self.selector = ModelSelector(settings.model_priority)

    async def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        task_type = req.get("task_type", "chat")

        # If a specific provider is requested, try it directly
        requested_provider = req.get("provider")
        if requested_provider and requested_provider in self.PROVIDER_MAP:
            provider_order = [requested_provider]
        else:
            provider_order = self.selector.select(task_type)

        for provider_name in provider_order:
            provider_class = self.PROVIDER_MAP.get(provider_name)
            if provider_class is None:
                continue

            try:
                provider = provider_class(
                    client=settings.get_client(provider_name),
                    model=settings.get_model(provider_name),
                )
                result = await provider.run(req)
                if "error" not in result:
                    return result
            except Exception:
                continue

        return {"error": "All providers failed"}
