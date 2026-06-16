# fzq_ai/llm/llm_router.py

import asyncio
from typing import Any, Dict

from fzq_ai.llm.providers.openai_client import OpenAIClient
from fzq_ai.llm.providers.deepseek_client import DeepSeekClient
from fzq_ai.llm.providers.minimax_client import MiniMaxClient


class LLMRouter:
    """
    LLM 路由器（增强版）
    - 保留全部旧功能
    - 新增 JSON mode 支持（用于结构化任务）
    """

    def __init__(self):
        self.providers = {
            "openai": OpenAIClient(),
            "deepseek": DeepSeekClient(),
            "minimax": MiniMaxClient(),
        }

        # 任务 → 默认 provider
        self.task_map = {
            "news_intel": "openai",
            "event_extraction": "openai",
            "risk_intel": "deepseek",
            "sentiment": "openai",
        }

    def _select_provider(self, task: str):
        name = self.task_map.get(task, "openai")
        return self.providers[name]

    async def route(self, task: str, prompt: str) -> str:
        provider = self._select_provider(task)

        # ⭐ 新增：结构化任务启用 JSON mode
        if task in {"news_intel", "event_extraction"}:
            return await provider.run(
                prompt,
                response_format={"type": "json_object"},
            )

        # ⭐ 旧逻辑保持不变
        return await provider.run(prompt)
