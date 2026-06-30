# src/fzq_ai/agents/registry.py
# V23 — Unified Agent Registry (v4.5 + V21 + V22 Compatible)
# Author: Nick
# Version: V23.1.0

from __future__ import annotations
from typing import Any, Dict, Type

# 旧 v4.5 agents
from fzq_ai.agents.report_agent import ReportAgent
from fzq_ai.agents.watchlist_agent import WatchlistAgent

# V21 agents
from fzq_ai.agents.tasks.policy_brief_agent import PolicyBriefAgent
from fzq_ai.agents.tasks.risk_scan_agent import RiskScanAgent
from fzq_ai.agents.tasks.opinion_landscape_agent import OpinionLandscapeAgent
from fzq_ai.agents.tasks.multisource_merge_agent import MultisourceMergeAgent

# V22 agents
try:
    from fzq_ai.agents.autonomy_agent_v22 import AutonomyAgentV22
except Exception:
    AutonomyAgentV22 = None


AGENT_REGISTRY: Dict[str, Type[Any]] = {}


def register_agent(name: str, cls: Type[Any]):
    AGENT_REGISTRY[name] = cls


def get_agent(name: str) -> Any:
    cls = AGENT_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Agent '{name}' not found in registry.")
    return cls()


# 注册所有智能体（类，而不是实例）
register_agent("report", ReportAgent)
register_agent("watchlist", WatchlistAgent)

register_agent("zh_policy_brief", PolicyBriefAgent)
register_agent("zh_risk_scan", RiskScanAgent)
register_agent("zh_opinion_landscape", OpinionLandscapeAgent)
register_agent("zh_multisource_merge", MultisourceMergeAgent)

if AutonomyAgentV22:
    register_agent("autonomy_v22", AutonomyAgentV22)
