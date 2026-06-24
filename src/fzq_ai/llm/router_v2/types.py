# src/fzq_ai/llm/router_v2/types.py

from typing import TypedDict, List, Dict, Any


class TaskInput(TypedDict):
    task_type: str
    input: str
    metadata: Dict[str, Any]


class ProviderCandidate(TypedDict):
    provider: str
    reason: str


class RoutingResult(TypedDict):
    provider: str
    candidates: List[str]
    metrics_used: Dict[str, Any]
