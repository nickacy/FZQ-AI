"""
FZQ-AI Task Router
任务路由器 — routes user input to the correct pipeline via intent engine.
----------------------------------------------------
意图识别 → Pipeline 选择 → 自动执行
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from dataclasses import dataclass

from fzq_ai.core.intent_engine import classify, IntentResult
from fzq_ai.pipelines.registry import PipelineRegistry


@dataclass
class RouteResult:
    """路由结果"""
    task_type: str
    pipeline_name: str
    confidence: float
    language: str
    intent: IntentResult


class TaskRouter:
    """
    Task Router: intent → pipeline auto-selection.
    任务路由器：意图 → Pipeline 自动选择。
    """

    # Map intent task_type → registered pipeline name
    _ROUTE_MAP = {
        "zh_risk_scan": "zh_risk_scan",
        "zh_policy_brief": "zh_policy_brief",
        "zh_opinion_landscape": "zh_opinion_landscape",
        "zh_multisource_merge": "zh_multisource_merge",
        "daily_report": "daily_report",
        "narrative": "narrative",
        "risk": "risk",
        "news": "news",
    }

    @classmethod
    def route(cls, text: str) -> RouteResult:
        """
        Analyze text and return the best pipeline route.
        分析文本，返回最佳 Pipeline 路由。
        """
        intent = classify(text)
        pipeline_name = cls._ROUTE_MAP.get(intent.task_type, "daily_report")

        # Verify pipeline exists
        try:
            PipelineRegistry.get_entry(pipeline_name)
        except KeyError:
            # Fallback to daily_report if pipeline not found
            pipeline_name = "daily_report"

        return RouteResult(
            task_type=intent.task_type,
            pipeline_name=pipeline_name,
            confidence=intent.confidence,
            language=intent.language,
            intent=intent,
        )

    @classmethod
    def route_and_execute(cls, text: str, **kwargs) -> Dict[str, Any]:
        """
        Route text and execute the selected pipeline.
        路由文本并执行选中的 Pipeline。
        """
        import asyncio

        route = cls.route(text)
        pipeline = PipelineRegistry.get(route.pipeline_name)

        # Build input dict
        payload = {
            "query": text,
            "target_language": route.language,
            "task_type": route.task_type,
            **kwargs,
        }

        # Execute
        if hasattr(pipeline, "run_async"):
            result = asyncio.run(pipeline.run_async(**payload))
        elif hasattr(pipeline, "run"):
            result = pipeline.run(**payload)
        else:
            raise RuntimeError(f"Pipeline {route.pipeline_name} has no run/run_async method")

        return {
            "route": {
                "task_type": route.task_type,
                "pipeline": route.pipeline_name,
                "confidence": route.confidence,
                "language": route.language,
                "keywords": route.intent.keywords_matched,
            },
            "result": result,
        }


__all__ = ["TaskRouter", "RouteResult"]
