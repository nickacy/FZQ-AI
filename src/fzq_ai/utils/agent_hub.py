# -*- coding: utf-8 -*-
"""
FZQ-AI Agent Hub (V15-Final)
智能体注册中心（V15 最终版）

负责统一管理所有智能体实例，供 TaskRouter 调用。
"""

from __future__ import annotations

from fzq_ai.agents.risk_scan_agent import RiskScanAgent
from fzq_ai.agents.policy_brief_agent import PolicyBriefAgent
from fzq_ai.agents.opinion_landscape_agent import OpinionLandscapeAgent
from fzq_ai.agents.multisource_merge_agent import MultiSourceMergeAgent


# ============================================================
# Agent Catalog / 智能体注册表
# ============================================================

AGENT_CATALOG = {
    "zh_risk_scan": RiskScanAgent(),
    "zh_policy_brief": PolicyBriefAgent(),
    "zh_opinion_landscape": OpinionLandscapeAgent(),
    "zh_multisource_merge": MultiSourceMergeAgent(),
}

__all__ = ["AGENT_CATALOG"]
