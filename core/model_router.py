# -*- coding: utf-8 -*-
"""
FZQ-AI Model Router (V20)
多模型智能调度（基于真实 providers 路径）
"""

from __future__ import annotations
from typing import Any

# 真实存在的模型客户端路径（来自你的项目结构）
from fzq_ai.llm.providers.glm_provider import GLMProvider
from fzq_ai.llm.providers.qwen_provider import QwenProvider
from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
from fzq_ai.llm.providers.openai_provider import OpenAIProvider
from fzq_ai.llm.providers.gemini_provider import GeminiProvider
from fzq_ai.llm.providers.kimi_provider import KimiProvider


class ModelRouter:
    """
    V20 多模型智能调度：
    - 按任务类型选择最佳模型
    - 按语言选择模型
    - 按场景选择模型
    - 按能力 fallback
    """

    def __init__(self):
        self.models = {
            "glm": GLMProvider(),
            "qwen": QwenProvider(),
            "deepseek": DeepSeekProvider(),
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "kimi": KimiProvider(),
        }

    def select(self, task_type: str, language: str = "zh") -> Any:
        """
        主调度逻辑（可扩展）
        """

        # 舆情分析 → DeepSeek（中文理解强）
        if task_type == "zh_opinion_landscape":
            return self.models["deepseek"]

        # 风险扫描 → GLM（结构化输出强）
        if task_type == "zh_risk_scan":
            return self.models["glm"]

        # 政策简报 → Qwen（中文生成强）
        if task_type == "zh_policy_brief":
            return self.models["qwen"]

        # 多源融合 → DeepSeek（长文本处理强）
        if task_type == "zh_multisource_merge":
            return self.models["deepseek"]

        # 默认模型
        return self.models["qwen"]
