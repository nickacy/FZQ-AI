"""FZQ-AI Core: intent engine, task router, LLM executor."""
from fzq_ai.core.intent_engine import classify, IntentResult
from fzq_ai.core.task_router import TaskRouter, RouteResult

__all__ = ["classify", "IntentResult", "TaskRouter", "RouteResult"]
