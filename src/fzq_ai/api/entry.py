# src/fzq_ai/api/entry.py
# V23 — Single-Agent API Entry
# Author: Nick

from fastapi import APIRouter
from pydantic import BaseModel
from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator

router = APIRouter()
orchestrator = UnifiedOrchestrator()


class EntryRequest(BaseModel):
    task: str
    ctx: dict = {}


@router.post("/entry")
def run_single_agent(req: EntryRequest):
    result = orchestrator.run(req.task, req.ctx)
    if hasattr(result, 'to_dict'):
        return result.to_dict()
    return {"task": req.task, "result": result}
