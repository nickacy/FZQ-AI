# -*- coding: utf-8 -*-
"""FZQ-AI Chinese Intelligence API (V24 — unified contract)"""
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from fzq_ai.core.intent_engine import classify, classify_async
from fzq_ai.core.task_router import TaskRouter

router = APIRouter(prefix="/api/zh", tags=["Chinese Intelligence"])
task_router = TaskRouter()


class ZhIntelPayload(BaseModel):
    text: str
    extra: dict | None = None


# ── V24 contract formatter ──────────────────────────────────

def wrap_response(route_result: Any) -> dict:
    """Map RouteResult → V24 execution + ui_schema."""
    import uuid as _uuid
    execution = {
        "intent": {},
        "route": {"task_type": route_result.task_type},
        "pipeline": route_result.pipeline_used or "unknown",
        "model": route_result.model_used or "unknown",
        "agent": route_result.agent_used or "unknown",
        "timeline": [],
        "state_machine": {"current": "FINALIZE", "history": []},
        "trace_id": str(_uuid.uuid4()),
        "fallback_used": route_result.fallback_used,
        "success": route_result.success,
    }
    if route_result.error:
        execution["error"] = {"code": "PIPELINE_ERROR", "message": route_result.error}
    return {
        "execution": execution,
        "ui_schema": {},
        "output": route_result.output if route_result.success else None,
    }


# ── Unified task runner ─────────────────────────────────────

async def _run_task(payload: ZhIntelPayload, expected_task: str) -> dict:
    """classify → route → pipeline with guard."""
    try:
        intent = await classify_async(payload.text)
        if intent.task_type == "clarification_required":
            return {
                "execution": {
                    "intent": {}, "route": {}, "pipeline": "unknown",
                    "model": "unknown", "agent": "unknown",
                    "timeline": [], "state_machine": {"current": "FINALIZE", "history": []},
                    "trace_id": "clarify",
                    "error": {"code": "CLARIFY", "message": intent.reason},
                    "clarification_needed": True, "fallback_used": None, "success": False,
                },
                "ui_schema": {}, "output": None,
            }
        intent.task_type = expected_task
        result = await task_router.route(intent, payload.text)
        return wrap_response(result)
    except Exception as e:
        import uuid as _uuid
        return {
            "execution": {
                "intent": {}, "route": {}, "pipeline": expected_task,
                "model": "unknown", "agent": "unknown",
                "timeline": [], "state_machine": {"current": "FINALIZE", "history": []},
                "trace_id": str(_uuid.uuid4()),
                "error": {"code": "CHAIN_FAIL", "message": str(e)},
                "fallback_used": "api_guard", "success": False, "clarification_needed": False,
            },
            "ui_schema": {}, "output": None,
        }


# ── Endpoints ───────────────────────────────────────────────

@router.post("/policy_brief")
async def api_zh_policy_brief(payload: ZhIntelPayload) -> dict:
    return await _run_task(payload, "zh_policy_brief")


@router.post("/risk_scan")
async def api_zh_risk_scan(payload: ZhIntelPayload) -> dict:
    return await _run_task(payload, "zh_risk_scan")


@router.post("/opinion_landscape")
async def api_zh_opinion_landscape(payload: ZhIntelPayload) -> dict:
    return await _run_task(payload, "zh_opinion_landscape")


@router.post("/multisource_merge")
async def api_zh_multisource_merge(payload: ZhIntelPayload) -> dict:
    return await _run_task(payload, "zh_multisource_merge")
