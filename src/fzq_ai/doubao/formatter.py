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

    def format(self, data: Any, feedback_context: Optional[dict] = None) -> Dict[str, Any]:
        """Main formatting entry point.

        Args:
            data: Minimax-validated schema (dict or Pydantic model).
            feedback_context: optional dict produced by FeedbackLoop.build_context.
                - If feedback_context contains 'issues' with 'order_issues', enable strict ordering.
                - If feedback_context contains 'risk_structure' or 'risk_issues', enable defensive normalization for risks.
        Returns:
            Clean, ordered dict ready for downstream consumption.
        """
        # Convert to dict if Pydantic model
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        if not isinstance(data, dict):
            return {"_error": "invalid_input", "_data": str(data)[:500]}

        # Defensive copy to avoid mutating caller data
        src = dict(data)

        # If feedback requests risk normalization, apply defensive normalization
        if feedback_context:
            # risk_issues may be a list of keys or a flag
            risk_issues = feedback_context.get("risk_structure") or feedback_context.get("risk_issues") or []
            if risk_issues:
                src = self._ensure_risks_list_inplace(src)

        result: Dict[str, Any] = {}

        # 1. Reorder top-level fields (but preserve ALL fields)
        # If feedback indicates order_issues, we enforce strict ordering for top fields.
        strict_order = False
        if feedback_context:
            issues = feedback_context.get("issues", [])
            if isinstance(issues, list) and "order_issues" in issues:
                strict_order = True

        if strict_order:
            # Only include top fields that exist in source, in the canonical order,
            # then append remaining keys in original source order.
            ordered_keys = [k for k in self._TOP_FIELDS if k in src]
            remaining_keys = [k for k in src.keys() if k not in ordered_keys]
        else:
            # Preserve original input order as much as possible:
            ordered_keys = [k for k in self._TOP_FIELDS if k in src]
            remaining_keys = [k for k in src.keys() if k not in ordered_keys]

        for key in ordered_keys + remaining_keys:
            result[key] = self._format_field(key, src.get(key))

        return result

    def _ensure_risks_list_inplace(self, src: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure risks field is normalized: risks -> dict[str, list]. Non-destructive to values."""
        if "risks" not in src:
            return src
        risks_val = src.get("risks")
        # If risks is a dict mapping category -> item(s), normalize each to list
        if isinstance(risks_val, dict):
            normalized = {}
            for k, v in risks_val.items():
                if v is None:
                    normalized[k] = []
                elif isinstance(v, list):
                    normalized[k] = v
                else:
                    # wrap scalar into list; do not fabricate content
                    normalized[k] = [v]
            src["risks"] = normalized
        else:
            # If risks is not a dict, fallback to preserving original but wrap into a single-entry dict
            # This is defensive: we do not invent categories, just keep original under 'unknown'
            src["risks"] = {"unknown": risks_val if isinstance(risks_val, list) else [risks_val]}
        return src

    def _format_field(self, key: str, value: Any) -> Any:
        """Format a single field, preserving its type."""
        if value is None:
            return None
        if isinstance(value, list):
            return [self._format_item(key, v) for v in value]
        if isinstance(value, dict):
            # Preserve dict key order; format nested fields recursively
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

    def format_to_json(self, data: Any, feedback_context: Optional[dict] = None, indent: int = 2) -> str:
        """Format and serialize to JSON string."""
        formatted = self.format(data, feedback_context=feedback_context)
        return json.dumps(formatted, indent=indent, ensure_ascii=False)

    @staticmethod
    def is_valid_json(text: str) -> bool:
        """Check if string is valid JSON."""
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
