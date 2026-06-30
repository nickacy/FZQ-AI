# src/fzq_ai/agents/coop/orchestrator.py
# V22 — Multi-Agent Orchestrator（多智能体调度器）
# Author: Nick
# Version: V22.3.0

from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass

from fzq_ai.agents.coop.protocol import AgentMessage, AgentIntent
from fzq_ai.agents.coop.blackboard import Blackboard
from fzq_ai.agents.registry import get_agent
from fzq_ai.agents.base import AgentContext


@dataclass
class AgentTask:
    """
    多智能体任务结构
    """
    agent: str
    intent: str
    payload: Any


class MultiAgentOrchestrator:
    """
    V22 — 多智能体调度器
    负责：
    - 多智能体任务分配
    - 多智能体协作执行
    - 多智能体推理链
    - 黑板交互
    """

    def __init__(self):
        self.blackboard = Blackboard()

    # ------------------------------------------------------------
    # Step 1: 分配任务
    # ------------------------------------------------------------
    def assign(self, tasks: List[AgentTask]) -> List[Dict[str, Any]]:
        results = []

        for task in tasks:
            agent = get_agent(task.agent)

            ctx = AgentContext(
                user_id="multi-agent",
                locale="en-US",
                focus_regions=["Global"],
                languages=["en"],
                raw_input=str(task.payload),
                metadata={"intent": task.intent}
            )

            output = agent.run(ctx)

            # 写入黑板
            self.blackboard.write(
                agent=task.agent,
                key=task.intent,
                value=output.data,
                metadata={"trace": output.trace}
            )

            results.append({
                "agent": task.agent,
                "intent": task.intent,
                "result": output.data,
                "trace": output.trace
            })

        return results

    # ------------------------------------------------------------
    # Step 2: 多智能体协作推理链
    # ------------------------------------------------------------
    def chain(self, chain_definition: List[AgentTask]) -> Dict[str, Any]:
        """
        多智能体推理链：
        agent1 → agent2 → agent3 → ...
        """
        chain_results = self.assign(chain_definition)

        merged = {}
        for r in chain_results:
            merged[f"{r['agent']}_{r['intent']}"] = r["result"]

        return merged

    # ------------------------------------------------------------
    # Step 3: 多智能体协作（黑板驱动）
    # ------------------------------------------------------------
    def collaborate(self, intents: List[str]) -> Dict[str, Any]:
        """
        根据黑板内容触发多智能体协作。
        """
        results = {}

        for intent in intents:
            latest = self.blackboard.latest(intent)
            if not latest:
                continue

            # 触发协作智能体
            agent_name = latest.agent
            agent = get_agent(agent_name)

            ctx = AgentContext(
                user_id="multi-agent",
                locale="en-US",
                focus_regions=["Global"],
                languages=["en"],
                raw_input=str(latest.value),
                metadata={"source": "blackboard"}
            )

            output = agent.run(ctx)

            results[agent_name] = output.data

        return results
