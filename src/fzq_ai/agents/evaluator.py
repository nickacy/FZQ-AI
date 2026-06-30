# src/fzq_ai/agents/evaluator.py
# V21 — Model Evaluator（模型评估器）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Any, Dict, List
import re

class ModelEvaluator:
    """
    ============================================================
    V21 — ModelEvaluator（模型评估器）
    ============================================================

    功能：
    - 质量评分（0–1）
    - 事实性检查（自相矛盾检测）
    - 风格一致性检查（是否符合任务风格）
    - 结构化输出检查（字段是否完整）
    - 模型选择建议（未来自动模型选择）

    ============================================================
    English Description
    ============================================================

    Evaluates model outputs for quality, consistency, structure,
    and provides scoring for agent decision-making.
    """

    # ------------------------------------------------------------
    # Step 1: 结构化检查
    # ------------------------------------------------------------
    def check_structure(self, result: Dict[str, Any], required_fields: List[str]) -> float:
        """
        检查字段是否完整。
        Check if required fields exist.
        """
        missing = 0
        for field in required_fields:
            if field not in result or result[field] in (None, "", []):
                missing += 1

        completeness = 1.0 - (missing / len(required_fields))
        return max(0.0, min(1.0, completeness))

    # ------------------------------------------------------------
    # Step 2: 风格一致性检查
    # ------------------------------------------------------------
    def check_style(self, text: str, expected_keywords: List[str]) -> float:
        """
        检查是否包含任务风格关键词。
        Check if text contains expected keywords.
        """
        if not text:
            return 0.0

        hits = sum(1 for kw in expected_keywords if kw.lower() in text.lower())
        score = hits / len(expected_keywords)
        return max(0.0, min(1.0, score))

    # ------------------------------------------------------------
    # Step 3: 自相矛盾检查（事实性）
    # ------------------------------------------------------------
    def check_contradictions(self, text: str) -> float:
        """
        简单检测是否存在自相矛盾的句子。
        Simple contradiction detection.
        """
        contradictions = [
            ("increase", "decrease"),
            ("rise", "fall"),
            ("support", "oppose"),
            ("approve", "reject"),
        ]

        penalty = 0
        for a, b in contradictions:
            if a in text.lower() and b in text.lower():
                penalty += 1

        score = 1.0 - min(1.0, penalty * 0.2)
        return score

    # ------------------------------------------------------------
    # Step 4: 综合评分
    # ------------------------------------------------------------
    def score(self, result: Dict[str, Any], required_fields: List[str], expected_keywords: List[str]) -> float:
        """
        综合评分：结构 + 风格 + 事实性
        Composite score.
        """

        # 结构化评分
        structure_score = self.check_structure(result, required_fields)

        # 文本提取
        text = ""
        if isinstance(result, dict):
            if "raw" in result:
                text = result["raw"]
            elif "text" in result:
                text = result["text"]
            else:
                text = str(result)

        # 风格评分
        style_score = self.check_style(text, expected_keywords)

        # 自相矛盾评分
        contradiction_score = self.check_contradictions(text)

        # 综合评分
        final_score = (structure_score * 0.4) + (style_score * 0.3) + (contradiction_score * 0.3)

        return max(0.0, min(1.0, final_score))
