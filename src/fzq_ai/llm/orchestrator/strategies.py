# src/fzq_ai/llm/orchestrator/strategies.py

from __future__ import annotations
from typing import Dict, Any

from fzq_ai.llm.router import Router


class ModelStrategy:
    """
    定义多模型协同策略：
    - primary(): 主模型
    - validator(): 校验模型
    - repair(): 修复模型
    - audit(): 审计模型
    """

    def __init__(self):
        self.router = Router()

    def primary(self, task: Dict[str, Any]):
        return self.router.get_provider("glm-5.2")

    def validator(self, task: Dict[str, Any]):
        return self.router.get_provider("qwen")

    def repair(self, task: Dict[str, Any]):
        return self.router.get_provider("qwen")

    def audit(self, task: Dict[str, Any]):
        return self.router.get_provider("deepseek")
