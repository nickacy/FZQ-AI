# src/fzq_ai/entry/entry_service_v23.py
from __future__ import annotations
import asyncio
from typing import Any, Dict

# 旧系统 orchestrator（保留）
from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator

# 新系统 orchestrator（V24）
from fzq_ai.orchestrator.unified_orchestrator_v24 import UnifiedOrchestratorV24

from fzq_ai.orchestrator.blackboard import Blackboard
from fzq_ai.schemas.route import RouteResult


class EntryServiceV23:
    def __init__(self):
        # 保留旧 orchestrator（为了兼容旧系统）
        self.orchestrator_v23 = UnifiedOrchestrator()

        # 新 orchestrator（用于实际执行）
        self.orchestrator_v24 = UnifiedOrchestratorV24()

    async def handle(
        self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]
    ) -> RouteResult:

        # 清空黑板
        Blackboard.clear()
        Blackboard.write("req.task", task)
        Blackboard.write("req.ctx", ctx)

        ctx["blackboard"] = Blackboard

        try:
            # 旧系统 ctx 格式：{"raw_input": "..."}
            raw_input = ctx.get("raw_input", "")

            # 构造 V24 的 agent_ctx
            agent_ctx = {
                "user_id": "legacy",
                "locale": "zh-CN",
                "focus_regions": [],
                "languages": ["zh"],
                "raw_input": raw_input,
                "metadata": {},
            }

            new_ctx = {"agent_ctx": agent_ctx}

            # 调用 V24 的单智能体执行流程
            v24_result = await self.orchestrator_v24.run_single(
                task, new_ctx, options={}
            )

            # 将 V24 的 RouteResult 转换为 V23 的 RouteResult
            final_result = RouteResult.ok(
                data=v24_result.data,
                ui_layout=v24_result.ui_layout,
                debug_info=v24_result.debug_info,
                timeline=v24_result.timeline,
                ui_schema=v24_result.ui_schema,
                warnings=v24_result.warnings,
                trace=v24_result.trace,
            )

        except Exception as e:
            final_result = RouteResult.error(str(e))

        # 黑板快照
        final_result.debug_info = final_result.debug_info or {}
        final_result.debug_info["blackboard_snapshot"] = Blackboard.read_all()

        return final_result
