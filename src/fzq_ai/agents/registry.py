from typing import Dict
from fzq_ai.agents.base import BaseAgent
from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.agents.tasks.policy_brief_agent import PolicyBriefAgent
from fzq_ai.agents.tasks.risk_scan_agent import RiskScanAgent
from fzq_ai.agents.tasks.opinion_landscape_agent import OpinionLandscapeAgent
from fzq_ai.agents.tasks.multisource_merge_agent import MultisourceMergeAgent

_AGENT_REGISTRY: Dict[str, BaseAgent] = {
    "news_center": NewsCenterAgent(),
    "zh_policy_brief": PolicyBriefAgent(),
    "zh_risk_scan": RiskScanAgent(),
    "zh_opinion_landscape": OpinionLandscapeAgent(),
    "zh_multisource_merge": MultisourceMergeAgent(),
}

def get_agent(name: str) -> BaseAgent:
    if name not in _AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {name}")
    return _AGENT_REGISTRY[name]
