# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Service (V19)
统一入口层：intent → route → pipeline.run(input_text, task_type, language)
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.core.intent_engine import classify
from core.task_router import TaskRouter


class EntryService:
    """
    V19 统一入口层服务
    - 意图识别
    - 任务路由
    - Pipeline 执行（真实 zh_* pipelines）
    - 结构化输出
    """

    def __init__(self, task_router: TaskRouter, pipeline_registry):
        self.task_router = task_router
        self.pipeline_registry = pipeline_registry

    async def handle(
        self,
        text: str,
        language: str = "zh",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        # 1. 意图识别
        intent = classify(text)
        intent.language = language

        if intent.task_type == "clarification_required":
            return {
                "status": "clarification_required",
                "type": "clarification_required",
                "message": "无法识别意图，请补充说明。",
                "intent": intent.__dict__,
            }

        # 2. 路由
        route_result = self.task_router.route(intent)

        if not route_result or not route_result.pipeline:
            return {
                "status": "error",
                "type": "routing_error",
                "message": f"No pipeline available (task_type={intent.task_type})",
                "intent": intent.__dict__,
            }

        # 3. 获取真实 Pipeline
        pipeline = self.pipeline_registry.resolve_pipeline(intent.task_type)
        if not pipeline:
            return {
                "status": "error",
                "type": "pipeline_missing",
                "message": f"Pipeline 未注册（task_type={intent.task_type}）",
                "intent": intent.__dict__,
            }

        # 4. 执行真实 Pipeline（统一参数）
        result = await pipeline.run(
            input_text=text,
            task_type=intent.task_type,
            language=intent.language,
        )

        # 5. 统一结构化输出
        return {
            "status": "success",
            "type": intent.task_type,
            "intent": intent.__dict__,
            "route": route_result.to_dict(),
            "data": result,
        }
