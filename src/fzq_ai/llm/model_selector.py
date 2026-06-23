# fzq_ai/llm/model_selector.py
# FZQ‑AI v13 ModelSelector（智能模型选择器）

import time
from typing import List, Dict, Optional

from fzq_ai.monitor.metrics import metrics
from fzq_ai.config.global_settings import settings


class ModelSelectorV3:
    """
    v13 智能模型选择器（基于 metrics 的自适应选择）
    - 自动降级（成本高 → 换便宜模型）
    - 自动升级（性能差 → 换更快模型）
    - 基于最近 N 次调用的稳定性、错误率、耗时
    """

    def __init__(self):
        self.priority = settings.model_priority.fallback
        self.primary = settings.model_priority.default_primary

    # ---------------------------------------------------------
    # 主入口：选择最优模型
    # ---------------------------------------------------------
    def select(self, task_type: str) -> str:
        candidates = [self.primary] + self.priority

        scored = []
        for model in candidates:
            score = self._score_model(model)
            scored.append((model, score))

        # 分数越高越好
        scored.sort(key=lambda x: x[1], reverse=True)

        best_model = scored[0][0]
        return best_model

    # ---------------------------------------------------------
    # 计算模型得分（核心智能逻辑）
    # ---------------------------------------------------------
    def _score_model(self, model: str) -> float:
        """
        综合评分：
        - 成本（越低越好）
        - 耗时（越低越好）
        - 错误率（越低越好）
        - 最近调用次数（越多越稳定）
        """

        stats = metrics.get_provider_stats(model)

        if not stats:
            # 没有数据 → 使用默认优先级
            return 0.5

        cost_weight = 0.3
        latency_weight = 0.3
        error_weight = 0.3
        usage_weight = 0.1

        # 成本（越低越好）
        cost_score = 1 / (stats["avg_cost"] + 1e-6)

        # 耗时（越低越好）
        latency_score = 1 / (stats["avg_latency_ms"] + 1e-6)

        # 错误率（越低越好）
        error_score = 1 - stats["error_rate"]

        # 使用次数（越多越稳定）
        usage_score = stats["count"] / (stats["count"] + 10)

        final_score = (
            cost_score * cost_weight +
            latency_score * latency_weight +
            error_score * error_weight +
            usage_score * usage_weight
        )

        return final_score


# 单例
model_selector = ModelSelectorV3()
