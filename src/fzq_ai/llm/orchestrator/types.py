# src/fzq_ai/llm/orchestrator/types.py

from typing import TypedDict

class OrchestratorResult(TypedDict):
    output: str
    audit: dict
    model_used: str
