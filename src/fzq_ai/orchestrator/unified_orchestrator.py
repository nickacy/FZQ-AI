# src/fzq_ai/orchestrator/unified_orchestrator.py
# V23.3 — Unified Orchestrator (Single-Agent + Multi-Agent)
# Author: Nick
# Version: V23.3.0

from __future__ import annotations
from typing import Any, Dict, List

from fzq_ai.schemas.route import RouteResult

# 旧系统业务 orchestrator（v4.5 / v14 / v15）
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator

# 新系统多智能体 orchestrator（V22）
from fzq_ai.agents.coop.orchestrator import MultiAgentOrchestrator, AgentTask

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
    """

    def __init__(self) -> None:
        # 旧系统单智能体 orchestrator
        self.single = TaskOrchestrator()

        # 新系统多智能体 orchestrator
        self.multi = MultiAgentOrchestrator()

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
        - "single"   : 旧系统单智能体任务
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
    # Single-agent execution (old system)
    # ------------------------------------------------------------
    def run_single(self, task_name: str, ctx: Any) -> Dict[str, Any]:
        """
        Unified entry for old single-agent tasks.
        """
        # run_scenario exists in scenario_orchestrator.py
        if hasattr(self.single, "run_scenario"):
            return self.single.run_scenario(task_name)  # type: ignore[attr-defined]

        # Fallback: use TaskOrchestrator.run with text input
        if isinstance(ctx, dict) and "raw_input" in ctx:
            return self.single.run(text=ctx["raw_input"])
        return self.single.run(text=str(ctx))

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
        data = self.multi.assign(agent_tasks)
        return RouteResult.ok(data=data)

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
    def run(self, task_name: str, ctx: Any = None) -> RouteResult:
        """Convenience entry — delegates to run_v23.  Used by /v23/entry."""
        return self.run_v23(task_name, ctx)

    def run_v23(
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
        """
        task_type = self.classify(task_name, ctx)

        try:
            if task_type == "single":
                data = self.run_single(task_name, ctx)
                return RouteResult.ok(data=data)

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
