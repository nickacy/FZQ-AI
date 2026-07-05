"""Minimax Phase 2 FeedbackLoop — read-side for pipeline module consumption.

Writes (by Minimax): civ.remember("feedback_*", ...)
Reads (by pipeline modules): FeedbackLoop.build_context(civ=civ, target="glm")

civ key convention:
  feedback_glm_priority, feedback_glm_issues
  feedback_doubao_order_issues, feedback_doubao_issues
  feedback_kimi_requires_action, feedback_kimi_issues
  feedback_qwen_schema_risks, feedback_qwen_issues
"""

from __future__ import annotations
from typing import Any, Dict, Optional


class FeedbackLoop:
    """Reads civilization feedback storage and builds target-specific context dicts."""

    CIV_KEY_MAP: dict[str, list[str]] = {
        "glm": ["feedback_glm_priority", "feedback_glm_issues"],
        "doubao": ["feedback_doubao_order_issues", "feedback_doubao_issues"],
        "kimi": ["feedback_kimi_requires_action", "feedback_kimi_issues"],
        "qwen": ["feedback_qwen_schema_risks", "feedback_qwen_issues"],
    }

    TARGET_FIELDS: dict[str, list[str]] = {
        "glm": ["priority", "issues"],
        "doubao": ["order_issues", "issues"],
        "kimi": ["requires_action", "issues"],
        "qwen": ["schema_risks", "issues"],
    }

    @classmethod
    def build_context(cls, civ: Optional[Any] = None, target: str = "") -> Optional[Dict[str, Any]]:
        """Build a feedback context dict for a target module from civilization memory.

        Args:
            civ: CivilizationEngine instance (or any object with .recall()).
            target: One of "glm", "doubao", "kimi", "qwen".

        Returns:
            Dict with target-specific feedback fields, or None if no civ/feedback.
        """
        if civ is None or not hasattr(civ, "recall"):
            return None

        keys = cls.CIV_KEY_MAP.get(target, [])
        fields = cls.TARGET_FIELDS.get(target, [])

        context: Dict[str, Any] = {}
        has_data = False

        for i, key in enumerate(keys):
            value = civ.recall(key)
            if value is not None:
                context[fields[i]] = value
                has_data = True

        return context if has_data else None


loop = FeedbackLoop()
