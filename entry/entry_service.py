# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Service (V17)
Unified entry: intent -> route -> execute
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.core.intent_engine import classify
from core.task_router import TaskRouter


class EntryService:
    """V17 unified entry service."""

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

        if not route_result or not route_result.pipeline:
            return {
                "status": "error",
                "type": "routing_error",
                "message": f"No pipeline available (task_type={intent.task_type})",
                "intent": intent.__dict__,
            }

        # 3. Execute pipeline
        result = await route_result.pipeline.run(
            input_text=text,
            intent=intent,
            route=route_result,
        )

        # 4. Structured output
        return {
            "status": "success",
            "type": intent.task_type,
            "intent": intent.__dict__,
            "route": route_result.to_dict() if hasattr(route_result, "to_dict") else route_result.__dict__,
            "data": result,
        }
