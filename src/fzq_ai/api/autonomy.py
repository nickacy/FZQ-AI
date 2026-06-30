# src/fzq_ai/api/autonomy.py
# V23 — Autonomous Agent API Entry
# Author: Nick

from fastapi import APIRouter
from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator

router = APIRouter()
orchestrator = UnifiedOrchestrator()


@router.post("/autonomy")
def run_autonomy():
    status = orchestrator.run_autonomy_v22()
    return {"status": status}
