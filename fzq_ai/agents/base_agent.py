# fzq_ai/agents/base_agent.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """
    所有 Agent 的统一基类。
    """

    name: str = "base-agent"
    description: str = "Base agent"

    @abstractmethod
    async def run(self, query: str) -> Dict[str, Any]:
        """
        执行 Agent 主逻辑，返回结构化结果。
        """
        raise NotImplementedError
