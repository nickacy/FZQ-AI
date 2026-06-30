# src/fzq_ai/orchestrator/unified_orchestrator.py
# V23 — Unified Orchestrator (Single-Agent + Multi-Agent)
# Author: Nick
# Version: V23.2.1

from __future__ import annotations
from typing import Any, Dict, List

# 旧系统业务 orchestrator（v4.5 / v14 / v15）
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator

# 新系统多智能体 orchestrator（V22）
from fzq_ai.agents.coop.orchestrator import MultiAgentOrchestrator, AgentTask


class UnifiedOrchestrator:
    """
    V23 — Unified Orchestrator
    Combines:
    - Single-agent orchestrator (v4.5 / v14 / v15)
    - Multi-agent orchestrator (V22)
    """

    def __init__(self):
        self.single = TaskOrchestrator()
        self.multi = MultiAgentOrchestrator()

    # ------------------------------------------------------------
    # Single-agent execution (old system)
    # ------------------------------------------------------------
    def run(self, task_name: str, ctx: Any) -> Dict[str, Any]:
        """
        Unified entry for old single-agent tasks.
        """
        # run_scenario exists in scenario_orchestrator.py
        if hasattr(self.single, "run_scenario"):
            return self.single.run_scenario(task_name)  # type: ignore[attr-defined]

        # run_nl exists in task_orchestrator.py
        return self.single.run_nl(task_name.replace("_", " "))  # type: ignore[attr-defined]

    # ------------------------------------------------------------
    # Multi-agent execution (V22)
    # ------------------------------------------------------------
    def run_multi(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Unified entry for multi-agent tasks (V22).
        """
        agent_tasks = [
            AgentTask(agent=t["agent"], intent=t["intent"], payload=t["payload"])
            for t in tasks
        ]
        return self.multi.assign(agent_tasks)

    # ------------------------------------------------------------
    # Autonomous multi-agent loop (V22)
    # ------------------------------------------------------------
    def run_autonomy_v22(self) -> Dict[str, Any]:
        """
        Run one cycle of V22 autonomous multi-agent loop.
        """
        from fzq_ai.agents.autonomy_agent_v22 import AutonomyAgentV22
        agent = AutonomyAgentV22()
        agent.loop(max_cycles=1)
        return agent.status

