# -*- coding: utf-8 -*-
"""
BasePipeline (V17-Final)
所有 Pipeline 的统一基类（中英双语）
"""

from __future__ import annotations
from typing import Any, Dict
import time
import uuid


class BasePipeline:
    """
    Pipeline 基类 / Base class for all pipelines
    """

    name: str = "base_pipeline"

    def run(self, text: str, language: str = "zh", session_id: str | None = None) -> Dict[str, Any]:
        """
        默认 Pipeline（占位）/ Default placeholder pipeline
        """
        start = time.time()
        trace_id = str(uuid.uuid4())

        return {
            "task_type": self.name,
            "message": "Base pipeline executed (placeholder).",
            "trace_id": trace_id,
            "duration_ms": (time.time() - start) * 1000.0,
            "status": "success",
            "type": self.name,
        }
