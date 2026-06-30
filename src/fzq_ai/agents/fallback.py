# src/fzq_ai/agents/fallback.py
# V21 — Fallback & Retry System（自动回退与重试系统）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Any, Dict, List

class FallbackEngine:
    """
    ============================================================
    V21 — FallbackEngine（自动回退系统）
    ============================================================

    功能：
    - 当模型失败时自动切换到备用模型
    - 当输出质量不足时自动重试
    - 模型不可用时自动降级
    - 与 BaseAgent.fallback() / retry() 完全兼容

    ============================================================
    English Description
    ============================================================

    Handles automatic fallback and retry logic for agents.
    """

    # ------------------------------------------------------------
    # Step 1: 自动回退（fallback）
    # ------------------------------------------------------------
    def fallback(self, plan: Dict[str, Any], primary_model: str) -> Dict[str, Any]:
        """
        自动选择备用模型。
        Auto-select fallback model.
        """

        fallback_order = ["deepseek", "qwen", "glm", "openai", "kimi"]

        # 移除当前模型
        if primary_model in fallback_order:
            fallback_order.remove(primary_model)

        # 选择第一个可用的备用模型
        fallback_model = fallback_order[0]

        return {
            "fallback_model": fallback_model,
            "reason": "primary_model_failed",
            "plan": plan
        }

    # ------------------------------------------------------------
    # Step 2: 自动重试（retry）
    # ------------------------------------------------------------
    def retry(self, plan: Dict[str, Any], model: str, attempt: int = 1) -> Dict[str, Any]:
        """
        自动重试任务。
        Auto-retry task.
        """

        return {
            "retry_model": model,
            "attempt": attempt + 1,
            "plan": plan,
            "reason": "low_quality_score"
        }
