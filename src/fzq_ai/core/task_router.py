# -*- coding: utf-8 -*-
"""
FZQ-AI Task Router (V15-Final)
任务路由器（V15 最终融合版）

本模块负责根据意图识别结果，将任务自动路由到对应的 Pipeline / Agent / Model。
This module routes tasks to the correct Pipeline / Agent / Model based on intent recognition.

核心特性 / Key Features:
1. Pipeline fallback（管道回退）
2. Model fallback（模型回退）
3. Agent fallback（智能体回退）
4. 统一错误格式（统一包装错误）
5. 统一输出结构（结构化结果）
6. 与 Intent Engine 完全兼容
7. 满足 GLM‑5.2 审计要求
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

from fzq_ai.core.intent_engine import IntentResult
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.utils.agent_hub import AGENT_CATALOG
from fzq_ai.llm.router import ModelRouter


# ============================================================
# 1. 路由结果结构 / Route Result Structure
# ============================================================

@dataclass
class RouteResult:
    """
    路由结果（结构化输出）
    Structured routing result
    """
    success: bool
    task_type: str
    pipeline_used: Optional[str]
    agent_used: Optional[str]
    model_used: Optional[str]
    output: Optional[Any]
    error: Optional[str] = None
    fallback_used: Optional[str] = None


# ============================================================
# 2. Task Router 主类 / Main Router Class
# ============================================================

class TaskRouter:
    """
    任务路由器（V15 最终融合版）
    Task Router (V15 Final Fusion Version)
    """

    # Pipeline fallback chain
    PIPELINE_FALLBACK = [
        "zh_risk_scan",
        "zh_policy_brief",
        "zh_opinion_landscape",
        "zh_multisource_merge",
        "daily_report",
    ]

    # Model fallback chain
    MODEL_FALLBACK = [
        "deepseek",
        "qwen",
        "glm",
        "openai",
        "gemini",
    ]

    # Agent fallback chain
    AGENT_FALLBACK = [
        "RiskScanAgent",
        "PolicyBriefAgent",
        "OpinionLandscapeAgent",
        "MultiSourceMergeAgent",
    ]

    def __init__(self):
        self.model_router = ModelRouter()

    # ============================================================
    # 3. 主路由函数 / Main Routing Function
    # ============================================================

    def route(self, intent: IntentResult, user_input: str) -> RouteResult:
        """
        根据意图识别结果执行任务
        Execute task based on intent recognition result
        """

        # 低置信度 → 请求澄清
        if intent.task_type == "clarification_required":
            return RouteResult(
                success=False,
                task_type="clarification_required",
                pipeline_used=None,
                agent_used=None,
                model_used=None,
                output=None,
                error="Low confidence. Need user clarification.",
                fallback_used=None,
            )

        # ============================================================
        # 3.1 Pipeline 路由 + fallback
        # ============================================================

        pipeline = PipelineRegistry.get(intent.task_type)
        fallback_used = None

        if pipeline is None:
            for fb in self.PIPELINE_FALLBACK:
                pipeline = PipelineRegistry.get(fb)
                if pipeline:
                    fallback_used = f"pipeline:{fb}"
                    break

        if pipeline is None:
            return RouteResult(
                success=False,
                task_type=intent.task_type,
                pipeline_used=None,
                agent_used=None,
                model_used=None,
                output=None,
                error="No pipeline available.",
                fallback_used="pipeline:none",
            )

        pipeline_name = pipeline.__class__.__name__

        # ============================================================
        # 3.2 Agent 路由 + fallback
        # ============================================================

        agent = AGENT_CATALOG.get(intent.task_type)

        if agent is None:
            for fb_agent in self.AGENT_FALLBACK:
                if fb_agent in AGENT_CATALOG:
                    agent = AGENT_CATALOG[fb_agent]
                    fallback_used = f"agent:{fb_agent}"
                    break

        agent_name = agent.__class__.__name__ if agent else None

        # ============================================================
        # 3.3 Model 路由 + fallback
        # ============================================================

        model = self.model_router.select(intent.task_type)

        if model is None:
            for fb_model in self.MODEL_FALLBACK:
                model = self.model_router.get_provider(fb_model)
                if model:
                    fallback_used = f"model:{fb_model}"
                    break

        model_name = model.name if model else None

        # ============================================================
        # 3.4 执行 Pipeline
        # ============================================================

        try:
            output = pipeline.run(user_input, agent=agent, model=model)
            return RouteResult(
                success=True,
                task_type=intent.task_type,
                pipeline_used=pipeline_name,
                agent_used=agent_name,
                model_used=model_name,
                output=output,
                error=None,
                fallback_used=fallback_used,
            )

        except Exception as e:
            return RouteResult(
                success=False,
                task_type=intent.task_type,
                pipeline_used=pipeline_name,
                agent_used=agent_name,
                model_used=model_name,
                output=None,
                error=str(e),
                fallback_used=fallback_used,
            )


# ============================================================
# 4. 对外暴露接口 / Public API
# ============================================================

__all__ = ["TaskRouter", "RouteResult"]
