# src/fzq_ai/monitor/metrics.py
# v13 MetricsRecorder – high-level metrics API using metrics_writer

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Optional

from fzq_ai.metrics.metrics_writer import metrics_writer


class MetricsRecorder:
    """
    v13 MetricsRecorder

    - 提供统一的 record() 接口（pipeline / orchestrator 等）
    - 提供 record_provider_call() 接口（LLM provider 调用）
    - 提供 get_provider_stats() 接口（给 model_selector 用）
    """

    def __init__(self) -> None:
        # 内存中的简单聚合，用于 get_provider_stats()
        self._provider_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "total_latency_ms": 0.0,
                "error_count": 0,
            }
        )

    # -------- 通用 metrics 记录（pipeline / orchestrator 等） --------

    def record(self, name: str, duration_ms: float, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        记录一次通用 metrics 事件，并写入 JSONL。
        """
        metrics_writer.append(name=name, duration_ms=duration_ms, extra=extra)

    # -------- Provider 级 metrics 记录 --------

    def record_provider_call(
        self,
        provider: str,
        model: str,
        duration_ms: float,
        success: bool = True,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        记录一次 LLM Provider 调用：
        - 用于后续 get_provider_stats()
        - 同时写入 JSONL
        """
        key = f"{provider}:{model}"
        stat = self._provider_stats[key]
        stat["count"] += 1
        stat["total_latency_ms"] += float(duration_ms)
        if not success:
            stat["error_count"] += 1

        merged_extra = {
            "provider": provider,
            "model": model,
            "success": success,
        }
        if extra:
            merged_extra.update(extra)

        metrics_writer.append(
            name="provider_call",
            duration_ms=duration_ms,
            extra=merged_extra,
        )

    # -------- 提供给 model_selector 的接口 --------

    def get_provider_stats(self, provider_model_key: str) -> Dict[str, Any]:
        """
        返回某个 provider+model 的统计信息：
        - count
        - avg_latency_ms
        - error_rate
        若没有记录，则返回默认值。
        """
        stat = self._provider_stats.get(
            provider_model_key,
            {
                "count": 0,
                "total_latency_ms": 0.0,
                "error_count": 0,
            },
        )
        count = stat["count"]
        total_latency = stat["total_latency_ms"]
        error_count = stat["error_count"]

        avg_latency = total_latency / count if count > 0 else 0.0
        error_rate = error_count / count if count > 0 else 0.0

        return {
            "count": count,
            "avg_latency_ms": avg_latency,
            "error_rate": error_rate,
        }


metrics = MetricsRecorder()
