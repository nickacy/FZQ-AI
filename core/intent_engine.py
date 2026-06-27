# -*- coding: utf-8 -*-
"""
FZQ-AI Intent Engine (V15-Minimal)
规则 + 结构化 IntentResult
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class IntentResult:
    task_type: str          # 例如：zh_policy_brief / zh_risk_scan
    confidence: float       # 0.0 - 1.0
    language: str           # "zh" / "en"
    raw_text: str           # 原始输入
    metadata: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "confidence": self.confidence,
            "language": self.language,
            "raw_text": self.raw_text,
            "metadata": self.metadata or {},
        }


class IntentEngine:
    """
    最小可运行版 IntentEngine：
    - 基于关键词的简单规则
    - 后续可以替换为 LLM / 更复杂模型
    """

    def __init__(self) -> None:
        # 简单关键词规则映射
        self.rules_zh = {
            "风险": "zh_risk_scan",
            "风险扫描": "zh_risk_scan",
            "舆情": "zh_opinion_landscape",
            "舆论": "zh_opinion_landscape",
            "多源": "zh_multisource_merge",
            "合并": "zh_multisource_merge",
            "简报": "zh_policy_brief",
            "政策": "zh_policy_brief",
        }

        self.default_task_zh = "zh_policy_brief"

    def detect_intent(
        self,
        text: str,
        language: str = "zh",
        session_id: str | None = None,
    ) -> IntentResult:
        """
        输入自然语言 → 输出结构化 IntentResult
        """

        text_lower = text.lower()
        task_type = self.default_task_zh
        confidence = 0.3  # 默认较低置信度

        # 简单中文规则匹配
        for keyword, mapped_task in self.rules_zh.items():
            if keyword in text_lower:
                task_type = mapped_task
                confidence = 0.8
                break

        metadata = {
            "session_id": session_id,
            "matched_rule": task_type if confidence >= 0.8 else None,
        }

        return IntentResult(
            task_type=task_type,
            confidence=confidence,
            language=language,
            raw_text=text,
            metadata=metadata,
        )
