# src/fzq_ai/agents/orchestrator.py
from typing import Dict
from fzq_ai.agents.base import AgentContext, AgentResult, BaseAgent


class AgentOrchestrator:
    def __init__(self) -> None:
        self._cache: Dict[str, AgentResult] = {}

    def run_task(self, task_name: str, ctx: AgentContext) -> AgentResult:
        """
        统一入口：按任务名调度对应 Agent（或组合 Agent）
        """
        from fzq_ai.agents.registry import get_agent  # lazy to break circular import
        agent = get_agent(task_name)
        result = agent.run(ctx)
        # TODO: 后续可加：结果评估、多模型投票、自动回退
        return result
