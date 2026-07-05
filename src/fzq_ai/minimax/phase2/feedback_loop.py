"""src/fzq_ai/minimax/phase2/feedback_loop.py

MinimaxFeedbackLoop — V24.3.5 Phase 2 闭环层.

Wires Phase 2 routed feedback INTO civilization memory so downstream
modules (GLM / Doubao / Kimi / Qwen / DeepSeek) can OPTIONALLY read it on
subsequent calls. This forms the structural closed-loop:

  Phase 2 → write to civ (key: feedback.<target>.*)
           ↓
  next call: GLMExtractor / DoubaoFormatter / KimiInterpreter / etc.
           ↓
  optionally read feedback.<target>.* from civ
           ↓
  inject into prompt / system message / decision logic

Design constraint:
  - Minimax NEVER modifies GLM/Doubao/Kimi/Qwen signatures
  - Loop is opt-in: each module decides whether to read feedback
  - Civ memory writes are best-effort (failures never break pipeline)

This module exposes two surfaces:
  1. MinimaxFeedbackLoop.record(routed_feedback, civ)
     — Persist routed feedback into civ with target-prefixed keys.
  2. MinimaxFeedbackLoop.build_context(civ, target)
     — Read target's accumulated feedback from civ, return context dict.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from .feedback_models import StructuralFeedback


logger = logging.getLogger(__name__)


# Key prefix conventions — readable by humans, greppable for tests
_FEEDBACK_PREFIX = "feedback"
# Per-target memory key suffixes
_TARGET_KEYS = {
    "glm": ["missing_count", "consistency_score", "suggestions"],
    "deepseek": ["type_repair_count", "risk_repair_count", "order_repair_count", "suggestions"],
    "doubao": ["type_repair_count", "order_repair_count", "suggestions"],
    "kimi": ["risk_repair_count", "risk_score", "consistency_score", "suggestions"],
    "qwen": ["consistency_score", "order_repair_count", "ds_tasks", "suggestions"],
    # ds (commit decision) is not stored — it's an action signal, not data
}


class MinimaxFeedbackLoop:
    """Persist Phase 2 routed feedback to civilization; build target contexts.

    Usage:
        loop = MinimaxFeedbackLoop()
        # 1. After Phase 2 routing, persist feedback
        loop.record(routed_feedback, civ=civ)
        # 2. Before next call to a target module, build context
        glm_ctx = loop.build_context(civ=civ, target="glm")
        # Pass glm_ctx to GLMExtractor.extract(user_input, feedback_context=glm_ctx)
    """

    def __init__(self) -> None:
        self.source = "minimax_phase2_feedback_loop"

    # ============================================================
    # WRITE: persist routed feedback into civ
    # ============================================================

    def record(
        self,
        routed_feedback: Dict[str, Any],
        civ: Any = None,
        phase2_feedback: Optional[StructuralFeedback] = None,
    ) -> bool:
        """Persist routed feedback into civ with target-prefixed keys.

        Args:
            routed_feedback: Output of MinimaxFeedbackRouter.route() (6 keys)
            civ: CivilizationEngine instance (None → no-op)
            phase2_feedback: Original StructuralFeedback (for global scores)

        Returns:
            True if write succeeded, False if civ missing / write failed.
        """
        if civ is None or not hasattr(civ, "remember"):
            return False

        try:
            # Global scores (all targets share these)
            if phase2_feedback is not None:
                civ.remember(f"{_FEEDBACK_PREFIX}._global.consistency_score",
                              str(phase2_feedback.consistency_score))
                civ.remember(f"{_FEEDBACK_PREFIX}._global.risk_score",
                              str(phase2_feedback.risk_score))
                civ.remember(f"{_FEEDBACK_PREFIX}._global.trace_id",
                              phase2_feedback.trace_id)
                civ.remember(f"{_FEEDBACK_PREFIX}._global.generated_at",
                              phase2_feedback.generated_at)
                civ.remember(f"{_FEEDBACK_PREFIX}._global.missing_fields",
                              phase2_feedback.missing_fields)
                civ.remember(f"{_FEEDBACK_PREFIX}._global.type_repairs",
                              phase2_feedback.type_repairs)
                civ.remember(f"{_FEEDBACK_PREFIX}._global.risk_repairs",
                              phase2_feedback.risk_repairs)

            # Per-target feedback
            for target, slice_data in routed_feedback.items():
                if target == "ds_commit_decision":
                    # Persist DS tasks list (action items for V25+)
                    if isinstance(slice_data, dict):
                        ds_tasks = slice_data.get("ds_tasks") or []
                        civ.remember(f"{_FEEDBACK_PREFIX}.ds.ds_tasks", ds_tasks)
                        civ.remember(f"{_FEEDBACK_PREFIX}.ds.requires_execution_book",
                                      str(slice_data.get("requires_ds_execution_book", False)))
                    continue

                if not isinstance(slice_data, dict):
                    continue

                target_name = slice_data.get("target", target)
                # Issues list
                issues = slice_data.get("issues") or []
                civ.remember(f"{_FEEDBACK_PREFIX}.{target_name}.issues", issues)
                civ.remember(f"{_FEEDBACK_PREFIX}.{target_name}.issue_count",
                              str(len(issues)))
                # Suggestions list
                suggestions = slice_data.get("suggestions") or []
                civ.remember(f"{_FEEDBACK_PREFIX}.{target_name}.suggestions", suggestions)
                # Priority + requires_action
                civ.remember(f"{_FEEDBACK_PREFIX}.{target_name}.priority",
                              slice_data.get("priority", "medium"))
                civ.remember(f"{_FEEDBACK_PREFIX}.{target_name}.requires_action",
                              str(slice_data.get("requires_action", False)))

            # Mark the loop's own write trace
            civ.remember(f"{_FEEDBACK_PREFIX}._global.last_loop_write_at",
                          _now_iso())
            return True
        except Exception as e:
            logger.warning("feedback loop write failed: %s", e)
            return False

    # ============================================================
    # READ: build target-specific context from civ
    # ============================================================

    def build_context(
        self,
        civ: Any = None,
        target: str = "glm",
    ) -> Dict[str, Any]:
        """Read accumulated feedback for `target` from civ.

        Returns a dict suitable for injection into a module's prompt/system message.
        Empty dict if civ missing / target has no feedback yet.

        Context shape:
          {
              "issues": [...],
              "issue_count": N,
              "suggestions": [...],
              "priority": "low|medium|high",
              "requires_action": bool,
              "consistency_score": float,
              "risk_score": float,
              "trace_id": "...",
              "last_write_at": "...",
          }
        """
        if civ is None or not hasattr(civ, "recall"):
            return {}

        context: Dict[str, Any] = {"target": target}
        try:
            # Target-specific
            context["issues"] = civ.recall(f"{_FEEDBACK_PREFIX}.{target}.issues") or []
            context["issue_count"] = civ.recall(f"{_FEEDBACK_PREFIX}.{target}.issue_count") or "0"
            context["suggestions"] = civ.recall(f"{_FEEDBACK_PREFIX}.{target}.suggestions") or []
            context["priority"] = civ.recall(f"{_FEEDBACK_PREFIX}.{target}.priority") or "medium"
            context["requires_action"] = civ.recall(f"{_FEEDBACK_PREFIX}.{target}.requires_action") or "False"

            # Global scores (shared)
            context["consistency_score"] = civ.recall(f"{_FEEDBACK_PREFIX}._global.consistency_score") or "0.0"
            context["risk_score"] = civ.recall(f"{_FEEDBACK_PREFIX}._global.risk_score") or "0.0"
            context["trace_id"] = civ.recall(f"{_FEEDBACK_PREFIX}._global.trace_id") or ""
            context["last_write_at"] = civ.recall(f"{_FEEDBACK_PREFIX}._global.last_loop_write_at") or ""
        except Exception as e:
            logger.warning("feedback loop read failed: %s", e)

        return context

    # ============================================================
    # Convenience: format context as prompt fragment
    # ============================================================

    def format_prompt_fragment(
        self,
        civ: Any = None,
        target: str = "glm",
        max_suggestions: int = 3,
    ) -> str:
        """Format civ feedback as a human-readable prompt fragment.

        Returns "" if no actionable feedback. Otherwise returns a string
        suitable for injection into a LLM system message or user prompt.
        """
        ctx = self.build_context(civ=civ, target=target)
        if not ctx or not ctx.get("issues"):
            return ""

        issues = ctx.get("issues") or []
        suggestions = (ctx.get("suggestions") or [])[:max_suggestions]

        lines = [
            f"[Minimax Phase 2 Feedback for {target}]",
            f"Issues found in previous runs ({len(issues)}):",
        ]
        for i, issue in enumerate(issues[:5], 1):  # cap at 5 issues for brevity
            lines.append(f"  {i}. {issue}")
        if suggestions:
            lines.append("Suggestions:")
            for i, s in enumerate(suggestions, 1):
                lines.append(f"  {i}. {s}")
        return "\n".join(lines)


def _now_iso() -> str:
    """ISO 8601 UTC timestamp (lazy import)."""
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat()