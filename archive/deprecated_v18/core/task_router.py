# -*- coding: utf-8 -*-
"""
FZQ-AI Task Router (V15-Minimal)
根据 Intent 决定：Pipeline + Model + Agent + Fallback
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from core.intent_engine import IntentResult
from core.pipelines import PipelineRegistry, BasePipeline


@dataclass
class RouteResult:
    pipeline: BasePipeline
    model_name: str
    agent: Any | None
    fallback_used: bool
    metadata: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline": self.pipeline.name if hasattr(self.pipeline, "name") else str(self.pipeline),
            "model_name": self.model_name,
            "agent": self.agent.__class__.__name__ if self.agent else None,
            "fallback_used": self.fallback_used,
            "metadata": self.metadata or {},
        }


class TaskRouter:
    """
    最小可运行版 TaskRouter：
    - 根据 Intent.task_type 选择 Pipeline
    - 简单固定模型名（后续可扩展为多模型路由）
    - 暂不启用复杂 Agent / Fallback 逻辑
    """

    def __init__(self, pipeline_registry: PipelineRegistry) -> None:
        self.pipeline_registry = pipeline_registry

        # 简单模型映射（后续你可以改成多模型策略）
        self.model_map: Dict[str, str] = {
            "zh_policy_brief": "glm-5.2",
            "zh_risk_scan": "glm-5.2",
            "zh_opinion_landscape": "glm-5.2",
            "zh_multisource_merge": "glm-5.2",
        }

    def route(
        self,
        intent: IntentResult,
        language: str = "zh",
        session_id: str | None = None,
    ) -> RouteResult:
        """
        输入 Intent → 输出 RouteResult
        """

        # 1) 解析 Pipeline
        pipeline = self.pipeline_registry.resolve_pipeline(intent.task_type)
        if pipeline is None:
            # 简单 fallback：回退到 zh_policy_brief
            pipeline = self.pipeline_registry.resolve_pipeline("zh_policy_brief")
            fallback_used = True
        else:
            fallback_used = False

        # 2) 选择模型
        model_name = self.model_map.get(intent.task_type, "glm-5.2")

        # 3) 暂不使用 Agent（留空）
        agent = None

        metadata = {
            "session_id": session_id,
            "language": language,
            "task_type": intent.task_type,
        }

        return RouteResult(
            pipeline=pipeline,
            model_name=model_name,
            agent=agent,
            fallback_used=fallback_used,
            metadata=metadata,
        )
