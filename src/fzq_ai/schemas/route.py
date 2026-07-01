# src/fzq_ai/schemas/route.py
from __future__ import annotations
from typing import Any, Optional, List, Dict
import uuid


class RouteResult:
    """
    Unified return structure for all orchestrator outputs.
    V24 统一增强版：
    - 保留 V23 全部字段（status, data, ui_layout, debug_info, trace_id）
    - 新增 timeline（协作链）
    - 新增 ui_schema（声明式渲染器）
    - 新增 warnings / trace（可选）
    - ★ data 支持 Any（Dict / List / str / model）
    """

    def __init__(
        self,
        status: str,
        data: Any = None,  # ★ V24: 支持任意类型
        ui_layout: Optional[Any] = None,
        debug_info: Optional[Any] = None,
        trace_id: Optional[str] = None,

        # ===== V24 新增字段 =====
        timeline: Optional[List[Any]] = None,
        ui_schema: Optional[Any] = None,
        warnings: Optional[List[str]] = None,
        trace: Optional[List[Any]] = None,
    ):
        # ===== V23 原有字段 =====
        self.status = status
        self.data = data
        self.ui_layout = ui_layout
        self.debug_info = debug_info
        self.trace_id = trace_id or str(uuid.uuid4())

        # ===== V24 新增字段 =====
        self.timeline = timeline or []
        self.ui_schema = ui_schema
        self.warnings = warnings or []
        self.trace = trace or []

    # ============================================================
    # 成功结果（兼容 V23 + V24）
    # ============================================================
    @staticmethod
    def ok(
        data: Any = None,  # ★ V24: 支持任意类型
        ui_layout: Optional[Any] = None,
        debug_info: Optional[Any] = None,
        timeline: Optional[List[Any]] = None,
        ui_schema: Optional[Any] = None,
        warnings: Optional[List[str]] = None,
        trace: Optional[List[Any]] = None,
    ) -> "RouteResult":
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

    # ============================================================
    # 错误结果（兼容 V23 + V24）
    # ============================================================
    @staticmethod
    def error(
        message: str,
        code: Optional[str] = None,
        debug_info: Optional[Any] = None,
    ) -> "RouteResult":
        return RouteResult(
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
    # 序列化（兼容 FastAPI / Agent Store）
    # ============================================================
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "ui_layout": self.ui_layout,
            "debug_info": self.debug_info,
            "trace_id": self.trace_id,
            "timeline": self.timeline,
            "ui_schema": self.ui_schema,
            "warnings": self.warnings,
            "trace": self.trace,
        }
