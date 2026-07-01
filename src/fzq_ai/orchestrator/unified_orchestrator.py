# src/fzq_ai/orchestrator/unified_orchestrator.py
# V23.3 — Unified Orchestrator (Single-Agent + Multi-Agent + V24 Bridge)
# Author: Nick
# Version: V23.3.1

from __future__ import annotations
from typing import Any, Dict, List

from fzq_ai.schemas.route import RouteResult

# 旧系统业务 orchestrator（v4.5 / v14 / v15）
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator

# 新系统多智能体 orchestrator（V22）
from fzq_ai.agents.coop.orchestrator import MultiAgentOrchestrator, AgentTask

# V24 单智能体 orchestrator（统一入口）
from fzq_ai.orchestrator.unified_orchestrator_v24 import UnifiedOrchestratorV24

# 统一注册中心（V23）
from fzq_ai.registry.agents import global_registry as agent_registry
from fzq_ai.registry.pipelines import global_registry as pipeline_registry
from fzq_ai.registry.orchestrators import global_registry as orchestrator_registry


class UnifiedOrchestrator:
    """
    V23 — Unified Orchestrator

    Combines:
    - Single-agent orchestrator (v4.5 / v14 / v15)
    - Multi-agent orchestrator (V22)
    - Autonomous multi-agent loop (V22)
    - Unified V23 entry with RouteResult
    - V24 单智能体桥接（run_single_v24）
    """

    def __init__(self) -> None:
        # 旧系统单智能体 orchestrator
        self.single = TaskOrchestrator()

        # 新系统多智能体 orchestrator
        self.multi = MultiAgentOrchestrator()

        # V24 单智能体 orchestrator（用于新架构）
        self.v24 = UnifiedOrchestratorV24()

        # 统一注册中心（目前主要用于后续扩展）
        self.agent_registry = agent_registry
        self.pipeline_registry = pipeline_registry
        self.orchestrator_registry = orchestrator_registry

    # ------------------------------------------------------------
    # Task classifier (V23)
    # ------------------------------------------------------------
    def classify(self, task_name: str, ctx: Any) -> str:
        """
        Classify task into:
        - "single"   : 旧系统单智能体任务（默认走 V24 桥接）
        - "multi"    : 多智能体协作任务
        - "autonomy" : 自治智能体循环任务
        """
        # 显式 multi_agent 标记优先
        if isinstance(ctx, dict) and ctx.get("multi_agent"):
            return "multi"

        # 以 autonomy 前缀标记自治任务
        if isinstance(task_name, str) and task_name.lower().startswith("autonomy"):
            return "autonomy"

        # 默认视为单智能体任务
        return "single"

    # ------------------------------------------------------------
    # Single-agent execution (old system, 保留但不再作为默认路径)
    # ------------------------------------------------------------
    def run_single_legacy(self, task_name: str, ctx: Any) -> Dict[str, Any]:
        """
        Legacy entry for old single-agent tasks.
        保留旧系统调用链（v4.5 / v14 / v15），用于需要原始行为的场景。
        """
        if hasattr(self.single, "run_scenario"):
            return self.single.run_scenario(task_name)  # type: ignore[attr-defined]

        if isinstance(ctx, dict) and "raw_input" in ctx:
            return self.single.run(text=ctx["raw_input"])
        return self.single.run(text=str(ctx))

    # ------------------------------------------------------------
    # Single-agent execution (V24 桥接，作为 V23 默认路径)
    # ------------------------------------------------------------
    async def run_single_v24(self, task_name: str, ctx: Any) -> RouteResult:
        """
        V24 单智能体桥接：
        - 输入：V23 ctx（通常为 {"raw_input": "..."}）
        - 输出：RouteResult（V24 的 RouteResult.ok）
        - 行为：调用 UnifiedOrchestratorV24.run_single()
        """
        if not isinstance(ctx, dict):
            raw_input = str(ctx)
        else:
            raw_input = ctx.get("raw_input", "")

        agent_ctx = {
            "user_id": "legacy",
            "locale": "zh-CN",
            "focus_regions": [],
            "languages": ["zh"],
            "raw_input": raw_input,
            "metadata": {},
        }

        new_ctx = {"agent_ctx": agent_ctx}

        v24_result = await self.v24.run_single(task_name, new_ctx, options={})

        return RouteResult.ok(
            data=v24_result.data,
            ui_layout=v24_result.ui_layout,
            debug_info=v24_result.debug_info,
            timeline=v24_result.timeline,
            ui_schema=v24_result.ui_schema,
            warnings=v24_result.warnings,
            trace=v24_result.trace,
        )

    # ------------------------------------------------------------
    # Multi-agent execution (V22)
    # ------------------------------------------------------------
def run_multi(self, tasks: List[Dict[str, Any]]) -> RouteResult:
    """
    Unified entry for multi-agent tasks (V22).
    输入为任务字典列表，输出为 RouteResult 包裹的多智能体结果。
    """
    agent_tasks = [
        AgentTask(agent=t["agent"], intent=t["intent"], payload=t["payload"])
        for t in tasks
    ]
    results = self.multi.assign(agent_tasks)

    # ⭐ 修复：RouteResult.ok 需要 Dict[str, Any]
    return RouteResult.ok(data={"results": results})


    # ------------------------------------------------------------
    # Autonomous multi-agent loop (V22)
    # ------------------------------------------------------------
    def run_autonomy_v22(self) -> RouteResult:
        """
        Run one cycle of V22 autonomous multi-agent loop.
        返回自治智能体当前状态，封装为 RouteResult。
        """
        from fzq_ai.agents.autonomy_agent_v22 import AutonomyAgentV22

        agent = AutonomyAgentV22()
        agent.loop(max_cycles=1)
        return RouteResult.ok(data=agent.status)

    # ------------------------------------------------------------
    # Unified V23 entry
    # ------------------------------------------------------------
    async def run(self, task_name: str, ctx: Any = None) -> RouteResult:
        """
        Convenience entry — delegates to run_v23.
        用于 /v23/entry 等入口。
        """
        return await self.run_v23(task_name, ctx)

    async def run_v23(
        self,
        task_name: str,
        ctx: Any = None,
        options: Dict[str, Any] | None = None,
    ) -> RouteResult:
        """
        V23 unified entry point.
        - 统一入口：单智能体 / 多智能体 / 自治智能体
        - 统一返回：RouteResult
        - 统一错误处理：RouteResult.error(...)
        - 单智能体默认走 V24 桥接（run_single_v24）
        """
        task_type = self.classify(task_name, ctx)

        try:
            if task_type == "single":
                # 默认走 V24 单智能体桥接
                return await self.run_single_v24(task_name, ctx)

            elif task_type == "multi":
                if not isinstance(ctx, dict):
                    return RouteResult.error(
                        code="CTX_TYPE_ERROR",
                        message="ctx must be dict for multi-agent tasks",
                        debug_info={"ctx_type": type(ctx).__name__},
                    )

                tasks = ctx.get("tasks", [])
                if not isinstance(tasks, list):
                    return RouteResult.error(
                        code="TASKS_TYPE_ERROR",
                        message="ctx['tasks'] must be a list for multi-agent tasks",
                        debug_info={"tasks_type": type(tasks).__name__},
                    )

                return self.run_multi(tasks)

            elif task_type == "autonomy":
                return self.run_autonomy_v22()

            else:
                return RouteResult.error(
                    code="UNKNOWN_TASK",
                    message=f"Unsupported task type: {task_type}",
                    debug_info={"task_name": task_name, "ctx": ctx},
                )

        except Exception as e:
            return RouteResult.error(
                code="ORCH_ERROR",
                message=str(e),
                debug_info={"task_name": task_name, "ctx": ctx},
            )
