# src/fzq_ai/orchestrator/blackboard.py
# V24 — Standalone Blackboard (no dependency on agents/__init__.py)
# Context-local shared state via contextvars; same API as agents.blackboard.

from __future__ import annotations
from typing import Any, Dict, Optional
from contextvars import ContextVar

_blackboard_ctx: ContextVar[Dict[str, Any]] = ContextVar("blackboard_ctx", default={})


class Blackboard:
    """Request-level shared context for agents and orchestrators."""

    @staticmethod
    def _get_data() -> Dict[str, Any]:
        return _blackboard_ctx.get()

    @staticmethod
    def _set_data(data: Dict[str, Any]) -> None:
        _blackboard_ctx.set(data)

    @staticmethod
    def write(key: str, value: Any) -> None:
        data = Blackboard._get_data().copy()
        data[key] = value
        Blackboard._set_data(data)

    @staticmethod
    def read(key: str, default: Optional[Any] = None) -> Any:
        return Blackboard._get_data().get(key, default)

    @staticmethod
    def read_all() -> Dict[str, Any]:
        return Blackboard._get_data().copy()

    @staticmethod
    def clear() -> None:
        Blackboard._set_data({})

    @staticmethod
    def ensure_keys(keys: Dict[str, Any]) -> None:
        data = Blackboard._get_data().copy()
        for k, v in keys.items():
            if k not in data:
                data[k] = v
        Blackboard._set_data(data)

    @staticmethod
    def update(values: Dict[str, Any]) -> None:
        data = Blackboard._get_data().copy()
        data.update(values)
        Blackboard._set_data(data)
