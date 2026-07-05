"""src/fzq_ai/minimax/phase2/feedback_router.py

MinimaxFeedbackRouter — routes Phase 2 feedback to 6 downstream targets.

Targets:
  glm      — upstream (extraction layer)
  deepseek — upstream (structuring layer)
  doubao   — downstream (formatter)
  kimi     — downstream (interpreter)
  qwen     — downstream (engineering governance)
  ds       — Copilot commit decision (Minimax can self-commit or needs DS execution book)

Each slice is a RoutedFeedback (subset of StructuralFeedback relevant to target).
"""
from __future__ import annotations
from typing import Any, Dict, List

from .feedback_models import (
    StructuralFeedback,
    RoutedFeedback,
    CommitDecision,
)


# Keywords used to filter target-specific suggestions (R5: structural prose only)
_TARGET_KEYWORDS = {
    "glm": ["missing", "prompt"],
    "deepseek": ["missing", "type", "schema", "category", "structure"],
    "doubao": ["format", "sort", "list", "豆包"],
    "kimi": ["interpret", "merge", "split", "explain", "Kimi"],
    "qwen": ["engineering", "schema upgrade", "refactor", "Qwen", "governance"],
}


class MinimaxFeedbackRouter:
    """Route Phase 2 feedback to 6 targets.

    Usage:
        router = MinimaxFeedbackRouter()
        routed = router.route(feedback)
        # routed["glm"]["issues"]
        # routed["doubao"]["suggestions"]
        # routed["ds_commit_decision"]["minimax_can_commit"]
    """

    def route(self, feedback: StructuralFeedback) -> Dict[str, Any]:
        """Route feedback to all 6 targets.

        Returns dict with 6 keys:
          glm, deepseek, doubao, kimi, qwen (each a RoutedFeedback-ish dict)
          ds_commit_decision (CommitDecision)
        """
        return {
            "glm": self._glm_feedback(feedback),
            "deepseek": self._deepseek_feedback(feedback),
            "doubao": self._doubao_feedback(feedback),
            "kimi": self._kimi_feedback(feedback),
            "qwen": self._qwen_feedback(feedback),
            "ds_commit_decision": self._ds_commit_decision(feedback),
        }

    # ============================================================
    # Upstream targets
    # ============================================================

    def _glm_feedback(self, f: StructuralFeedback) -> Dict[str, Any]:
        """GLM (extraction layer) cares about missing fields + content extraction hints."""
        issues = list(f.missing_fields)
        # GLM-specific suggestions
        suggestions = self._filter_suggestions(f.suggestions, "glm")
        priority = self._priority_from_score(f.consistency_score, threshold_low=30.0)
        return RoutedFeedback(
            target="glm",
            issues=issues,
            suggestions=suggestions,
            priority=priority,
            requires_action=bool(issues),
        ).model_dump()

    def _deepseek_feedback(self, f: StructuralFeedback) -> Dict[str, Any]:
        """DeepSeek (structuring layer) cares about type/risk/order repairs."""
        issues = list(f.type_repairs) + list(f.risk_repairs) + list(f.order_repairs)
        suggestions = self._filter_suggestions(f.suggestions, "deepseek")
        priority = self._priority_from_score(
            max(f.consistency_score, f.risk_score), threshold_low=50.0
        )
        return RoutedFeedback(
            target="deepseek",
            issues=issues,
            suggestions=suggestions,
            priority=priority,
            requires_action=bool(issues),
        ).model_dump()

    # ============================================================
    # Downstream targets
    # ============================================================

    def _doubao_feedback(self, f: StructuralFeedback) -> Dict[str, Any]:
        """豆包 (formatter) cares about list/sort/format consistency."""
        # Doubao cares about type repairs (list shapes) and order repairs
        issues = [t for t in f.type_repairs if "list" in t or "str" in t]
        issues += list(f.order_repairs)
        suggestions = self._filter_suggestions(f.suggestions, "doubao")
        priority = "medium" if issues else "low"
        return RoutedFeedback(
            target="doubao",
            issues=issues,
            suggestions=suggestions,
            priority=priority,
            requires_action=bool(issues),
        ).model_dump()

    def _kimi_feedback(self, f: StructuralFeedback) -> Dict[str, Any]:
        """Kimi (interpreter) cares about risk structure + completeness."""
        issues = list(f.risk_repairs)
        # Add consistency hint if low
        if f.consistency_score < 50.0:
            issues.append(f"low_consistency:{f.consistency_score}")
        suggestions = self._filter_suggestions(f.suggestions, "kimi")
        priority = self._priority_from_score(f.risk_score, threshold_low=40.0)
        return RoutedFeedback(
            target="kimi",
            issues=issues,
            suggestions=suggestions,
            priority=priority,
            requires_action=bool(issues),
        ).model_dump()

    def _qwen_feedback(self, f: StructuralFeedback) -> Dict[str, Any]:
        """Qwen (engineering governance) cares about schema + refactor signals."""
        # Qwen only cares if many issues suggest schema work
        issues = list(f.order_repairs)
        # Only flag Qwen if schema-upgrade signal
        if f.consistency_score < 30.0:
            issues.append("schema_upgrade_signal:consistency_too_low")
        suggestions = self._filter_suggestions(f.suggestions, "qwen")
        priority = "high" if f.consistency_score < 30.0 else "low"
        return RoutedFeedback(
            target="qwen",
            issues=issues,
            suggestions=suggestions,
            priority=priority,
            requires_action=bool(issues),
        ).model_dump()

    # ============================================================
    # Copilot commit decision
    # ============================================================

    def _ds_commit_decision(self, f: StructuralFeedback) -> Dict[str, Any]:
        """Phase 2 outputs are structural — Minimax can self-commit.

        BUT: if feedback signals that code/schema/pipeline work is needed,
        generate a DS execution book task list.
        """
        ds_tasks: List[str] = []
        requires_ds_book = False

        # Detect "code-layer changes needed"
        if f.consistency_score < 30.0:
            # Very low consistency suggests schema/template rework
            ds_tasks.append("Review upstream prompts (GLM/DeepSeek) for missing field requirements")
            ds_tasks.append("Consider extending StrictSchema if new fields emerge")
            requires_ds_book = True
        if f.risk_score < 40.0:
            ds_tasks.append("Update DeepSeek prompt to require all 5 risk categories")
            requires_ds_book = True
        if any("schema" in s.lower() for s in f.suggestions):
            ds_tasks.append("Review Schema definitions for structural improvements")
            requires_ds_book = True

        decision = CommitDecision(
            minimax_can_commit=True,  # Phase 2 outputs are always structural
            reason=(
                "Phase 2 outputs are structural feedback only (R1-R6 compliance). "
                "Feedback file + scores can be self-committed. "
                + (
                    "However, downstream code/schema/prompt changes require DS execution book."
                    if requires_ds_book else
                    "No code/schema/prompt changes required."
                )
            ),
            requires_ds_execution_book=requires_ds_book,
            ds_tasks=ds_tasks,
        )
        return decision.model_dump()

    # ============================================================
    # Helpers
    # ============================================================

    def _filter_suggestions(self, suggestions: List[str], target: str) -> List[str]:
        """Filter suggestions by target-specific keywords."""
        keywords = _TARGET_KEYWORDS.get(target, [])
        if not keywords:
            return []
        return [s for s in suggestions if any(kw.lower() in s.lower() for kw in keywords)]

    def _priority_from_score(self, score: float, threshold_low: float) -> str:
        """Map score to priority label."""
        if score >= 80.0:
            return "low"
        if score >= threshold_low:
            return "medium"
        return "high"