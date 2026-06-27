"""FZQ-AI Core: intent engine, task router, LLM executor, config."""


def __getattr__(name: str):
    """Lazy imports to avoid circular dependency."""
    if name in ("classify", "IntentResult"):
        from fzq_ai.core.intent_engine import classify, IntentResult
        return locals()[name]
    if name in ("TaskRouter", "RouteResult"):
        from fzq_ai.core.task_router import TaskRouter, RouteResult
        return locals()[name]
    raise AttributeError(f"module 'fzq_ai.core' has no attribute {name}")


__all__ = ["classify", "IntentResult", "TaskRouter", "RouteResult"]
