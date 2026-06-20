"""
Metrics Schemas
系统指标数据结构（中英文双语）
----------------------------------------------------
These Pydantic models define the structure of system-level
and pipeline-level metrics for FZQ-AI.
这些 Pydantic 模型定义了 FZQ-AI 的系统级与 Pipeline 级指标结构。
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


# -------------------------------
# Provider-level metrics
# -------------------------------
class ProviderStats(BaseModel):
    """
    Metrics for each model provider.
    每个模型提供商的性能指标。
    """
    provider_name: str
    total_calls: int
    success_rate: float
    error_rate: float
    avg_latency_ms: float
    last_used_at: Optional[datetime]


# -------------------------------
# Pipeline-level metrics
# -------------------------------
class PipelineStats(BaseModel):
    """
    Metrics for each pipeline.
    每个 Pipeline 的性能指标。
    """
    pipeline_name: str
    call_count: int
    avg_latency_ms: float
    error_rate: float
    last_called_at: Optional[datetime]


# -------------------------------
# System-level metrics
# -------------------------------
class SystemMetrics(BaseModel):
    """
    Global system metrics.
    系统级指标。
    """
    uptime_seconds: float
    total_requests: int
    total_errors: int
    avg_latency_ms: float
    active_providers: List[str]
    provider_stats: Dict[str, ProviderStats]
    pipeline_stats: Dict[str, PipelineStats]
