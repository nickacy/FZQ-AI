# src/fzq_ai/orchestrator/unified_orchestrator_v24.py
# V24 — Unified Orchestrator（最终版）
# 保留 V23 全部功能 + 增量增强（timeline + ui_schema + autonomy）

from __future__ import annotations
from typing import Any, Dict

from src.fzq_ai.orchestrator.blackboard import Blackboard
from src.fzq_ai.schemas.route import RouteResult
from src.fzq_ai.ui.ui_schema import UISchema

# V24 Agents
from src.fzq_ai.agents.news_agent_v24 import NewsAgentV24
from src.fzq_ai.agents.autonomy_agent_v24 import AutonomyAgentV24


class UnifiedOrchestratorV24:
    """
    V24 — 最终 orchestrator：
    - 保留 V23 全部功能
    - 新增 timeline 输出（协作链）
    - 新增 ui_schema 输出（声明式渲染器）
    - 新增自治智能体（ReAct 状态机）
    - 完全兼容 V21 BaseAgent
    """

    def __init__(self):
        self.news_agent = NewsAgentV24()
        self.autonomy_agent = AutonomyAgentV24()

    # ============================================================
    # 单智能体任务（Entry /entry）
    # ============================================================

    async def run_single(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        agent_ctx = ctx["agent_ctx"]

        # V21 BaseAgent.run() 是同步的
        result = self.news_agent.run(agent_ctx)

        timeline = Blackboard.read("sys.timeline", [])

        ui_schema = UISchema.layout([
            UISchema.card("智能体输出", result.data),
            UISchema.timeline_block("协作链", timeline),
        ])

        return RouteResult.ok(
            data=result.data,
            ui_layout=None,
            debug_info=result.trace,
            timeline=timeline,
            ui_schema=ui_schema,
            warnings=result.warnings,
            trace=result.trace,
        )

    # ============================================================
    # 多智能体任务（Entry /multi）
    # ============================================================

    async def run_multi(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        # 未来可扩展多个 Agent
        return await self.run_single(task, ctx, options)

    # ============================================================
    # 自治智能体任务（Entry /autonomy）
    # ============================================================

    async def run_autonomy(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        agent_ctx = ctx["agent_ctx"]

        # 1. 规划（DECOMPOSE）
        plan = self.autonomy_agent.plan(agent_ctx)

        # 2. 模型选择
        model = self.autonomy_agent.route(plan)

        # 3. 执行（ACT）
        act_result = await self.autonomy_agent.execute(model, plan)

        # 4. 反思（REFLECT）
        reflect_result = self.autonomy_agent.reflect(act_result)

        # 5. 自愈（FINALIZE）
        final_result = self.autonomy_agent.heal(reflect_result)

        # 6. 读取状态机轨迹
        states = {
            "DECOMPOSE": Blackboard.read("autonomy.DECOMPOSE", {}),
            "ACT": Blackboard.read("autonomy.ACT", {}),
            "REFLECT": Blackboard.read("autonomy.REFLECT", {}),
            "FINALIZE": Blackboard.read("autonomy.FINALIZE", {}),
        }

        timeline = Blackboard.read("sys.timeline", [])

        ui_schema = UISchema.layout([
            UISchema.state_machine("自治智能体状态机", states),
            UISchema.timeline_block("协作链", timeline),
            UISchema.card("最终输出", final_result),
        ])

        return RouteResult.ok(
            data=final_result,
            ui_layout=None,
            debug_info={"states": states},
            timeline=timeline,
            ui_schema=ui_schema,
            warnings=[],
            trace=[],
        )
