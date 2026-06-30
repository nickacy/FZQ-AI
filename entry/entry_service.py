# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Service (V19)
Unified entry: intent -> route -> execute
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.core.intent_engine import classify
from core.task_router import TaskRouter


class EntryService:
    """V19 unified entry service."""

    def __init__(self):
        self._intent_engine = classify
        self._task_router = TaskRouter()

    async def handle(
        self,
        text: str,
        language: str = "zh",
        session_id: str | None = None,
        task_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle user input: intent classify -> route -> execute."""

        # 1. Intent recognition
        intent = classify(text)
        intent.language = language

        if intent.task_type == "clarification_required":
            return {
                "status": "clarification_required",
                "type": "clarification_required",
                "message": "Unable to identify intent. Please provide more details.",
                "intent": intent.__dict__,
            }

        # 2. Route
        route_result = await self._task_router.route(intent, text)

        if not route_result or not route_result.success:
            return {
                "status": "error",
                "type": "routing_error",
                "message": f"No pipeline available (task_type={intent.task_type})",
                "intent": intent.__dict__,
            }

        # 3. Structured output from route result
        return {
            "status": "success",
            "type": intent.task_type,
            "intent": intent.__dict__,
            "output": route_result.output,
            "model_used": route_result.model_used,
            "pipeline_used": route_result.pipeline_used,
            "data": route_result.output if route_result.output else {},
        }
