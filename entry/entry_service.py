# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Service (V17)
统一入口层：intent → route → execute
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.core.intent_engine import classify
from core.task_router import TaskRouter


class EntryService:
    """
    V17 统一入口层服务
    - 负责意图识别
    - 负责任务路由
    - 负责 Pipeline 执行
    - 负责结构化输出
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
        route_result = self.task_router.route(intent.task_type)

        if not route_result or not route_result.pipeline_name:
            return {
                "status": "error",
                "type": "routing_error",
                "message": f"未找到可用 Pipeline（task_type={intent.task_type}）",
                "intent": intent.__dict__,
            }

        # 3. 获取 Pipeline
        pipeline = self.pipeline_registry.resolve_pipeline(intent.task_type)
        if not pipeline:
            return {
                "status": "error",
                "type": "pipeline_missing",
                "message": f"Pipeline 未注册（task_type={intent.task_type}）",
                "intent": intent.__dict__,
            }

        # 4. 执行 Pipeline
        result = await pipeline.run(
            input_text=text,
            intent=intent,
            route=route_result,
        )

        # 5. 统一结构化输出
        return {
            "status": "success",
            "type": intent.task_type,
            "intent": intent.__dict__,
            "route": route_result.__dict__,
            "data": result,
        }
