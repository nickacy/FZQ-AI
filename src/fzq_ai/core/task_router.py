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

from pydantic import BaseModel


class RouteResult(BaseModel):
    success: bool = False
    task_type: str = ""
    pipeline_used: Optional[str] = None
    output: Optional[Any] = None
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

        # 0. 澄清机制：IntentEngine 报告低置信度 → 立即返回
        if task_type == "clarification_required":
            return RouteResult(
                success=False,
                task_type="clarification_required",
                pipeline_used=None,
                output=None,
                error=intent.reason or "Low confidence; please clarify your request.",
                fallback_used="clarification",
            )
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

        # 4. 调用 pipeline（统一 sync/async 桥接）
        try:
            output = await _call_pipeline(pipeline, user_input)
            return RouteResult(
                success=True,
                task_type=task_type,
                pipeline_used=pipeline_key,
                output=output,
                error=None,
                fallback_used=fallback_used,
            )
        except Exception as e:
            return RouteResult(
                success=False,
                task_type=task_type,
                pipeline_used=pipeline_key,
                output=None,
                error=f"Pipeline execution failed: {str(e)}",
                fallback_used=fallback_used,
            )


# ── Unified pipeline call bridge (sync + async) ──────────────

async def _call_pipeline(pipeline, user_input: str):
    """Call pipeline.run_async or pipeline.run with graceful fallback."""
    import asyncio
    import inspect

    # 1. Prefer run_async
    if hasattr(pipeline, "run_async"):
        sig = inspect.signature(pipeline.run_async)
        params = list(sig.parameters.keys())
        if "content" in params:
            return await pipeline.run_async(content=user_input)
        if "query" in params:
            return await pipeline.run_async(query=user_input)
        if "text" in params:
            return await pipeline.run_async(text=user_input)
        if "input" in params or "prompt" in params:
            return await pipeline.run_async(**{"input": user_input, "prompt": user_input})
        if "req" in params:
            return await pipeline.run_async(req={"query": user_input})
        # Fallback: keyword-only pipelines (e.g. zh run_async(self, **kwargs))
        # can't take a positional arg. `_extract_user_input` accepts
        # event_topic/content/input/text/query/req — "text" is the most
        # compatible neutral key.
        return await pipeline.run_async(text=user_input)

    # 2. Fallback to run()
    if hasattr(pipeline, "run"):
        sig = inspect.signature(pipeline.run)
        if inspect.iscoroutinefunction(pipeline.run):
            return await pipeline.run(user_input)
        else:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: pipeline.run(user_input))

    raise RuntimeError(f"No run() or run_async() found on {type(pipeline).__name__}")
