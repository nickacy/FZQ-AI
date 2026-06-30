# src/fzq_ai/agents/healing.py
# V21 — Self-Healing System（自愈系统）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Any, Dict, List
import json
import re

class HealingEngine:
    """
    ============================================================
    V21 — HealingEngine（自愈系统）
    ============================================================

    功能：
    - 修复模型输出格式错误
    - 修复 JSON 结构
    - 自动补全缺失字段
    - 自动结构化文本
    - 自动重构内容
    - 清理重复、乱码、异常输出

    ============================================================
    English Description
    ============================================================

    HealingEngine fixes malformed model outputs, reconstructs
    missing fields, cleans noise, and ensures structured results.
    """

    # ------------------------------------------------------------
    # Step 1: 修复 JSON 格式
    # ------------------------------------------------------------
    def fix_json(self, text: str) -> Dict[str, Any]:
        """
        尝试将模型输出修复为 JSON。
        Try to repair malformed JSON output.
        """
        try:
            return json.loads(text)
        except Exception:
            # 尝试修复常见错误
            text = text.replace("\n", " ")
            text = re.sub(r",\s*}", "}", text)
            text = re.sub(r",\s*]", "]", text)

            try:
                return json.loads(text)
            except Exception:
                return {"raw_text": text, "error": "json_repair_failed"}

    # ------------------------------------------------------------
    # Step 2: 自动补全字段
    # ------------------------------------------------------------
    def fill_missing_fields(self, data: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        """
        自动补齐缺失字段。
        Auto-fill missing fields.
        """
        for field in required:
            if field not in data:
                data[field] = None
        return data

    # ------------------------------------------------------------
    # Step 3: 清理异常输出
    # ------------------------------------------------------------
    def clean_text(self, text: str) -> str:
        """
        清理乱码、重复、异常字符。
        Clean noise, duplicates, and malformed characters.
        """
        text = re.sub(r"[^\x00-\x7F]+", " ", text)  # 移除非 ASCII 乱码
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ------------------------------------------------------------
    # Step 4: 自动结构化文本
    # ------------------------------------------------------------
    def structure_text(self, text: str) -> Dict[str, Any]:
        """
        将文本自动结构化为段落、要点。
        Auto-structure text into paragraphs and bullet points.
        """
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        bullets = [p for p in paragraphs if p.startswith("-") or p.startswith("•")]

        return {
            "paragraphs": paragraphs,
            "bullets": bullets,
            "raw": text
        }

    # ------------------------------------------------------------
    # Step 5: 自动重构内容
    # ------------------------------------------------------------
    def reconstruct(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        当输出质量不足时自动重构内容。
        Auto-reconstruct content when quality is low.
        """
        if "raw_text" in data:
            cleaned = self.clean_text(data["raw_text"])
            structured = self.structure_text(cleaned)
            return structured

        return data

    # ------------------------------------------------------------
    # Step 6: 总入口
    # ------------------------------------------------------------
    def heal(self, result: Any, required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        自愈入口：格式修复 → 字段补全 → 清理 → 重构
        Healing entry point.
        """
        # Step 1: JSON 修复
        if isinstance(result, str):
            result = self.fix_json(result)

        # Step 2: 字段补全
        if required_fields:
            result = self.fill_missing_fields(result, required_fields)

        # Step 3: 重构内容
        result = self.reconstruct(result)

        return result
