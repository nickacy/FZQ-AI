# src/fzq_ai/api/entry.py
# V23 — Single-Agent API Entry
# Author: Nick

from fastapi import APIRouter
from pydantic import BaseModel
from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator
from typing import Dict, Any

router = APIRouter()
orchestrator = UnifiedOrchestrator()


class EntryRequest(BaseModel):
    task: str
    ctx: dict = {}


@router.post("/entry")
def run_single_agent(req: EntryRequest) -> dict:
    result = orchestrator.run(req.task, req.ctx)
    if hasattr(result, 'to_dict'):
        d = result.to_dict()
        # Wrap in V24 contract
        return {
            "execution": {
                "intent": {},
                "route": {"task_type": req.task},
                "pipeline": d.get("data", {}).get("pipeline", "unknown"),
                "model": d.get("data", {}).get("model", "unknown"),
                "agent": d.get("data", {}).get("agent", "unknown"),
                "timeline": d.get("timeline", []),
                "state_machine": {"current": "FINALIZE", "history": []},
                "trace_id": d.get("trace_id", ""),
                "success": d.get("status") == "ok",
            },
            "ui_schema": d.get("ui_schema", {}),
            "output": d.get("data"),
        }
    return {"execution": {"success": False, "error": {"code": "UNKNOWN", "message": "No result"}}, "ui_schema": {}, "output": None}
