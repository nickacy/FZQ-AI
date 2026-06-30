# src/fzq_ai/agents/healing.py
# V21 — Self-Healing System（自愈系统）
# 修复版：补全 Optional 导入，统一类型注解

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import re


class HealingEngine:
    """
    V21 — HealingEngine（自愈系统）
    """

    def fix_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except Exception:
            text = text.replace("\n", " ")
            text = re.sub(r",\s*}", "}", text)
            text = re.sub(r",\s*]", "]", text)
            try:
                return json.loads(text)
            except Exception:
                return {"raw_text": text, "error": "json_repair_failed"}

    def fill_missing_fields(self, data: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        for field in required:
            if field not in data:
                data[field] = None
        return data

    def clean_text(self, text: str) -> str:
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def structure_text(self, text: str) -> Dict[str, Any]:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        bullets = [p for p in paragraphs if p.startswith("-") or p.startswith("•")]
        return {
            "paragraphs": paragraphs,
            "bullets": bullets,
            "raw": text,
        }

    def reconstruct(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if "raw_text" in data:
            cleaned = self.clean_text(data["raw_text"])
            structured = self.structure_text(cleaned)
            return structured
        return data

    def heal(self, result: Any, required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        if isinstance(result, str):
            result = self.fix_json(result)
        if required_fields:
            result = self.fill_missing_fields(result, required_fields)
        result = self.reconstruct(result)
        return result
