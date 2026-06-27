"""FZQ-AI Agents module — role-based intelligence agents."""

from fzq_ai.agents.base import BaseAgent
from fzq_ai.agents.news_center_agent import NewsCenterAgent


# Lazy accessor for agent catalog (avoids circular import from registry -> orchestrator -> registry)
def get_agent_catalog():
    from fzq_ai.agents.registry import _AGENT_REGISTRY
    return _AGENT_REGISTRY


def get_agent(name: str):
    from fzq_ai.agents.registry import get_agent as _get_agent
    return _get_agent(name)


# AGENT_CATALOG is a property-like accessor for backward compat
# Call get_agent_catalog() to get the actual dict
AGENT_CATALOG = property(lambda self: get_agent_catalog())

__all__ = ["AGENT_CATALOG", "BaseAgent", "get_agent", "get_agent_catalog", "NewsCenterAgent"]
