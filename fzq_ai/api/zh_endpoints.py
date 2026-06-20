"""
Chinese Intelligence API Endpoints
中文情报任务 API 端点（中英文双语）
----------------------------------------------------
This module exposes REST APIs for the four zh-intel tasks.
该模块为四大中文情报任务提供 REST API。
"""

from fastapi import APIRouter
from fzq_ai.pipelines.registry import PipelineRegistry

router = APIRouter(prefix="/api/zh", tags=["Chinese Intelligence"])


# -------------------------------
# 1. zh_policy_brief
# -------------------------------
@router.post("/policy_brief")
async def api_zh_policy_brief(payload: dict):
    """
    Run zh_policy_brief pipeline.
    执行 zh_policy_brief 中文政策解读任务。
    """
    pipeline = PipelineRegistry.get("zh_policy_brief")()
    result = await pipeline.run_async(**payload)
    return result.dict()


# -------------------------------
# 2. zh_risk_scan
# -------------------------------
@router.post("/risk_scan")
async def api_zh_risk_scan(payload: dict):
    """
    Run zh_risk_scan pipeline.
    执行 zh_risk_scan 中文风险扫描任务。
    """
    pipeline = PipelineRegistry.get("zh_risk_scan")()
    result = await pipeline.run_async(**payload)
    return result.dict()


# -------------------------------
# 3. zh_opinion_landscape
# -------------------------------
@router.post("/opinion_landscape")
async def api_zh_opinion_landscape(payload: dict):
    """
    Run zh_opinion_landscape pipeline.
    执行 zh_opinion_landscape 中文舆论版图任务。
    """
    pipeline = PipelineRegistry.get("zh_opinion_landscape")()
    result = await pipeline.run_async(**payload)
    return result.dict()


# -------------------------------
# 4. zh_multisource_merge
# -------------------------------
@router.post("/multisource_merge")
async def api_zh_multisource_merge(payload: dict):
    """
    Run zh_multisource_merge pipeline.
    执行 zh_multisource_merge 中文多源新闻合并任务。
    """
    pipeline = PipelineRegistry.get("zh_multisource_merge")()
    result = await pipeline.run_async(**payload)
    return result.dict()
