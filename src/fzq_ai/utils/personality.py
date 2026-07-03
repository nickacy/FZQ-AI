# src/fzq_ai/utils/personality.py
# V24-Final — Agent Personality Engine
"""
Personality profiles for FZQ-AI agents.

Each agent has a stable personality that influences:
  - PromptEngine: tone, style, detail level
  - LLM Router:  risk preference → model selection bias
  - MemoryEngine: detail_level → storage granularity
  - Orchestrator: execution.personality output

Profiles are versioned and extensible (v24 → v25).
"""
from __future__ import annotations
from typing import Any, Dict, Optional

# ── Default profile ──────────────────────────────────────────

DEFAULT_PERSONALITY: Dict[str, Any] = {
    "id": "v24-default",
    "tone": "professional",          # professional | casual | analytical
    "style": "structured",           # structured | narrative | bullet_points
    "risk_preference": "balanced",   # low | balanced | high
    "detail_level": "medium",        # low | medium | high
    "language": "auto",              # auto | zh | en
    "creativity": 0.5,               # 0.0–1.0
    "verbosity": 0.5,                # 0.0–1.0
}


# ── Pre-built profiles ───────────────────────────────────────

PROFILES: Dict[str, Dict[str, Any]] = {
    "deepseek-risk": {
        "id": "v24-deepseek-risk",
        "tone": "analytical",
        "style": "structured",
        "risk_preference": "low",
        "detail_level": "high",
        "language": "zh",
        "creativity": 0.3,
        "verbosity": 0.7,
    },
    "deepseek-policy": {
        "id": "v24-deepseek-policy",
        "tone": "professional",
        "style": "structured",
        "risk_preference": "balanced",
        "detail_level": "high",
        "language": "zh",
        "creativity": 0.4,
        "verbosity": 0.8,
    },
    "deepseek-news": {
        "id": "v24-deepseek-news",
        "tone": "professional",
        "style": "bullet_points",
        "risk_preference": "balanced",
        "detail_level": "medium",
        "language": "zh",
        "creativity": 0.5,
        "verbosity": 0.5,
    },
    "glm-opinion": {
        "id": "v24-glm-opinion",
        "tone": "casual",
        "style": "narrative",
        "risk_preference": "high",
        "detail_level": "medium",
        "language": "zh",
        "creativity": 0.8,
        "verbosity": 0.6,
    },
    "openai-research": {
        "id": "v24-openai-research",
        "tone": "analytical",
        "style": "structured",
        "risk_preference": "balanced",
        "detail_level": "high",
        "language": "en",
        "creativity": 0.5,
        "verbosity": 0.7,
    },
    "autonomy-agent": {
        "id": "v24-autonomy",
        "tone": "professional",
        "style": "bullet_points",
        "risk_preference": "high",
        "detail_level": "low",
        "language": "auto",
        "creativity": 0.9,
        "verbosity": 0.3,
    },
}


# ── Personality Engine ───────────────────────────────────────

class PersonalityEngine:
    """Central personality store for all agents."""

    def __init__(self):
        self._profiles: Dict[str, Dict[str, Any]] = dict(PROFILES)

    # ── Profile management ──────────────────────────────────

    def get(self, agent: str) -> Dict[str, Any]:
        """Get personality for an agent. Falls back to DEFAULT."""
        return self._profiles.get(agent, dict(DEFAULT_PERSONALITY))

    def set(self, agent: str, profile: Dict[str, Any]) -> None:
        """Set or override a personality profile."""
        self._profiles[agent] = {**DEFAULT_PERSONALITY, **profile}

    def list_agents(self) -> list:
        return list(self._profiles.keys())

    # ── Influence helpers ────────────────────────────────────

    def prompt_influence(self, agent: str) -> str:
        """Generate a prompt suffix that enforces the agent's tone/style."""
        p = self.get(agent)
        parts = [f"风格：{p['style']}", f"语气：{p['tone']}"]
        if p["detail_level"] == "high":
            parts.append("请提供详细分析。")
        elif p["detail_level"] == "low":
            parts.append("请简洁总结。")
        return "\n".join(parts)

    def router_influence(self, agent: str) -> str:
        """Get routing bias based on risk preference."""
        p = self.get(agent)
        rp = p.get("risk_preference", "balanced")
        if rp == "low":
            return "quality"     # prefer high-quality, conservative models
        elif rp == "high":
            return "cost"        # prefer cheap models (more experiments)
        return "balanced"

    def memory_influence(self, agent: str) -> str:
        """Get memory granularity based on detail_level."""
        p = self.get(agent)
        return p.get("detail_level", "medium")


# ── Global instance ──────────────────────────────────────────

global_personality = PersonalityEngine()
