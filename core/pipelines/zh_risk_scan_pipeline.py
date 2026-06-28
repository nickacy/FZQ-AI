# -*- coding: utf-8 -*-
"""
ZhRiskScanPipeline / 中文风险扫描 Pipeline (V17)
用于生成五维风险雷达图数据：
- 政治 / Political
- 经济 / Economic
- 社会 / Social
- 科技 / Technological
- 国际 / International
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
import uuid

from core.pipelines.base import BasePipeline


@dataclass
class ZhRiskScanResult:
    """
    中文风险扫描结果 / Zh Risk Scan Result
    """
    task_type: str
    scan_window: Optional[str]
    risks: List[int]
    overall_risk_level: Optional[str]
    entity_watchlist: List[str]
    suggested_actions: List[str]
    summary: Optional[str]
    confidence: Optional[float]
    trace_id: str
    duration_ms: float
    status: str
    type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "scan_window": self.scan_window,
            "risks": self.risks,
            "overall_risk_level": self.overall_risk_level,
            "entity_watchlist": self.entity_watchlist,
            "suggested_actions": self.suggested_actions,
            "summary": self.summary,
            "confidence": self.confidence,
            "trace_id": self.trace_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "type": self.type,
        }


class ZhRiskScanPipeline(BasePipeline):
    """
    ZhRiskScanPipeline (V17)
    中文风险扫描 Pipeline：
    - 输入：用户文本（text）
    - 输出：结构化风险数据（用于前端雷达图）
    """

    name: str = "zh_risk_scan"

    def run(self, text: str, language: str = "zh", session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行风险扫描 / Run risk scan

        Parameters:
        - text: 用户输入文本 / user query text
        - language: 语言代码（默认 zh）/ language code (default zh)
        - session_id: 会话 ID / session id

        Returns:
        - dict: ZhRiskScanResult.to_dict()
        """
        start = time.time()
        trace_id = str(uuid.uuid4())

        # 简单示例逻辑：根据关键词粗略打分
        # Simple demo logic: score by keywords
        text_lower = text.lower()

        political = 2
        economic = 2
        social = 2
        tech = 2
        international = 2

        if "政治" in text or "policy" in text_lower:
            political = 4
        if "经济" in text or "finance" in text_lower or "market" in text_lower:
            economic = 4
        if "社会" in text or "social" in text_lower:
            social = 3
        if "科技" in text or "technology" in text_lower or "ai" in text_lower:
            tech = 5
        if "国际" in text or "global" in text_lower or "geopolitics" in text_lower:
            international = 5

        risks = [political, economic, social, tech, international]

        # 计算总体风险等级 / overall risk level
        avg_risk = sum(risks) / len(risks)
        if avg_risk >= 4:
            overall = "高风险 / High Risk"
        elif avg_risk >= 3:
            overall = "中风险 / Medium Risk"
        else:
            overall = "低风险 / Low Risk"

        # 监测实体 / watchlist
        entity_watchlist: List[str] = []
        if international >= 4:
            entity_watchlist.append("国际局势 / Global Situation")
        if tech >= 4:
            entity_watchlist.append("科技与 AI / Technology & AI")

        # 建议行动 / suggested actions
        suggested_actions: List[str] = [
            "加强对关键领域的监测 / Strengthen monitoring of key domains",
            "定期更新风险评估 / Regularly update risk assessments",
        ]
        if overall.startswith("高风险"):
            suggested_actions.append("启动应急预案 / Activate contingency plans")

        # 摘要 / summary
        summary = (
            f"当前综合风险等级为：{overall}。"
            f"科技与国际维度风险相对较高，需要重点关注。"
        )

        duration_ms = (time.time() - start) * 1000.0

        result = ZhRiskScanResult(
            task_type="zh_risk_scan",
            scan_window=None,
            risks=risks,
            overall_risk_level=overall,
            entity_watchlist=entity_watchlist,
            suggested_actions=suggested_actions,
            summary=summary,
            confidence=0.8,
            trace_id=trace_id,
            duration_ms=duration_ms,
            status="success",
            type="zh_risk_scan",
        )

        return result.to_dict()
