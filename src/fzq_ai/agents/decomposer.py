# src/fzq_ai/agents/decomposer.py
# V21 — Task Decomposer（任务分解器）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from fzq_ai.agents.base import AgentContext, AgentResult
from fzq_ai.registry.agents import get_agent

@dataclass
class SubTask:
    """
    子任务结构（用于任务树）
    """
    name: str
    description: str
    agent: str
    context: AgentContext


@dataclass
class DecompositionResult:
    """
    任务分解结果
    """
    ok: bool
    subtasks: List[SubTask]
    merged: Dict[str, Any]
    trace: List[str]


class TaskDecomposer:
    """
    ============================================================
    V21 — TaskDecomposer（任务分解器）
    ============================================================

    功能：
    - 自动拆分复杂任务
    - 为每个子任务选择智能体
    - 执行子任务
    - 合并结果
    - 生成任务树（Task Tree）
    - 与 orchestrator 完全兼容

    ============================================================
    English Description
    ============================================================

    TaskDecomposer splits complex tasks into subtasks,
    assigns agents, executes them, and merges results.
    """

    # ------------------------------------------------------------
    # Step 1: 自动任务拆分
    # ------------------------------------------------------------
    def decompose(self, task_name: str, ctx: AgentContext) -> List[SubTask]:
        """
        根据任务名自动拆分子任务。
        Auto-decompose task into subtasks.
        """

        subtasks: List[SubTask] = []

        # 示例：政策简报任务拆分
        if task_name == "zh_policy_brief":
            subtasks.append(SubTask(
                name="news_center",
                description="收集相关新闻",
                agent="news_center",
                context=ctx
            ))
            subtasks.append(SubTask(
                name="zh_risk_scan",
                description="扫描风险点",
                agent="zh_risk_scan",
                context=ctx
            ))
            subtasks.append(SubTask(
                name="zh_opinion_landscape",
                description="分析舆论环境",
                agent="zh_opinion_landscape",
                context=ctx
            ))

        # 示例：多源合并任务拆分
        elif task_name == "zh_multisource_merge":
            subtasks.append(SubTask(
                name="news_center",
                description="收集多源新闻",
                agent="news_center",
                context=ctx
            ))

        # 默认：单任务 → 不拆分
        else:
            subtasks.append(SubTask(
                name=task_name,
                description="单任务执行",
                agent=task_name,
                context=ctx
            ))

        return subtasks

    # ------------------------------------------------------------
    # Step 2: 执行子任务
    # ------------------------------------------------------------
    def execute_subtasks(self, subtasks: List[SubTask]) -> tuple[Dict[str, Any], List[str]]:
        merged: Dict[str, Any] = {}
        trace: List[str] = []

        for sub in subtasks:
            trace.append(f"[Decomposer] Running subtask: {sub.name} → agent: {sub.agent}")
            agent = get_agent(sub.agent)
            result: AgentResult = agent.run(sub.context)

            merged[sub.name] = result.data
            trace.extend(result.trace)

        return merged, trace

    # ------------------------------------------------------------
    # Step 3: 总入口
    # ------------------------------------------------------------
    def run(self, task_name: str, ctx: AgentContext) -> DecompositionResult:
        trace: List[str] = []
        trace.append(f"[Decomposer] Start decomposition for task: {task_name}")

        # Step 1: 拆分任务
        subtasks = self.decompose(task_name, ctx)
        trace.append(f"[Decomposer] Subtasks count: {len(subtasks)}")

        # Step 2: 执行子任务
        merged, subtrace = self.execute_subtasks(subtasks)  # type: ignore
        trace.extend(subtrace)

        return DecompositionResult(
            ok=True,
            subtasks=subtasks,
            merged=merged,
            trace=trace
        )
