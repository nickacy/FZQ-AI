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
        """
        返回 provider 实例（与 Router v1 一致）
        """
        client = settings.get_client(provider_name)
        model = settings.get_model(provider_name)

        from fzq_ai.llm.router import PROVIDER_MAP
        provider_class = PROVIDER_MAP[provider_name]
        return provider_class(client=client, model=model)
