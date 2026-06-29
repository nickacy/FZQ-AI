# -*- coding: utf-8 -*-
"""
FZQ-AI Model Router (V20)
统一多模型调度：GLM / Qwen / DeepSeek / MiniMax
"""

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.models.glm_client import GLMClient
from fzq_ai.models.qwen_client import QwenClient
from fzq_ai.models.deepseek_client import DeepSeekClient
from fzq_ai.models.minimax_client import MiniMaxClient


class ModelRouter:
    """
    V20 多模型智能调度：
    - 按任务类型选择最佳模型
    - 按模型状态 fallback
    - 按语言选择模型
    - 按复杂度选择模型
    """

    def __init__(self):
        self.models = {
            "glm": GLMClient(),
            "qwen": QwenClient(),
            "deepseek": DeepSeekClient(),
            "minimax": MiniMaxClient(),
        }

    def select(self, task_type: str, language: str = "zh") -> Any:
        """
        主调度逻辑（可扩展）
        """

        # 舆情分析 → DeepSeek（更强的中文理解）
        if task_type == "zh_opinion_landscape":
            return self.models["deepseek"]

        # 风险扫描 → GLM（更强的结构化输出）
        if task_type == "zh_risk_scan":
            return self.models["glm"]

        # 政策简报 → Qwen（更强的中文生成）
        if task_type == "zh_policy_brief":
            return self.models["qwen"]

        # 多源融合 → DeepSeek（更强的长文本处理）
        if task_type == "zh_multisource_merge":
            return self.models["deepseek"]

        # 默认模型
        return self.models["qwen"]
