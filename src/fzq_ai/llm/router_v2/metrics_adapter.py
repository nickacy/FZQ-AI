# src/fzq_ai/llm/router_v2/metrics_adapter.py

from fzq_ai.metrics.metrics_v2 import metrics_v2
from fzq_ai.metrics.cost_model import CostModel

class MetricsAdapter:
    """
    根据历史成功率、延迟、错误率、成本对候选模型排序。
    """

    def __init__(self):
        self.cost_model = CostModel()

    def rank(self, providers):
        scored = []

        for p in providers:
            stats = metrics_v2.get_stats(p) or {}

            success_rate = stats.get("success_rate", 0.8)
            error_rate = stats.get("error_rate", 0.0)
            latency = stats.get("avg_latency_ms", 1000)
            tokens = stats.get("avg_tokens", 1000)

            cost_score = 1 / (self.cost_model.cost(p, tokens) + 1)

            score = (
                success_rate * 0.6 +
                (1 - error_rate) * 0.2 +
                (1 / (latency + 1)) * 0.1 +
                cost_score * 0.1
            )

            scored.append((p, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]
