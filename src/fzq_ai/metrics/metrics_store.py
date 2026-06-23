"""
MetricsStore - In-memory metrics aggregation for the API layer.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict


class MetricsStore:
    """Simple in-memory metrics store for the API dashboard."""

    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.total_requests = 0
        self.total_errors = 0
        self.total_latency_ms = 0.0
        self.pipeline_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"call_count": 0, "avg_latency_ms": 0.0, "error_rate": 0.0, "last_called_at": ""}
        )
        self.provider_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"total_calls": 0, "success_rate": 1.0, "avg_latency_ms": 0.0, "last_used_at": ""}
        )

    def export_system_metrics(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        uptime = (now - self.start_time).total_seconds()
        return {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "avg_latency_ms": self.total_latency_ms / max(self.total_requests, 1),
            "provider_stats": dict(self.provider_stats),
            "pipeline_stats": dict(self.pipeline_stats),
        }


metrics_store = MetricsStore()
