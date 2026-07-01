# src/fzq_ai/api/entry_service_v24.py
# V24 — EntryService（统一入口层 · 最终版）
# 保留 V23 设计风格 + 增量增强（single / multi / autonomy）

from __future__ import annotations
from typing import Any, Dict

from src.fzq_ai.orchestrator.unified_orchestrator_v24 import UnifiedOrchestratorV24
from src.fzq_ai.schemas.route import RouteResult


class EntryServiceV24:
    """
    V24 统一入口层：
    - 对接 UnifiedOrchestratorV24
    - 提供 single / multi / autonomy 三种入口模式
    - 返回 RouteResult（含 timeline + ui_schema）
    """

    def __init__(self):
        self.orchestrator = UnifiedOrchestratorV24()

    # ============================================================
    # 公共上下文构造
    # ============================================================

    def _build_ctx(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        将前端 / APP 传入的 JSON 转换为内部上下文结构。
        这里保持简单，方便你后续扩展。
        """
        raw_input = payload.get("input", "")
        languages = payload.get("languages", ["zh"])
        focus_regions = payload.get("focus_regions", [])
        metadata = payload.get("metadata", {})

        agent_ctx = {
            "raw_input": raw_input,
            "languages": languages,
            "focus_regions": focus_regions,
            "metadata": metadata,
        }

        return {
            "agent_ctx": agent_ctx,
        }

    # ============================================================
    # 单智能体入口（/entry）
    # ============================================================

    async def handle_single(self, payload: Dict[str, Any]) -> RouteResult:
        """
        单智能体任务入口：
        - 对接 UnifiedOrchestratorV24.run_single()
        """
        ctx = self._build_ctx(payload)
        options: Dict[str, Any] = {}

        return await self.orchestrator.run_single(
            task=payload.get("task", "single"),
            ctx=ctx,
            options=options,
        )

    # ============================================================
    # 多智能体入口（/multi）
    # ============================================================

    async def handle_multi(self, payload: Dict[str, Any]) -> RouteResult:
        """
        多智能体任务入口：
        - 当前复用 run_single()
        - 未来可扩展为真正多 Agent 协作
        """
        ctx = self._build_ctx(payload)
        options: Dict[str, Any] = {}

        return await self.orchestrator.run_multi(
            task=payload.get("task", "multi"),
            ctx=ctx,
            options=options,
        )

    # ============================================================
    # 自治智能体入口（/autonomy）
    # ============================================================

    async def handle_autonomy(self, payload: Dict[str, Any]) -> RouteResult:
        """
        自治智能体任务入口：
        - 对接 UnifiedOrchestratorV24.run_autonomy()
        - 输出状态机 + 协作链 + 最终总结
        """
        ctx = self._build_ctx(payload)
        options: Dict[str, Any] = {}

        return await self.orchestrator.run_autonomy(
            task=payload.get("task", "autonomy"),
            ctx=ctx,
            options=options,
        )
