# -*- coding: utf-8 -*-
"""
FZQ-AI Task Router (V19-Final · Compatible Edition)
完全兼容你现有的 zh-pipelines / registry / orchestrator / ModelClient
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Dict

from fzq_ai.core.intent_engine import IntentResult
from fzq_ai.pipelines.registry import PipelineRegistry


@dataclass
class RouteResult:
    success: bool
    task_type: str
    pipeline_used: Optional[str]
    output: Optional[Any]
    error: Optional[str] = None
    fallback_used: Optional[str] = None
    agent_used: Optional[str] = None
    model_used: Optional[str] = None
    pipeline_name: Optional[str] = None


class TaskRouter:
    """
    V19-Final 任务路由器（兼容你现有 zh-pipelines）
    """

    # task_type → pipeline_key 映射（带 @v1）
    PIPELINE_MAP = {
        "zh_policy_brief": "zh_policy_brief",
        "zh_risk_scan": "zh_risk_scan",
        "zh_opinion_landscape": "zh_opinion_landscape",
        "zh_multisource_merge": "zh_multisource_merge",
    }

    # fallback 顺序
    PIPELINE_FALLBACK = [
        "zh_policy_brief",
        "zh_risk_scan",
        "zh_opinion_landscape",
        "zh_multisource_merge",
    ]

    # ------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------
    async def route(self, intent: IntentResult, user_input: str) -> RouteResult:

        task_type = intent.task_type

        # 1. 找到 pipeline key
        pipeline_key = self.PIPELINE_MAP.get(task_type)

        fallback_used = None

        # 2. 如果找不到 → fallback
        if pipeline_key is None:
            for fb in self.PIPELINE_FALLBACK:
                try:
                    PipelineRegistry.get(fb)
                    pipeline_key = fb
                    fallback_used = f"pipeline:{fb}"
                    break
                except KeyError:
                    continue

        if pipeline_key is None:
            return RouteResult(
                success=False,
                task_type=task_type,
                pipeline_used=None,
                output=None,
                error="No pipeline available.",
                fallback_used="pipeline:none",
            )

        # 3. 获取 pipeline 实例
        try:
            pipeline = PipelineRegistry.get(pipeline_key)
        except Exception as e:
            return RouteResult(
                success=False,
                task_type=task_type,
                pipeline_used=pipeline_key,
                output=None,
                error=str(e),
                fallback_used=fallback_used,
            )

        # 4. 调用 pipeline.run_async（兼容不同签名）
        try:
            # 尝试传递 content 参数（多数 pipeline 的通用接口）
            output = await pipeline.run_async(content=user_input)
            return RouteResult(
                success=True,
                task_type=task_type,
                pipeline_used=pipeline_key,
                output=output,
                error=None,
                fallback_used=fallback_used,
            )
        except TypeError as te:
            # 如果 pipeline 不接受 content 参数，尝试直接传递 kwargs
            if "unexpected keyword argument" in str(te) and "content" in str(te):
                output = await pipeline.run_async(**{"text": user_input, "topic": user_input})
                return RouteResult(
                    success=True,
                    task_type=task_type,
                    pipeline_used=pipeline_key,
                    output=output,
                    error=None,
                    fallback_used=fallback_used,
                )
            raise
        except Exception as e:
            return RouteResult(
                success=False,
                task_type=task_type,
                pipeline_used=pipeline_key,
                output=None,
                error=str(e),
                fallback_used=fallback_used,
            )
