# src/fzq_ai/metrics/metrics_v2.py

from __future__ import annotations
from typing import Dict, Any
from collections import defaultdict
import time


class MetricsV2:
    """
    Metrics v2
    - 记录模型调用表现
    - 聚合历史指标
    - 提供 Router v2 使用的评分
    """

    def __init__(self):
        self.data = defaultdict(list)

    def record(self, provider: str, success: bool, latency_ms: int, tokens: int, error: str = None):
        self.data[provider].append({
            "success": success,
            "latency_ms": latency_ms,
            "tokens": tokens,
            "error": error,
            "timestamp": time.time(),
        })

    def get_stats(self, provider: str) -> Dict[str, Any]:
        records = self.data.get(provider, [])
        if not records:
            return {}

        success_rate = sum(1 for r in records if r["success"]) / len(records)
        error_rate = sum(1 for r in records if r["error"]) / len(records)
        avg_latency = sum(r["latency_ms"] for r in records) / len(records)
        avg_tokens = sum(r["tokens"] for r in records) / len(records)

        return {
            "success_rate": success_rate,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency,
            "avg_tokens": avg_tokens,
        }


metrics_v2 = MetricsV2()
