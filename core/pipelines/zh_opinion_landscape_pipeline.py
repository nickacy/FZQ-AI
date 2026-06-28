# -*- coding: utf-8 -*-
"""
ZhOpinionLandscapePipeline / 中文舆情趋势分析 Pipeline (V17)
用于生成舆情趋势折线图数据：
- 时间序列（过去 7 天）
- 舆情热度（0–100）
- 舆情摘要（中英双语）
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
import uuid
import random

from core.pipelines.base import BasePipeline


@dataclass
class ZhOpinionLandscapeResult:
    """
    中文舆情趋势结果 / Zh Opinion Landscape Result
    """
    task_type: str
    timeline: List[str]
    values: List[int]
    summary: str
    confidence: float
    trace_id: str
    duration_ms: float
    status: str
    type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "timeline": self.timeline,
            "values": self.values,
            "summary": self.summary,
            "confidence": self.confidence,
            "trace_id": self.trace_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "type": self.type,
        }


class ZhOpinionLandscapePipeline(BasePipeline):
    """
    ZhOpinionLandscapePipeline (V17)
    中文舆情趋势 Pipeline：
    - 输入：用户文本（text）
    - 输出：结构化舆情趋势数据（用于前端折线图）
    """

    name: str = "zh_opinion_landscape"

    def run(self, text: str, language: str = "zh", session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行舆情趋势分析 / Run opinion trend analysis
        """

        start = time.time()
        trace_id = str(uuid.uuid4())

        # 生成过去 7 天的日期标签 / Generate last 7 days timeline
        timeline = ["6/22", "6/23", "6/24", "6/25", "6/26", "6/27", "6/28"]

        # 随机生成舆情热度（模拟数据）/ Generate random trend values
        values = [random.randint(10, 90) for _ in range(7)]

        # 舆情摘要 / Summary (CN + EN)
        peak_day = timeline[values.index(max(values))]
        summary = (
            f"过去 7 天舆情在 {peak_day} 达到峰值，随后有所回落。"
            f" / Public opinion peaked on {peak_day} and then declined."
        )

        duration_ms = (time.time() - start) * 1000.0

        result = ZhOpinionLandscapeResult(
            task_type="zh_opinion_landscape",
            timeline=timeline,
            values=values,
            summary=summary,
            confidence=0.85,
            trace_id=trace_id,
            duration_ms=duration_ms,
            status="success",
            type="zh_opinion_landscape",
        )

        return result.to_dict()
