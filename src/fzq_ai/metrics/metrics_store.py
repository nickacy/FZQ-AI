"""
Metrics Store
系统指标内存存储（中英文双语）
----------------------------------------------------
A lightweight in-memory store for system, provider, and pipeline metrics.
用于存储系统级、Provider 级与 Pipeline 级指标的轻量级内存存储。
"""

import time
from typing import Dict
from datetime import datetime

from fzq_ai.schemas.metrics import SystemMetrics, ProviderStats, PipelineStats


class MetricsStore:
    """
    Global metrics store (in-memory).
    全局指标存储（内存版）。
    """

    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.total_errors = 0
        self.total_latency_ms = 0.0

        # provider_name -> ProviderStats
        self.provider_stats: Dict[str, ProviderStats] = {}

        # pipeline_name -> PipelineStats
        self.pipeline_stats: Dict[str, PipelineStats] = {}

    # -------- System-level --------
    def record_request(self, latency_ms: float, error: bool = False):
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        if error:
            self.total_errors += 1

    # -------- Provider-level --------
    def record_provider_call(self, provider_name: str, latency_ms: float, success: bool):
        stats = self.provider_stats.get(provider_name)
        if not stats:
            stats = ProviderStats(
                provider_name=provider_name,
                total_calls=0,
                success_rate=0.0,
                error_rate=0.0,
                avg_latency_ms=0.0,
                last_used_at=None,
            )

        stats.total_calls += 1
        # 更新平均延迟
        stats.avg_latency_ms = (
            (stats.avg_latency_ms * (stats.total_calls - 1) + latency_ms) / stats.total_calls
        )
        # 更新成功/失败率（简单近似）
        success_count = int(stats.success_rate * (stats.total_calls - 1)) + (1 if success else 0)
        error_count = stats.total_calls - success_count
        stats.success_rate = success_count / stats.total_calls
        stats.error_rate = error_count / stats.total_calls
        stats.last_used_at = datetime.utcnow()

        self.provider_stats[provider_name] = stats

    # -------- Pipeline-level --------
    def record_pipeline_call(self, pipeline_name: str, latency_ms: float, error: bool):
        stats = self.pipeline_stats.get(pipeline_name)
        if not stats:
            stats = PipelineStats(
                pipeline_name=pipeline_name,
                call_count=0,
                avg_latency_ms=0.0,
                error_rate=0.0,
                last_called_at=None,
            )

        stats.call_count += 1
        stats.avg_latency_ms = (
            (stats.avg_latency_ms * (stats.call_count - 1) + latency_ms) / stats.call_count
        )
        # 更新错误率（简单近似）
        error_count = int(stats.error_rate * (stats.call_count - 1)) + (1 if error else 0)
        stats.error_rate = error_count / stats.call_count
        stats.last_called_at = datetime.utcnow()

        self.pipeline_stats[pipeline_name] = stats

    # -------- Export --------
    def export_system_metrics(self) -> SystemMetrics:
        uptime_seconds = time.time() - self.start_time
        avg_latency_ms = (
            self.total_latency_ms / self.total_requests if self.total_requests > 0 else 0.0
        )
        active_providers = list(self.provider_stats.keys())

        return SystemMetrics(
            uptime_seconds=uptime_seconds,
            total_requests=self.total_requests,
            total_errors=self.total_errors,
            avg_latency_ms=avg_latency_ms,
            active_providers=active_providers,
            provider_stats=self.provider_stats,
            pipeline_stats=self.pipeline_stats,
        )


# 全局单例（简单实现）
metrics_store = MetricsStore()
