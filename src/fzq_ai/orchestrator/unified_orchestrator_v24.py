# src/fzq_ai/orchestrator/unified_orchestrator_v24.py
# V24 — Unified Orchestrator（最终版）
# 保留 V23 全部功能 + 增量增强（timeline + ui_schema + autonomy）

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.orchestrator.blackboard import Blackboard
from fzq_ai.schemas.route import RouteResult
from fzq_ai.ui.ui_schema import UISchema

# V24 Agents
from fzq_ai.agents.news_agent_v24 import NewsAgentV24
from fzq_ai.agents.autonomy_agent_v24 import AutonomyAgentV24
from fzq_ai.agents.base import AgentContext


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
        V23 ctx 格式：{"raw_input": "..."}
        """
        raw_input = ""
        if isinstance(ctx, dict):
            raw_input = ctx.get("raw_input", str(ctx))
        else:
            raw_input = str(ctx)

        agent_ctx = {
            "user_id": "legacy",
            "locale": "zh-CN",
            "focus_regions": [],
            "languages": ["zh"],
            "raw_input": raw_input,
            "metadata": {},
        }

        new_ctx = {
            "agent_ctx": agent_ctx
        }

        try:
            result = await self.run_single(task, new_ctx, options={})
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
        except Exception as e:
            return {
                "success": False,
                "task_type": task,
                "pipeline": None,
                "agent": "news_agent_v24",
                "model": None,
                "fallback_used": True,
                "output": None,
                "error": str(e),
                "recovery_trace": [
                    {"stage": "exception", "error": str(e)}
                ],
            }

    # ============================================================
    # 单智能体任务（Entry /entry）
    # ============================================================

    async def run_single(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        """
        V24 单智能体执行：
        - 使用 NewsAgentV24
        - 使用 CivilizationEngine 做计划/共识增强
        - 输出 timeline + ui_schema + civilization_trace
        - 返回 RouteResult（兼容 V23 + V24）
        """
        # Extract civilization from context
        civilization = ctx.get("civilization")
        agent_ctx_dict = ctx.get("agent_ctx", {})

        # ── Civilization: remember the task ──
        civ_trace: list[dict] = []
        if civilization:
            try:
                civilization.remember("last_task", task)
                civilization.remember("last_input", agent_ctx_dict.get("raw_input", "")[:200])
                civ_trace.append({"stage": "civilization.remember", "key": "last_task"})
            except Exception:
                pass

        agent_ctx = AgentContext(
            user_id=agent_ctx_dict.get("user_id"),
            locale=agent_ctx_dict.get("locale", "zh-CN"),
            focus_regions=agent_ctx_dict.get("focus_regions", []),
            languages=agent_ctx_dict.get("languages", ["zh"]),
            raw_input=agent_ctx_dict.get("raw_input", ""),
            metadata={
                **agent_ctx_dict.get("metadata", {}),
                "civilization": ctx.get("civilization"),
            },
        )

        # ── Civilization: plan before execution ──
        if civilization:
            try:
                civ_snapshot = civilization.snapshot()
                civ_trace.append({"stage": "civilization.snapshot", "agents": civ_snapshot.get("agents", [])})
            except Exception:
                pass

        try:
            result = await self.news_agent.run(agent_ctx)
        except Exception as e:
            return RouteResult.error(
                message=str(e),
                code="AGENT_EXEC_ERROR",
                debug_info={
                    "agent": "news_agent_v24",
                    "task": task,
                    "raw_input": agent_ctx.raw_input,
                },
            )

        # ── Civilization: generate consensus after execution ──
        civ_consensus = None
        if civilization:
            try:
                civilization.remember("last_result", repr(result.data)[:500])
                civ_consensus = civilization._generate_consensus() if hasattr(civilization, "_generate_consensus") else None
                civ_trace.append({"stage": "civilization.consensus", "consensus": civ_consensus})
            except Exception:
                pass

        timeline = Blackboard.read("sys.timeline", [])

        ui_schema = UISchema.layout([
            UISchema.card("智能体输出", result.data),
            UISchema.timeline_block("协作链", timeline),
        ])

        return RouteResult.ok(
            data=result.data,
            ui_layout=None,
            debug_info={
                "agent_trace": result.trace,
                "civilization_trace": civ_trace,
                "civilization_consensus": civ_consensus,
            },
            timeline=timeline,
            ui_schema=ui_schema,
            warnings=result.warnings,
            trace=result.trace,
        )

    # ============================================================
    # 多智能体任务（Entry /multi）
    # ============================================================

    async def run_multi(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        """
        V24 多智能体占位实现：
        当前复用单智能体逻辑，未来可扩展为真正的多智能体协作。
        """
        return await self.run_single(task, ctx, options)

    # ============================================================
    # 自治智能体任务（Entry /autonomy）
    # ============================================================

    async def run_autonomy(self, task: str, ctx: Dict[str, Any], options: Dict[str, Any]):
        """
        V24 自治智能体（ReAct 状态机）执行流程：
        - DECOMPOSE / ACT / REFLECT / FINALIZE
        - 输出状态机轨迹 + timeline + ui_schema
        """
        agent_ctx = ctx.get("agent_ctx", {})

        try:
            plan = self.autonomy_agent.plan(agent_ctx)
        except Exception as e:
            return RouteResult.error(
                message=str(e),
                code="AUTONOMY_PLAN_ERROR",
                debug_info={
                    "stage": "DECOMPOSE",
                    "task": task,
                    "agent_ctx": agent_ctx,
                },
            )

        try:
            model = self.autonomy_agent.route(plan)
        except Exception as e:
            return RouteResult.error(
                message=str(e),
                code="AUTONOMY_ROUTE_ERROR",
                debug_info={
                    "stage": "ROUTE",
                    "task": task,
                    "plan": plan,
                },
            )

        try:
            act_result = await self.autonomy_agent.execute(model, plan)
        except Exception as e:
            return RouteResult.error(
                message=str(e),
                code="AUTONOMY_EXEC_ERROR",
                debug_info={
                    "stage": "ACT",
                    "task": task,
                    "model": model,
                    "plan": plan,
                },
            )

        try:
            reflect_result = self.autonomy_agent.reflect(act_result)
        except Exception as e:
            return RouteResult.error(
                message=str(e),
                code="AUTONOMY_REFLECT_ERROR",
                debug_info={
                    "stage": "REFLECT",
                    "task": task,
                    "act_result": act_result,
                },
            )

        try:
            final_result = self.autonomy_agent.heal(reflect_result)
        except Exception as e:
            return RouteResult.error(
                message=str(e),
                code="AUTONOMY_HEAL_ERROR",
                debug_info={
                    "stage": "FINALIZE",
                    "task": task,
                    "reflect_result": reflect_result,
                },
            )

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
