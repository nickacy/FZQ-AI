# fzq_ai/scenarios/base.py
"""v6.0: Unified Scenario interface — all scenarios return ServiceResult."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

from fzq_ai.domain.models import ServiceResult


class BaseScenario(ABC):
    """
    v6.0 Scenario contract:
    - execute() returns ServiceResult
    - to_dict() returns structured JSON-safe dict
    - name / description for UI discoverability
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Scenario display name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """What this scenario does."""
        ...

    @abstractmethod
    def execute(self, **kwargs: Any) -> ServiceResult:
        """Run the scenario. Must return ServiceResult."""
        ...

    def to_dict(self, result: ServiceResult) -> Dict[str, Any]:
        """Serialize result to JSON-safe dict."""
        return {
            "scenario": self.name,
            "success": result.success,
            "data": result.data,
            "error": result.error,
        }
