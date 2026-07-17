# src/fzq_ai/api/entry.py
# V23 — Single-Agent API Entry
# Author: Nick

from fastapi import APIRouter
from pydantic import BaseModel
from fzq_ai.orchestrator.unified_orchestrator_v24 import UnifiedOrchestratorV24
from typing import Dict, Any

router = APIRouter()
orchestrator = UnifiedOrchestratorV24()


class EntryRequest(BaseModel):
    task: str
    ctx: dict = {}


@router.post("/entry")
async def run_single_agent(req: EntryRequest) -> dict:
    # UnifiedOrchestratorV24.run() is async and returns a plain dict:
    # {success, task_type, pipeline, agent, model, fallback_used,
    #  output, error, recovery_trace}
    result = await orchestrator.run(req.task, req.ctx)
    if result.get("success"):
        # Wrap in V24 contract
        return {
            "execution": {
                "intent": {},
                "route": {"task_type": req.task},
                "pipeline": result.get("pipeline") or "unknown",
                "model": result.get("model") or "unknown",
                "agent": result.get("agent") or "unknown",
                "timeline": result.get("recovery_trace") or [],
                "state_machine": {"current": "FINALIZE", "history": []},
                "trace_id": "",
                "success": True,
            },
            "ui_schema": {},
            "output": result.get("output"),
        }
    return {
        "execution": {
            "success": False,
            "error": {
                "code": "EXECUTION_ERROR",
                "message": result.get("error") or "No result",
            },
        },
        "ui_schema": {},
        "output": None,
    }
