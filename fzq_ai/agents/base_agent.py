# fzq_ai/agents/base_agent.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """
    """

    @abstractmethod
    async def run(self, query: str) -> Dict[str, Any]:
        """
        """
        raise NotImplementedError
