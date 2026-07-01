# -*- coding: utf-8 -*-
"""
FZQ-AI Agents Package (V19-Final)
智能体模块（V19 最终版）

从 agents/tasks/ 导出所有角色智能体，供 AgentHub / TaskRouter 使用。
"""

from .tasks.risk_scan_agent import RiskScanAgent
from .tasks.policy_brief_agent import PolicyBriefAgent
from .tasks.opinion_landscape_agent import OpinionLandscapeAgent
from .tasks.multisource_merge_agent import MultisourceMergeAgent
from .news_center_agent import NewsCenterAgent

__all__ = [
    "RiskScanAgent",
    "PolicyBriefAgent",
    "OpinionLandscapeAgent",
    "MultisourceMergeAgent",
    "NewsCenterAgent",
]
