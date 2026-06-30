# src/fzq_ai/agents/blackboard.py
# V23 — Blackboard System for Multi-Agent Collaboration
# Author: Nick
# Version: V23.1.0

from __future__ import annotations
from typing import Any, Dict, Optional
from contextvars import ContextVar


# Context-local storage for blackboard data
_blackboard_ctx: ContextVar[Dict[str, Any]] = ContextVar("blackboard_ctx", default={})


class Blackboard:
    """
    V23 Blackboard System

    - Request-level shared context for agents and orchestrators
    - Backed by contextvars to avoid cross-request interference
    - Provides simple read/write/clear API
    """

    @staticmethod
    def _get_data() -> Dict[str, Any]:
        return _blackboard_ctx.get()

    @staticmethod
    def _set_data(data: Dict[str, Any]) -> None:
        _blackboard_ctx.set(data)

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    @staticmethod
    def write(key: str, value: Any) -> None:
        """
        Write a value to the blackboard under the given key.
        """
        data = Blackboard._get_data().copy()
        data[key] = value
        Blackboard._set_data(data)

    @staticmethod
    def read(key: str, default: Optional[Any] = None) -> Any:
        """
        Read a value from the blackboard.
        Returns default if key is not present.
        """
        return Blackboard._get_data().get(key, default)

    @staticmethod
    def read_all() -> Dict[str, Any]:
        """
        Return a shallow copy of all blackboard data.
        """
        return Blackboard._get_data().copy()

    @staticmethod
    def clear() -> None:
        """
        Clear all data from the blackboard for the current context.
        """
        Blackboard._set_data({})

    # ------------------------------------------------------------
    # Helper methods for orchestration
    # ------------------------------------------------------------
    @staticmethod
    def ensure_keys(keys: Dict[str, Any]) -> None:
        """
        Ensure a set of keys exist on the blackboard, filling defaults if missing.
        """
        data = Blackboard._get_data().copy()
        for k, v in keys.items():
            if k not in data:
                data[k] = v
        Blackboard._set_data(data)

    @staticmethod
    def update(values: Dict[str, Any]) -> None:
        """
        Bulk update multiple keys on the blackboard.
        """
        data = Blackboard._get_data().copy()
        data.update(values)
        Blackboard._set_data(data)
