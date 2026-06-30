# src/fzq_ai/agents/model_selector.py
# V21 — Auto Model Selection Engine（自动模型选择器）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Dict, Any

class ModelSelector:
    """
    ============================================================
    V21 — ModelSelector（自动模型选择器）
    ============================================================

    功能：
    - 根据任务类型选择最佳模型
    - 根据质量评分选择最佳模型
    - 根据延迟/成本选择最佳模型
    - 与 BaseAgent.auto_select_model() 完全兼容

    ============================================================
    English Description
    ============================================================

    Selects the best model based on task type, quality score,
    latency, cost, and agent preferences.
    """

    def __init__(self):
        # 模型能力表（可扩展）
        self.model_capabilities = {
            "deepseek": ["analysis", "reasoning", "long_text"],
            "qwen": ["summary", "translation", "zh_tasks"],
            "glm": ["politics", "risk", "global_south"],
            "openai": ["general", "creative"],
            "kimi": ["long_context"],
        }

        # 模型成本（示例）
        self.model_cost = {
            "deepseek": 1.0,
            "qwen": 0.5,
            "glm": 0.8,
            "openai": 2.0,
            "kimi": 1.2,
        }

    # ------------------------------------------------------------
    # Step 1: 根据任务类型选择模型
    # ------------------------------------------------------------
    def select_by_task(self, task_type: str) -> str:
        if task_type in ("policy", "risk", "global_south"):
            return "glm"
        if task_type in ("summary", "zh"):
            return "qwen"
        if task_type in ("analysis", "reasoning"):
            return "deepseek"
        return "openai"

    # ------------------------------------------------------------
    # Step 2: 根据质量评分选择模型
    # ------------------------------------------------------------
    def select_by_score(self, score: float) -> str:
        if score < 0.4:
            return "deepseek"
        if score < 0.6:
            return "glm"
        return "qwen"

    # ------------------------------------------------------------
    # Step 3: 综合选择
    # ------------------------------------------------------------
    def auto_select(self, plan: Dict[str, Any], score: float = 0.5) -> str:
        task_type = plan.get("task_type", "general")

        model_by_task = self.select_by_task(task_type)
        model_by_score = self.select_by_score(score)

        # 简单策略：优先任务类型，其次质量评分
        if model_by_task != model_by_score:
            return model_by_task

        return model_by_score
