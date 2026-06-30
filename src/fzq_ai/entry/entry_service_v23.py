# src/fzq_ai/entry/entry_service_v23.py
from __future__ import annotations
import asyncio
from typing import Any, Dict

from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator
from fzq_ai.agents.blackboard import Blackboard
from fzq_ai.schemas.route import RouteResult


class EntryServiceV23:
    def __init__(self):
        self.orchestrator = UnifiedOrchestrator()

    async def handle(
        self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]
    ) -> RouteResult:

        Blackboard.clear()
        Blackboard.write("req.task", task)
        Blackboard.write("req.ctx", ctx)

        ctx["blackboard"] = Blackboard

        result = await asyncio.to_thread(
            self.orchestrator.run_v23, task, ctx, options
        )

        if result.status == "ok":
            result.debug_info = result.debug_info or {}
            result.debug_info["blackboard_snapshot"] = Blackboard.read_all()

        return result
