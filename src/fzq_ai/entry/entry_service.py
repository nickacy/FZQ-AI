"""
V15 Entry Service — Unified Entry Protocol.

Order: intent recognition -> task routing -> pipeline execution.

Usage:
    service = EntryService()
    result = await service.handle(text="...", task_type="zh_policy_brief")
"""

from __future__ import annotations
from typing import Any, Optional

from fzq_ai.core.intent_engine import classify
from fzq_ai.core.task_router import TaskRouter, RouteResult


class EntryService:
    """V15 unified entry: intent -> route -> execute."""

    def __init__(self):
        self._intent_engine = classify
        self._task_router = TaskRouter()

    async def handle(
        self, text: str, task_type: Optional[str] = None
    ) -> RouteResult:
        """
        Handle a user input:
          1. Classify intent
          2. Route to appropriate pipeline
          3. Return RouteResult

        Args:
            text: User input text (Chinese or English)
            task_type: Explicit task type override (optional)
                       One of: zh_policy_brief, zh_risk_scan,
                               zh_opinion_landscape, zh_multisource_merge

        Returns:
            RouteResult with output, model info, and metadata
        """
        # 1. Intent recognition
        intent = self._intent_engine(text)

        # 2. Apply explicit task_type override
        if task_type:
            intent.task_type = task_type

        # 3. Route to pipeline (async)
        result = await self._task_router.route(intent, text)
        return result
