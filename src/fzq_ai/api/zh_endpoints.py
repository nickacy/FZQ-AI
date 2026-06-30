# -*- coding: utf-8 -*-
"""
FZQ-AI Chinese Intelligence API (V19-Final)
中文情报任务 API（V19 最终版）

本模块通过 TaskRouter 执行四大中文情报任务：
- zh_policy_brief
- zh_risk_scan
- zh_opinion_landscape
- zh_multisource_merge

所有端点返回统一结构化响应格式。
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fzq_ai.core.intent_engine import classify
from fzq_ai.core.task_router import TaskRouter

router = APIRouter(prefix="/api/zh", tags=["Chinese Intelligence"])
task_router = TaskRouter()


# ============================================================
# 1. 请求体 Schema
# ============================================================

class ZhIntelPayload(BaseModel):
    text: str
    extra: dict | None = None


# ============================================================
# 2. 统一响应包装
# ============================================================

def wrap_response(route_result):
    """统一 API 响应格式"""
    if not route_result.success:
        return {
            "success": False,
            "task_type": route_result.task_type,
            "pipeline": route_result.pipeline_used,
            "agent": route_result.agent_used,
            "model": route_result.model_used,
            "fallback_used": route_result.fallback_used,
            "error": route_result.error,
            "output": None,
        }

    return {
        "success": True,
        "task_type": route_result.task_type,
        "pipeline": route_result.pipeline_used,
        "agent": route_result.agent_used,
        "model": route_result.model_used,
        "fallback_used": route_result.fallback_used,
        "error": None,
        "output": route_result.output,
    }


# ============================================================
# 3. 四大中文情报任务端点
# ============================================================

@router.post("/policy_brief")
async def api_zh_policy_brief(payload: ZhIntelPayload):
    intent = classify(payload.text)
    intent.task_type = "zh_policy_brief"
    result = await task_router.route(intent, payload.text)
    return wrap_response(result)


@router.post("/risk_scan")
async def api_zh_risk_scan(payload: ZhIntelPayload):
    intent = classify(payload.text)
    intent.task_type = "zh_risk_scan"
    result = await task_router.route(intent, payload.text)
    return wrap_response(result)


@router.post("/opinion_landscape")
async def api_zh_opinion_landscape(payload: ZhIntelPayload):
    intent = classify(payload.text)
    intent.task_type = "zh_opinion_landscape"
    result = await task_router.route(intent, payload.text)
    return wrap_response(result)


@router.post("/multisource_merge")
async def api_zh_multisource_merge(payload: ZhIntelPayload):
    intent = classify(payload.text)
    intent.task_type = "zh_multisource_merge"
    result = await task_router.route(intent, payload.text)
    return wrap_response(result)
