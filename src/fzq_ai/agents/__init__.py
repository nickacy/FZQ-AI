# -*- coding: utf-8 -*-
"""
FZQ-AI Agents Package (V15-Final)
智能体模块（V15 最终版）

导出所有角色智能体，供 AgentHub / TaskRouter 使用。
"""

from .risk_scan_agent import RiskScanAgent
from .policy_brief_agent import PolicyBriefAgent
from .opinion_landscape_agent import OpinionLandscapeAgent
from .multisource_merge_agent import MultiSourceMergeAgent
from .news_center_agent import NewsCenterAgent  # 保留旧版兼容性

__all__ = [
    "RiskScanAgent",
    "PolicyBriefAgent",
    "OpinionLandscapeAgent",
    "MultiSourceMergeAgent",
    "NewsCenterAgent",
]
