from __future__ import annotations

from typing import List, Dict

from fzq_ai.llm.provider_capabilities import PROVIDER_CAPABILITIES
from fzq_ai.metrics.metrics import metrics


class ModelSelector:
    """
    v13 Model Selector
    - 根据任务类型过滤 provider
    - 根据 metrics 排序 provider（成功率优先）
    - 根据用户优先级排序 provider
    """

    def __init__(self, priority_order: List[str]):
        self.priority_order = priority_order

    def filter_by_capability(self, task_type: str) -> List[str]:
        return [
            p for p in self.priority_order
            if task_type in PROVIDER_CAPABILITIES[p]["supports"]
        ]

    def sort_by_metrics(self, providers: List[str]) -> List[str]:
        stats = metrics.get_provider_stats()

        def score(p):
            s = stats.get(p, {})
            return s.get("success_rate", 1.0)

        return sorted(providers, key=score, reverse=True)

    def select(self, task_type: str) -> List[str]:
        candidates = self.filter_by_capability(task_type)
        return self.sort_by_metrics(candidates)
