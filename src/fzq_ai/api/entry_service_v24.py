# src/fzq_ai/api/entry_service_v24.py
# V24 — EntryService（统一入口层 · 最终版）
from __future__ import annotations
from typing import Any, Dict

from fzq_ai.orchestrator.unified_orchestrator_v24 import UnifiedOrchestratorV24
from fzq_ai.schemas.route import RouteResult


class EntryServiceV24:
    """V24 unified entry: single / multi / autonomy."""

    def __init__(self):
        self.orchestrator = UnifiedOrchestratorV24()

    def _build_ctx(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw_input = payload.get("input", "")
        languages = payload.get("languages", ["zh"])
        focus_regions = payload.get("focus_regions", [])
        metadata = payload.get("metadata", {})
        return {
            "agent_ctx": {
                "raw_input": raw_input,
                "languages": languages,
                "focus_regions": focus_regions,
                "metadata": metadata,
            }
        }

    async def handle_single(self, payload: Dict[str, Any]) -> RouteResult:
        ctx = self._build_ctx(payload)
        return await self.orchestrator.run_single(task=payload.get("task", "single"), ctx=ctx, options={})

    async def handle_multi(self, payload: Dict[str, Any]) -> RouteResult:
        ctx = self._build_ctx(payload)
        return await self.orchestrator.run_multi(task=payload.get("task", "multi"), ctx=ctx, options={})

    async def handle_autonomy(self, payload: Dict[str, Any]) -> RouteResult:
        ctx = self._build_ctx(payload)
        return await self.orchestrator.run_autonomy(task=payload.get("task", "autonomy"), ctx=ctx, options={})
