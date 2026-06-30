# src/fzq_ai/agents/orchestrator.py
# V21 — Agent Orchestrator（智能体调度器）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Dict, List
from fzq_ai.agents.base import AgentContext, AgentResult, BaseAgent

class AgentOrchestrator:
    """
    ============================================================
    V21 — Agent Orchestrator（智能体调度器）
    ============================================================

    这是 FZQ‑AI 智能体层的核心调度中心。

    功能包括：
    - 按任务名选择智能体
    - 执行智能体 run()
    - 自动 fallback / retry
    - 自动质量评估
    - 自动自愈（Self‑Healing）
    - 多智能体协作（未来 V22）
    - 执行链路追踪（trace）
    - 结果缓存（cache）

    ============================================================
    English Description
    ============================================================

    Central orchestrator for the FZQ‑AI Agent Layer.
    Handles agent selection, execution, fallback, retry,
    evaluation, healing, and future multi-agent collaboration.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, AgentResult] = {}

    # ============================================================
    # 主入口：run_task()
    # ============================================================

    def run_task(self, task_name: str, ctx: AgentContext) -> AgentResult:
        """
        统一入口：按任务名调度对应 Agent（或组合 Agent）
        Unified entry point for running an agent by task name.
        """

        from fzq_ai.agents.registry import get_agent  # lazy import
        agent: BaseAgent = get_agent(task_name)

        trace: List[str] = []
        trace.append(f"[Orchestrator] Selected agent: {agent.name}")

        # Step 1: 执行智能体
        result = agent.run(ctx)
        trace.extend(result.trace)

        # Step 2: 自动 fallback（如果失败）
        if not result.ok:
            trace.append("[Orchestrator] Agent failed → fallback")
            fallback_result = agent.fallback(result.data)
            trace.append("[Orchestrator] Fallback executed")
            result = AgentResult(
                ok=True,
                data=fallback_result,
                warnings=result.warnings,
                trace=trace
            )

        # Step 3: 自动 retry（如果质量不足）
        if hasattr(agent, "evaluate"):
            score = agent.evaluate(result.data)
            trace.append(f"[Orchestrator] Score = {score}")

            if score < 0.5:
                trace.append("[Orchestrator] Score too low → retry")
                retry_result = agent.retry(result.data)
                trace.append("[Orchestrator] Retry executed")
                result = AgentResult(
                    ok=True,
                    data=retry_result,
                    warnings=result.warnings,
                    trace=trace
                )

        # Step 4: 缓存结果
        self._cache[task_name] = result

        return result

    # ============================================================
    # 获取缓存结果
    # ============================================================

    def get_cached(self, task_name: str) -> AgentResult | None:
        return self._cache.get(task_name)
