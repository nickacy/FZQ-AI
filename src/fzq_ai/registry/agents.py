# src/fzq_ai/registry/agents.py
# V25 — QWEN Governance: Agent Registry with metadata + health + fallback + trace
from __future__ import annotations
from typing import Any, Dict, Type, List, Optional
import time
import logging

_logger = logging.getLogger("fzq_ai.registry.agents")

# ── Agent imports ──
from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.agents.tasks.policy_brief_agent import PolicyBriefAgent
from fzq_ai.agents.tasks.risk_scan_agent import RiskScanAgent
from fzq_ai.agents.tasks.opinion_landscape_agent import OpinionLandscapeAgent
from fzq_ai.agents.tasks.multisource_merge_agent import MultisourceMergeAgent


# ── Registry ──
AGENT_REGISTRY: Dict[str, Type[Any]] = {}
AGENT_METADATA: Dict[str, Dict[str, Any]] = {}
AGENT_HEALTH: Dict[str, Dict[str, Any]] = {}
AGENT_TRACE: List[Dict[str, Any]] = []

FALLBACK_CHAIN: Dict[str, str] = {}


def register_agent(name: str, cls: Type[Any], **meta) -> None:
    """Register an agent class with metadata."""
    AGENT_REGISTRY[name] = cls
    AGENT_METADATA[name] = {
        "registered_at": time.time(),
        **meta,
    }
    AGENT_HEALTH[name] = {"status": "ok", "last_check": time.time(), "failures": 0}
    _logger.info(f"Agent registered: {name}")


def get_agent(name: str) -> Any:
    """Instantiate and return an agent by name."""
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        return None
    try:
        instance = cls()
        AGENT_HEALTH[name]["last_check"] = time.time()
        return instance
    except Exception:
        AGENT_HEALTH[name]["failures"] += 1
        _logger.warning(f"Agent instantiation failed: {name}", exc_info=True)
        return None


def set_fallback(agent_name: str, fallback_agent: str) -> None:
    """Set a fallback chain for an agent."""
    FALLBACK_CHAIN[agent_name] = fallback_agent
    _logger.info(f"Fallback set: {agent_name} → {fallback_agent}")


def get_with_fallback(name: str) -> Any:
    """Get agent with fallback chain support."""
    agent = get_agent(name)
    if agent is not None:
        AGENT_TRACE.append({"agent": name, "timestamp": time.time(), "fallback_used": False})
        return agent
    fallback = FALLBACK_CHAIN.get(name)
    if fallback:
        _logger.warning(f"Falling back: {name} → {fallback}")
        agent = get_agent(fallback)
        AGENT_TRACE.append({"agent": fallback, "timestamp": time.time(), "fallback_used": True, "original": name})
        return agent
    return None


def agent_health_report() -> Dict[str, Any]:
    """Return health status for all registered agents."""
    return {"agents": dict(AGENT_HEALTH), "fallback_chain": dict(FALLBACK_CHAIN), "trace_count": len(AGENT_TRACE)}


# ── Auto-register all agents ──
register_agent("news_center", NewsCenterAgent, role="coordinator", priority=1)
register_agent("zh_policy_brief", PolicyBriefAgent, role="task", priority=2)
register_agent("zh_risk_scan", RiskScanAgent, role="task", priority=2)
register_agent("zh_opinion_landscape", OpinionLandscapeAgent, role="task", priority=2)
register_agent("zh_multisource_merge", MultisourceMergeAgent, role="task", priority=2)

set_fallback("zh_policy_brief", "zh_risk_scan")


class AgentRegistry:
    """OOP-style registry singleton."""
    def __init__(self):
        self._agents: Dict[str, Any] = dict(AGENT_REGISTRY)

    def register(self, name: str, agent_cls, **meta):
        self._agents[name] = agent_cls
        register_agent(name, agent_cls, **meta)

    def get(self, name: str):
        return get_with_fallback(name)

    def all(self):
        return dict(self._agents)

    def health(self):
        return agent_health_report()


global_registry = AgentRegistry()
