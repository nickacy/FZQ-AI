# src/fzq_ai/entry/entry_service_v23.py
from __future__ import annotations
import asyncio
from typing import Any, Dict

from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator
from fzq_ai.agents.blackboard import Blackboard
from fzq_ai.schemas.route import RouteResult


class EntryServiceV23:
    """
    Unified entry layer for V23 architecture.
    Connects HTTP layer → UnifiedOrchestrator → Blackboard.
    """

    def __init__(self):
        self.orchestrator = UnifiedOrchestrator()

    async def handle(
        self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]
    ) -> RouteResult:

        # 1. Reset Blackboard for this request
        Blackboard.clear()
        Blackboard.write("req.task", task)
        Blackboard.write("req.ctx", ctx)

        # 2. Inject Blackboard reference into context
        ctx["blackboard"] = Blackboard

        # 3. Run synchronous orchestrator in thread pool (non-blocking)
        result = await asyncio.to_thread(
            self.orchestrator.run_v23, task, ctx, options
        )

        # 4. Attach Blackboard snapshot for debugging / UI rendering
        if result.status == "ok":
            result.debug_info = result.debug_info or {}
            result.debug_info["blackboard_snapshot"] = Blackboard.read_all()

        return result
