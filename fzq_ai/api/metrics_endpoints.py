"""
Metrics API Endpoints
系统指标 API 路由（中英文双语）
----------------------------------------------------
Provides system-level and pipeline-level metrics for FZQ-AI.
提供 FZQ-AI 的系统级与 Pipeline 级指标。
"""

from fastapi import APIRouter
from fzq_ai.metrics.metrics_store import metrics_store

router = APIRouter(prefix="/api", tags=["Metrics"])


# -------------------------------
# 1. System Metrics
# -------------------------------
@router.get("/metrics")
async def get_system_metrics():
    """
    Get global system metrics.
    获取系统级指标。
    """
    return metrics_store.export_system_metrics()


# -------------------------------
# 2. Pipeline Metrics
# -------------------------------
@router.get("/pipelines")
async def get_pipeline_metrics():
    """
    Get metrics for all pipelines.
    获取所有 Pipeline 的指标。
    """
    return metrics_store.pipeline_stats
