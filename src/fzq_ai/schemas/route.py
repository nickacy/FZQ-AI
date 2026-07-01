# src/fzq_ai/schemas/route.py
from __future__ import annotations
from typing import Any, Dict, Optional, List
import uuid


class RouteResult:
    """
    Unified return structure for all orchestrator outputs.
    V24 增量增强版：
    - 保留 V23 全部字段（status, data, ui_layout, debug_info, trace_id）
    - 新增 timeline（协作链）
    - 新增 ui_schema（声明式渲染器）
    - 新增 warnings / trace（可选）
    """

    def __init__(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        ui_layout: Optional[Any] = None,
        debug_info: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,

        # ★ V24 新增字段（不影响旧版本）
        timeline: Optional[List[Dict[str, Any]]] = None,
        ui_schema: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        trace: Optional[List[str]] = None,
    ):
        # ===== V23 原有字段 =====
        self.status = status
        self.data = data or {}
        self.ui_layout = ui_layout
        self.debug_info = debug_info
        self.trace_id = trace_id or str(uuid.uuid4())

        # ===== V24 新增字段（完全兼容旧版本） =====
        self.timeline = timeline or []
        self.ui_schema = ui_schema
        self.warnings = warnings or []
        self.trace = trace or []

    # ============================================================
    # 工厂方法（保持旧版本兼容）
    # ============================================================

    @staticmethod
    def ok(
        data: Dict[str, Any],
        ui_layout=None,
        debug_info=None,
        timeline=None,
        ui_schema=None,
        warnings=None,
        trace=None,
    ):
        return RouteResult(
            status="ok",
            data=data,
            ui_layout=ui_layout,
            debug_info=debug_info,
            timeline=timeline,
            ui_schema=ui_schema,
            warnings=warnings,
            trace=trace,
        )

    @staticmethod
    def error(code: str, message: str, debug_info=None):
        return RouteResult(
            status="error",
            data={"code": code, "message": message},
            debug_info=debug_info,
        )
