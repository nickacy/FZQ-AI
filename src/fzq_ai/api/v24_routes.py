# app/api_v24.py
# V24 Frontend-facing API Adapter
# 翻译 V23 内部结构为前端要求书规定的标准契约

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from fzq_ai.api.entry_service_v24 import EntryServiceV24
from fzq_ai.orchestrator.blackboard import Blackboard
from fzq_ai.schemas.route import RouteResult

router = APIRouter(prefix="/api/v1", tags=["V24 Frontend API"])
service = EntryServiceV24()


def _to_route_result(r24) -> RouteResult:
    """Wrap EntryServiceV24's `handle_*` RouteResult in a V24 RouteResult for
    `translate_to_v24_contract` (which expects the unified `RouteResult` shape)."""
    return RouteResult.ok(
        data=r24.data,
        ui_layout=r24.ui_layout,
        debug_info=r24.debug_info,
        timeline=r24.timeline,
        ui_schema=r24.ui_schema,
        warnings=r24.warnings,
        trace=r24.trace,
    )

# --- 严格对齐前端要求书的请求体 ---
class V24EntryRequest(BaseModel):
    text: str = Field(..., min_length=1, description="用户输入文本")
    language: str = Field("zh", pattern="^(zh|en)$")
    session_id: Optional[str] = Field(None, max_length=64)
    agent: Optional[str] = Field(None, description="指定智能体名称")

class V24MultiRequest(BaseModel):
    text: str = Field(...)
    language: str = Field("zh")
    tasks: List[Dict[str, Any]] = Field(..., description="多智能体任务列表")

# --- 核心翻译函数 ---
def translate_to_v24_contract(v23_result) -> Dict[str, Any]:
    """将 V23 的 RouteResult 翻译为 V24 前端契约"""
    # `debug_info` may be a dict, a list (V24 puts trace there), or None.
    # Normalize to dict for safe .get() access.
    raw = v23_result.debug_info
    if isinstance(raw, dict):
        debug_info = raw
    elif isinstance(raw, list):
        debug_info = {"trace": raw}
    else:
        debug_info = {}
    blackboard_snapshot = debug_info.get("blackboard_snapshot", {})
    internal_data = v23_result.data or {}

    return {
        "execution": {
            "intent": internal_data.get("intent", {}),
            "route": internal_data.get("route", {}),
            "pipeline": internal_data.get("pipeline", {}),
            "model": internal_data.get("model", {}),
            "agent": internal_data.get("agent", {}),
            # 从 Blackboard 提取 V24 要求的状态机和时序数据
            "state_machine": {
                "current": blackboard_snapshot.get("autonomy.phase", "FINALIZE"),
                "history": blackboard_snapshot.get("sys.timeline", [])
            },
            "timeline": blackboard_snapshot.get("sys.timeline", []),
            "duration_ms": internal_data.get("duration_ms", 0),
            "trace_id": v23_result.trace_id
        },
        # 统一命名为前端要求的 ui_schema
        "ui_schema": v23_result.ui_layout or {}
    }

# --- 对齐前端要求书的端点 ---
@router.post("/entry")
async def v24_entry(req: V24EntryRequest):
    # V24 入口：委托给 EntryServiceV24.handle_single
    payload = {
        "task": req.text,
        "input": req.text,
        "language": req.language,
        "agent": req.agent,
    }
    r24 = await service.handle_single(payload)
    return translate_to_v24_contract(_to_route_result(r24))


@router.post("/multi")
async def v24_multi(req: V24MultiRequest):
    payload = {
        "task": "multi",
        "input": req.text,
        "tasks": [t.dict() if hasattr(t, "dict") else t for t in req.tasks],
    }
    r24 = await service.handle_multi(payload)
    return translate_to_v24_contract(_to_route_result(r24))


@router.post("/autonomy")
async def v24_autonomy(req: V24EntryRequest):
    payload = {"task": "autonomy", "input": req.text}
    r24 = await service.handle_autonomy(payload)
    return translate_to_v24_contract(_to_route_result(r24))