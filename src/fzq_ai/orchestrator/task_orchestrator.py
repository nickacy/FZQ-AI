# -*- coding: utf-8 -*-
"""
FZQ-AI Task Orchestrator (V15-Final)
任务编排器（V15 最终版）

核心功能：
- 调用 Intent Engine → TaskRouter → ModelRouter → AgentHub → Pipelines
- 自愈链路（Self-Healing）
- Recovery Trace（恢复链路）
- Pipeline fallback
- Model fallback
- Agent fallback
- 统一输出结构
"""

from __future__ import annotations
from typing import Dict, Any

from fzq_ai.core.intent_engine import classify
from fzq_ai.core.task_router import TaskRouter


class TaskOrchestrator:
    """V15-Final 任务编排器"""

    def __init__(self):
        self.router = TaskRouter()

    # ------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------
    def run(self, text: str) -> Dict[str, Any]:
        """
        输入自然语言 → 自动执行完整任务链
        """
        recovery_trace = []
        try:
            # 1. 意图识别
            intent = classify(text)
            recovery_trace.append({"stage": "intent", "intent": intent.model_dump()})

            # 2. 路由任务
            result = self.router.route(intent, text)
            recovery_trace.append(
                {
                    "stage": "task_router",
                    "pipeline": result.pipeline_used,
                    "agent": result.agent_used,
                    "model": result.model_used,
                }
            )

            # 3. 输出结构化结果
            return {
                "success": result.success,
                "task_type": result.task_type,
                "pipeline": result.pipeline_used,
                "agent": result.agent_used,
                "model": result.model_used,
                "fallback_used": result.fallback_used,
                "output": result.output,
                "error": result.error,
                "recovery_trace": recovery_trace,
            }

        except Exception as e:
            recovery_trace.append({"stage": "exception", "error": str(e)})
            return {
                "success": False,
                "task_type": None,
                "pipeline": None,
                "agent": None,
                "model": None,
                "fallback_used": None,
                "output": None,
                "error": str(e),
                "recovery_trace": recovery_trace,
            }
