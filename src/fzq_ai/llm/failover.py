# src/fzq_ai/llm/failover.py
# V24-Final — LLM Failover (automatic model degradation)
"""
Three-tier failover for LLM calls:

  Tier 1: Same-family fallback (deepseek-chat → deepseek-reasoner)
  Tier 2: Cross-family fallback (DeepSeek → GLM → Qwen → OpenAI)
  Tier 3: Ultimate fallback (gpt-4-turbo / deepseek-chat)

All failover events are recorded via: tracing, monitoring, structlog.
"""
from __future__ import annotations
from typing import Any, Dict, List

# ── Failover map ──────────────────────────────────────────────

_FAILOVER: Dict[str, List[str]] = {
    # DeepSeek family
    "deepseek-chat":    ["deepseek-reasoner", "glm-4-flash", "qwen-max", "gpt-4o-mini"],
    "deepseek-reasoner":["deepseek-chat", "glm-4-flash", "qwen-max", "gpt-4o-mini"],

    # GLM family
    "glm-4":            ["glm-4-flash", "deepseek-chat", "qwen-max", "gpt-4o-mini"],
    "glm-4-flash":      ["glm-4", "deepseek-chat", "qwen-max", "gpt-4o-mini"],

    # Qwen family
    "qwen-max":         ["deepseek-chat", "glm-4-flash", "gpt-4o-mini"],

    # OpenAI family
    "gpt-4o":           ["gpt-4o-mini", "deepseek-chat", "glm-4-flash"],
    "gpt-4o-mini":      ["gpt-4o", "deepseek-chat", "glm-4-flash"],

    # Gemini
    "gemini-2.0-flash": ["deepseek-chat", "glm-4-flash", "gpt-4o-mini"],

    # Default
    "default":          ["deepseek-chat", "glm-4-flash", "qwen-max", "gpt-4o-mini"],
}


# ── Get failover chain ───────────────────────────────────────

def get_failover_chain(model: str) -> List[str]:
    """Return ordered list of fallback models for a given model."""
    return _FAILOVER.get(model, _FAILOVER["default"])


def format_failover_path(original: str, tried: List[str], succeeded: str) -> str:
    """Human-readable failover path: 'modelA -> modelB -> modelC'."""
    path_parts = [original] + tried[: tried.index(succeeded) + 1 if succeeded in tried else len(tried)]
    return " → ".join(path_parts)
