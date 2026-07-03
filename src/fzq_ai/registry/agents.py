# src/fzq_ai/registry/agents.py
# V24-Final — Unified Agent Registry
# Migrated from agents/registry.py
from __future__ import annotations
from typing import Any, Dict, Type

# ── Agent imports ──
from fzq_ai.agents.report_agent import ReportAgent
from fzq_ai.agents.watchlist_agent import WatchlistAgent
from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.agents.tasks.policy_brief_agent import PolicyBriefAgent
from fzq_ai.agents.tasks.risk_scan_agent import RiskScanAgent
from fzq_ai.agents.tasks.opinion_landscape_agent import OpinionLandscapeAgent
from fzq_ai.agents.tasks.multisource_merge_agent import MultisourceMergeAgent

try:
    from fzq_ai.agents.autonomy_agent_v22 import AutonomyAgentV22
except Exception:
    AutonomyAgentV22 = None


# ── Registry ──
AGENT_REGISTRY: Dict[str, Type[Any]] = {}


def register_agent(name: str, cls: Type[Any], **meta) -> None:
    """Register an agent class with optional metadata."""
    AGENT_REGISTRY[name] = cls


def get_agent(name: str) -> Any:
    """Instantiate and return an agent by name.

    Returns None if the agent is not registered (caller can decide how to
    handle missing agents — e.g. fallback or graceful skip).
    """
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        return None
    return cls()


# ── Auto-register all agents ──
register_agent("report", ReportAgent)
register_agent("watchlist", WatchlistAgent)
register_agent("news_center", NewsCenterAgent)
register_agent("zh_policy_brief", PolicyBriefAgent)
register_agent("zh_risk_scan", RiskScanAgent)
register_agent("zh_opinion_landscape", OpinionLandscapeAgent)
register_agent("zh_multisource_merge", MultisourceMergeAgent)
if AutonomyAgentV22:
    register_agent("autonomy_v22", AutonomyAgentV22)


# ── Backward-compatible global instance ──
class AgentRegistry:
    """OOP-style registry for use as global singleton."""
    def __init__(self):
        self._agents: Dict[str, Any] = dict(AGENT_REGISTRY)

    def register(self, name: str, agent_cls):
        self._agents[name] = agent_cls
        AGENT_REGISTRY[name] = agent_cls

    def get(self, name: str):
        cls = self._agents.get(name)
        if cls:
            return cls()
        return None

    def all(self):
        return dict(self._agents)


global_registry = AgentRegistry()
