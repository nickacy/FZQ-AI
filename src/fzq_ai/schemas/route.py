# src/fzq_ai/schemas/route.py
from __future__ import annotations
from typing import Any, Optional, List
import uuid
from pydantic import BaseModel, Field


class RouteResult(BaseModel):
    """
    Unified return structure for all orchestrator outputs.
    V24 Pydantic edition — replaces the legacy plain-class RouteResult.
    """

    status: str = "ok"
    data: Any = None
    ui_layout: Optional[Any] = None
    debug_info: Optional[Any] = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # V24 fields
    timeline: List[Any] = Field(default_factory=list)
    ui_schema: Optional[Any] = None
    warnings: List[str] = Field(default_factory=list)
    trace: List[Any] = Field(default_factory=list)

    # ============================================================
    # 成功结果
    # ============================================================
    @classmethod
    def ok(
        cls,
        data: Any = None,
        ui_layout: Optional[Any] = None,
        debug_info: Optional[Any] = None,
        timeline: Optional[List[Any]] = None,
        ui_schema: Optional[Any] = None,
        warnings: Optional[List[str]] = None,
        trace: Optional[List[Any]] = None,
    ) -> "RouteResult":
        return cls(
            status="ok",
            data=data,
            ui_layout=ui_layout,
            debug_info=debug_info,
            timeline=timeline or [],
            ui_schema=ui_schema,
            warnings=warnings or [],
            trace=trace or [],
        )

    # ============================================================
    # 错误结果
    # ============================================================
    @classmethod
    def error(
        cls,
        message: str,
        code: Optional[str] = None,
        debug_info: Optional[Any] = None,
    ) -> "RouteResult":
        return cls(
            status="error",
            data={
                "error": message,
                "code": code,
                "debug_info": debug_info,
            },
            debug_info=debug_info,
            timeline=[],
            ui_schema=None,
            warnings=[],
            trace=[],
        )

    # ============================================================
    # Backward compat: to_dict() → model_dump()
    # ============================================================
    def to_dict(self) -> dict:
        """DEPRECATED: use model_dump() for Pydantic serialization."""
        return self.model_dump()
