# src/fzq_ai/api/multi.py
# V23 — Multi-Agent API Entry
# Author: Nick

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator

router = APIRouter()
orchestrator = UnifiedOrchestrator()


class MultiTask(BaseModel):
    agent: str
    intent: str
    payload: Any


class MultiRequest(BaseModel):
    tasks: List[MultiTask]


@router.post("/multi")
def run_multi_agent(req: MultiRequest):
    tasks = [t.dict() for t in req.tasks]
    result = orchestrator.run_multi(tasks)
    return {"tasks": tasks, "result": result}
