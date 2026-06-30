# src/fzq_ai/agents/registry.py
# V21 — Agent Registry（智能体注册表）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Dict
from fzq_ai.agents.base import BaseAgent

# ============================================================
# 导入所有智能体（按需扩展）
# ============================================================

from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.agents.tasks.policy_brief_agent import PolicyBriefAgent
from fzq_ai.agents.tasks.risk_scan_agent import RiskScanAgent
from fzq_ai.agents.tasks.opinion_landscape_agent import OpinionLandscapeAgent
from fzq_ai.agents.tasks.multisource_merge_agent import MultisourceMergeAgent

# ============================================================
# 智能体注册表（唯一来源）
# ============================================================

_AGENT_REGISTRY: Dict[str, BaseAgent] = {
    "news_center": NewsCenterAgent(),
    "zh_policy_brief": PolicyBriefAgent(),
    "zh_risk_scan": RiskScanAgent(),
    "zh_opinion_landscape": OpinionLandscapeAgent(),
    "zh_multisource_merge": MultisourceMergeAgent(),
}

# ============================================================
# 获取智能体
# ============================================================

def get_agent(name: str) -> BaseAgent:
    """
    获取智能体实例。
    Get agent instance by name.
    """
    if name not in _AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {name}")
    return _AGENT_REGISTRY[name]
