# src/fzq_ai/agents/registry.py
from typing import Dict
from fzq_ai.agents.base import BaseAgent
from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.agents.tasks.policy_brief_agent import PolicyBriefAgent
# TODO: risk_scan_agent, opinion_landscape_agent, multisource_merge_agent

_AGENT_REGISTRY: Dict[str, BaseAgent] = {
    "news_center": NewsCenterAgent(),
    "zh_policy_brief": PolicyBriefAgent(),
    # "zh_risk_scan": RiskScanAgent(),
    # "zh_opinion_landscape": OpinionLandscapeAgent(),
    # "zh_multisource_merge": MultisourceMergeAgent(),
}

def get_agent(name: str) -> BaseAgent:
    if name not in _AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {name}")
    return _AGENT_REGISTRY[name]
