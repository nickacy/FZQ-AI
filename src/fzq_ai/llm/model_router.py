# src/fzq_ai/llm/model_router.py
# -*- coding: utf-8 -*-
"""
FZQ-AI Model Router (V20)
多模型智能调度（统一 Provider 构造函数）
"""

from __future__ import annotations
from typing import Any

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
            "glm": GLMProvider("glm-4-flash"),
            "qwen": QwenProvider("qwen-max"),
            "deepseek": DeepSeekProvider("deepseek-chat"),
            "openai": OpenAIProvider("gpt-4o"),
            "gemini": GeminiProvider("gemini-2.0-flash"),
            "kimi": KimiProvider("moonshot-v1-32k"),
        }

    def select(self, task_type: str, language: str = "zh") -> Any:
        """
        主调度逻辑（可扩展）
        """

        if task_type == "zh_opinion_landscape":
            return self.models["deepseek"]

        if task_type == "zh_risk_scan":
            return self.models["glm"]

        if task_type == "zh_policy_brief":
            return self.models["qwen"]

        if task_type == "zh_multisource_merge":
            return self.models["deepseek"]

        return self.models["qwen"]
