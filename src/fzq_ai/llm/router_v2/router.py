# src/fzq_ai/llm/router_v2/router.py

from __future__ import annotations
from typing import Dict, Any

from fzq_ai.llm.router_v2.selectors import TaskSelector
from fzq_ai.llm.router_v2.metrics_adapter import MetricsAdapter
from fzq_ai.config.global_settings import settings


class RouterV2:
    """
    Task-Aware Router v2
    - 根据任务类型选择模型
    - 根据输入长度选择模型
    - 根据结构化程度选择模型
    - 根据历史成功率动态排序
    """

    def __init__(self):
        self.task_selector = TaskSelector()
        self.metrics = MetricsAdapter()

    def select(self, task: Dict[str, Any]) -> str:
        """
        返回最优 provider 名称。
        """
        candidates = self.task_selector.select(task)
        ranked = self.metrics.rank(candidates)
        return ranked[0]

    def get_provider(self, provider_name: str):
        """Return a unified ModelClient for the given provider name.

        Settings.PROVIDER_MAP is only a declaration table (string names);
        the actual unified client lives in fzq_ai.clients.model_client.ModelClient.
        """
        from fzq_ai.clients.model_client import ModelClient

        if provider_name not in settings.PROVIDER_MAP:
            raise ValueError(
                f"Unknown provider '{provider_name}'. "
                f"Available: {list(settings.PROVIDER_MAP.keys())}"
            )

        model = settings.get_model(provider_name)
        return ModelClient(provider=provider_name, model=model)
