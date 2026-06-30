# src/fzq_ai/schemas/route.py
from __future__ import annotations
from typing import Any, Dict, Optional
import uuid


class RouteResult:
    """
    Unified return structure for all orchestrator outputs.
    Used by web_app.py and EntryServiceV23.
    """

    def __init__(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        ui_layout: Optional[Any] = None,
        debug_info: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ):
        self.status = status
        self.data = data or {}
        self.ui_layout = ui_layout
        self.debug_info = debug_info
        self.trace_id = trace_id or str(uuid.uuid4())

    @staticmethod
    def ok(data: Dict[str, Any], ui_layout=None, debug_info=None):
        return RouteResult(
            status="ok",
            data=data,
            ui_layout=ui_layout,
            debug_info=debug_info,
        )

    @staticmethod
    def error(code: str, message: str, debug_info=None):
        return RouteResult(
            status="error",
            data={"code": code, "message": message},
            debug_info=debug_info,
        )
