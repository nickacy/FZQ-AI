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
from src.fzq_ai.agents.base import AgentContext


class UnifiedOrchestratorV24:
    """
    V24 — 最终 orchestrator：
    - 保留 V23 全部功能
    - 新增 timeline 输出（协作链）
    - 新增 ui_schema 输出（声明式渲染器）
    - 新增自治智能体（ReAct 状态机）
    - 完全兼容 V21 BaseAgent
    - 新增 V23 兼容层 run()
    """

    def __init__(self):
        self.news_agent = NewsAgentV24()
        self.autonomy_agent = AutonomyAgentV24()

    # ============================================================
    # V23 兼容层（旧系统调用 orchestrator.run()）
    # ============================================================

    async def run(self, task: str, ctx: Dict[str, Any], **kwargs):
        """
        兼容旧系统的 TaskOrchestrator.run(task, ctx)
        自动映射到 V24 的 run_single()
        """
        # V23 的 ctx 格式是 {"raw_input": "..."}
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

        # 构造 V24 的 ctx 格式
        new_ctx = {
            "agent_ctx": agent_ctx
        }

        # 调用 V24 的单智能体执行流程
        result = await self.run_single(task, new_ctx, options={})

        # 返回旧系统能理解的格式
        return {
            "success": True,
            "task_type": task,
            "pipeline": None,
            "agent": "news_agent_v24",
            "model": None,
            "fallback_used": False,
            "output": result.data,
            "error": None,
            "recovery_trace": [],
        }

    # ============================================================
    # 单智能体任务（Entry /entry）
    # ============================================================

    async def run_single(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        agent_ctx_dict = ctx["agent_ctx"]

        # Build AgentContext from the dict payload
        agent_ctx = AgentContext(
            user_id=agent_ctx_dict.get("user_id"),
            locale=agent_ctx_dict.get("locale", "zh-CN"),
            focus_regions=agent_ctx_dict.get("focus_regions", []),
            languages=agent_ctx_dict.get("languages", ["zh"]),
            raw_input=agent_ctx_dict.get("raw_input", ""),
            metadata=agent_ctx_dict.get("metadata", {}),
        )

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
