# src/fzq_ai/api/v24_formatter.py
# V24-Final — Unified API output contract for all endpoints
from __future__ import annotations
import uuid
from typing import Any, Dict, Optional, List


def v24_success(
    *,
    intent: Optional[Dict[str, Any]] = None,
    route: Optional[Dict[str, Any]] = None,
    pipeline: Optional[str] = None,
    model: Optional[str] = None,
    agent: Optional[str] = None,
    output: Any = None,
    timeline: Optional[List[Dict[str, Any]]] = None,
    state_machine: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
    ui_schema: Optional[Dict[str, Any]] = None,
    fallback_used: Optional[str] = None,
) -> Dict[str, Any]:
    """Unified V24 success response — all API endpoints MUST use this."""
    return {
        "execution": {
            "intent": intent or {},
            "route": route or {},
            "pipeline": pipeline or "unknown",
            "model": model or "unknown",
            "agent": agent or "unknown",
            "timeline": timeline or [],
            "state_machine": state_machine or {"current": "FINALIZE", "history": []},
            "trace_id": trace_id or str(uuid.uuid4()),
            "fallback_used": fallback_used,
        },
        "ui_schema": ui_schema or {},
        "output": output,
    }


def v24_error(
    *,
    error: str,
    code: str = "ERROR",
    pipeline: Optional[str] = None,
    agent: Optional[str] = None,
    trace_id: Optional[str] = None,
    fallback_used: Optional[str] = None,
    clarification_needed: bool = False,
) -> Dict[str, Any]:
    """Unified V24 error response."""
    return {
        "execution": {
            "intent": {},
            "route": {},
            "pipeline": pipeline or "unknown",
            "model": "unknown",
            "agent": agent or "unknown",
            "timeline": [],
            "state_machine": {"current": "FINALIZE", "history": []},
            "trace_id": trace_id or str(uuid.uuid4()),
            "fallback_used": fallback_used,
            "error": {"code": code, "message": error},
            "clarification_needed": clarification_needed,
        },
        "ui_schema": {},
        "output": None,
    }
