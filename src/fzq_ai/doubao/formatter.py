"""Doubao Formatter — Formatting layer for FZQ-AI pipeline.

Pipeline: GLM → DeepSeek → Minimax → Doubao(Format) → Kimi → Qwen

Rules (enforced):
- R1: No inference — never add facts
- R2: No supplementation — never fill missing fields
- R3: No invention — never create content
- R4: No structural change — preserve field names and order
- R5: Preserve field order — output fields in input order
- R6: Output must be valid JSON

Doubao is the FORMATTING layer: it takes the validated Minimax schema and
produces clean, well-structured JSON suitable for document generation (Kimi)
and engineering governance (Qwen Coder).
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional


class DoubaoFormatter:
    """Format validated Minimax schema into clean, consistent JSON.

    Does NOT infer, supplement, or modify semantic content.
    """

    # ── Field ordering conventions ──
    _TOP_FIELDS: list[str] = [
        "facts", "events", "actors", "narratives", "risks",
        "policy", "trend", "raw_quotes", "metadata", "timestamp",
    ]

    def format(self, data: Any) -> Dict[str, Any]:
        """Main formatting entry point.

        Args:
            data: Minimax-validated schema (dict or Pydantic model).

        Returns:
            Clean, ordered dict ready for downstream consumption.
        """
        # Convert to dict if Pydantic model
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        if not isinstance(data, dict):
            return {"_error": "invalid_input", "_data": str(data)[:500]}

        result: Dict[str, Any] = {}

        # 1. Reorder top-level fields (but preserve ALL fields)
        ordered_keys = [k for k in self._TOP_FIELDS if k in data]
        remaining_keys = [k for k in data if k not in ordered_keys]

        for key in ordered_keys + remaining_keys:
            result[key] = self._format_field(key, data[key])

        return result

    def _format_field(self, key: str, value: Any) -> Any:
        """Format a single field, preserving its type."""
        if value is None:
            return None
        if isinstance(value, list):
            return [self._format_item(key, v) for v in value]
        if isinstance(value, dict):
            return {k: self._format_field(k, v) for k, v in value.items()}
        if isinstance(value, (int, float, bool, str)):
            return value
        if hasattr(value, "model_dump"):
            return self._format_field(key, value.model_dump())
        return str(value)[:1000]

    def _format_item(self, parent_key: str, item: Any) -> Any:
        """Format a list item."""
        if isinstance(item, dict):
            return {k: self._format_field(k, v) for k, v in item.items()}
        if hasattr(item, "model_dump"):
            return self._format_field(parent_key, item.model_dump())
        if isinstance(item, (int, float, bool, str)):
            return item
        return str(item)[:1000]

    def format_to_json(self, data: Any, indent: int = 2) -> str:
        """Format and serialize to JSON string."""
        formatted = self.format(data)
        return json.dumps(formatted, indent=indent, ensure_ascii=False)

    @staticmethod
    def is_valid_json(text: str) -> bool:
        """Check if string is valid JSON."""
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
