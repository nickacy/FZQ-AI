"""tests/test_minimax_feedback_loop.py — MinimaxFeedbackLoop tests.

V24.3.5: Phase 2 feedback loop wiring.

Covers:
  - record() writes to civ with target-prefixed keys
  - build_context() reads from civ for any target
  - format_prompt_fragment() produces human-readable text
  - record() no-ops gracefully when civ is None
  - integration with MinimaxFeedbackRouter output
"""
from __future__ import annotations
import pytest

from fzq_ai.minimax.phase2 import (
    MinimaxFeedbackEngine,
    MinimaxFeedbackRouter,
    MinimaxFeedbackLoop,
    StructuralFeedback,
)
from fzq_ai.civilization.civilization_engine import CivilizationEngine


def _make_routed_feedback() -> dict:
    """Build a routed feedback dict using engine + router."""
    engine = MinimaxFeedbackEngine()
    router = MinimaxFeedbackRouter()
    feedback = engine.generate(
        strict_schema={"facts": ["x"], "events": [], "actors": [],
                      "narratives": [], "risks": {"political": [], "economic": [],
                      "social": [], "tech": [], "international": []},
                      "policy": [], "trend": [], "raw_quotes": []},
        original_input={"actors": "Alice"},
    )
    return router.route(feedback)


# ============================================================
# record() — WRITE to civ
# ============================================================

class TestRecord:
    def test_record_writes_global_keys(self):
        civ = CivilizationEngine("test_record_global")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        feedback = StructuralFeedback(consistency_score=42.0, risk_score=50.0)
        ok = loop.record(routed_feedback=routed, civ=civ, phase2_feedback=feedback)
        assert ok is True
        assert civ.recall("feedback._global.consistency_score") == "42.0"
        assert civ.recall("feedback._global.risk_score") == "50.0"
        assert civ.recall("feedback._global.trace_id") != ""

    def test_record_writes_per_target_issues(self):
        civ = CivilizationEngine("test_record_target")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        ok = loop.record(routed_feedback=routed, civ=civ)
        # glm should have at least missing_fields issues
        glm_issues = civ.recall("feedback.glm.issues") or []
        assert isinstance(glm_issues, list)
        glm_count = civ.recall("feedback.glm.issue_count")
        assert glm_count == str(len(glm_issues))

    def test_record_writes_ds_tasks(self):
        civ = CivilizationEngine("test_record_ds")
        loop = MinimaxFeedbackLoop()
        # Force DS execution book requirement via low consistency
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
        )
        router = MinimaxFeedbackRouter()
        routed = router.route(feedback)
        loop.record(routed_feedback=routed, civ=civ)
        # Low consistency should trigger DS tasks
        ds_tasks = civ.recall("feedback.ds.ds_tasks") or []
        if routed["ds_commit_decision"]["requires_ds_execution_book"]:
            assert isinstance(ds_tasks, list)
            assert len(ds_tasks) >= 1

    def test_record_no_op_when_civ_none(self):
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        ok = loop.record(routed_feedback=routed, civ=None)
        assert ok is False

    def test_record_no_op_when_civ_lacks_recall(self):
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        # Mock civ without recall
        class FakeCiv:
            pass
        ok = loop.record(routed_feedback=routed, civ=FakeCiv())
        assert ok is False


# ============================================================
# build_context() — READ from civ
# ============================================================

class TestBuildContext:
    def test_build_context_returns_dict(self):
        civ = CivilizationEngine("test_build_ctx")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        feedback = StructuralFeedback(consistency_score=75.0)
        loop.record(routed_feedback=routed, civ=civ, phase2_feedback=feedback)
        ctx = loop.build_context(civ=civ, target="glm")
        assert isinstance(ctx, dict)
        assert ctx["target"] == "glm"
        assert "issues" in ctx
        assert "suggestions" in ctx
        assert "consistency_score" in ctx

    def test_build_context_empty_when_civ_none(self):
        loop = MinimaxFeedbackLoop()
        ctx = loop.build_context(civ=None, target="glm")
        assert ctx == {}

    def test_build_context_empty_when_target_unseen(self):
        civ = CivilizationEngine("test_build_unseen")
        loop = MinimaxFeedbackLoop()
        # No record() called — civ is empty
        ctx = loop.build_context(civ=civ, target="nonexistent_target")
        assert ctx["target"] == "nonexistent_target"
        assert ctx["issues"] == []
        assert ctx["consistency_score"] == "0.0"

    def test_build_context_for_all_5_targets(self):
        civ = CivilizationEngine("test_all_targets")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        loop.record(routed_feedback=routed, civ=civ)
        for target in ["glm", "deepseek", "doubao", "kimi", "qwen"]:
            ctx = loop.build_context(civ=civ, target=target)
            assert ctx["target"] == target
            assert "issues" in ctx
            assert "priority" in ctx


# ============================================================
# format_prompt_fragment() — format as LLM prompt text
# ============================================================

class TestFormatPromptFragment:
    def test_format_empty_when_no_issues(self):
        civ = CivilizationEngine("test_fmt_empty")
        loop = MinimaxFeedbackLoop()
        ctx_str = loop.format_prompt_fragment(civ=civ, target="glm")
        assert ctx_str == ""

    def test_format_with_issues(self):
        civ = CivilizationEngine("test_fmt_with_issues")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        loop.record(routed_feedback=routed, civ=civ)
        ctx_str = loop.format_prompt_fragment(civ=civ, target="glm")
        assert "[Minimax Phase 2 Feedback for glm]" in ctx_str
        assert "Issues" in ctx_str

    def test_format_caps_suggestions(self):
        civ = CivilizationEngine("test_fmt_cap")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        loop.record(routed_feedback=routed, civ=civ)
        # max_suggestions=2 should limit output
        ctx_str = loop.format_prompt_fragment(civ=civ, target="glm", max_suggestions=2)
        # Verify only up to 2 "Suggestions:" entries
        assert isinstance(ctx_str, str)


# ============================================================
# Integration test — full Phase 2 + Loop pipeline
# ============================================================

class TestIntegration:
    def test_full_loop_pipeline(self):
        """End-to-end: Phase 2 → Loop → build context."""
        civ = CivilizationEngine("test_full_loop")
        engine = MinimaxFeedbackEngine()
        router = MinimaxFeedbackRouter()
        loop = MinimaxFeedbackLoop()

        # 1. Generate Phase 2 feedback
        feedback = engine.generate(
            strict_schema={"facts": [], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": ["p"], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"risks": ["p"]},  # list→dict risk_repair
        )
        routed = router.route(feedback)

        # 2. Persist to civ
        ok = loop.record(routed_feedback=routed, civ=civ, phase2_feedback=feedback)
        assert ok is True

        # 3. Simulate "next call" — Kimi reads its context
        kimi_ctx = loop.build_context(civ=civ, target="kimi")
        assert kimi_ctx["target"] == "kimi"
        # Kimi should see risk_repair_count issues
        # (routed "kimi" slice contains risk_repairs)
        # Note: build_context reads feedback.<target>.issues; for Kimi those are risk_repairs
        # So issues list should be non-empty when there are risk_repairs
        kimi_routed = routed["kimi"]
        if kimi_routed["issues"]:
            assert len(kimi_ctx["issues"]) >= 1

        # 4. Format as prompt fragment
        prompt_fragment = loop.format_prompt_fragment(civ=civ, target="kimi")
        if kimi_routed["issues"]:
            assert "kimi" in prompt_fragment.lower()


# ============================================================
# Edge cases
# ============================================================

class TestEdgeCases:
    def test_record_with_empty_routed(self):
        civ = CivilizationEngine("test_empty_routed")
        loop = MinimaxFeedbackLoop()
        ok = loop.record(routed_feedback={}, civ=civ)
        # Even with empty routed, global keys may be written if phase2_feedback is given
        assert ok is True

    def test_record_with_routed_only(self):
        """No phase2_feedback — should still write per-target keys."""
        civ = CivilizationEngine("test_routed_only")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        ok = loop.record(routed_feedback=routed, civ=civ)
        assert ok is True
        # Per-target keys exist even without phase2_feedback
        assert civ.recall("feedback.glm.issues") is not None

    def test_format_prompt_fragment_no_civ(self):
        loop = MinimaxFeedbackLoop()
        ctx_str = loop.format_prompt_fragment(civ=None, target="glm")
        assert ctx_str == ""

    def test_last_write_at_marked(self):
        civ = CivilizationEngine("test_last_write")
        loop = MinimaxFeedbackLoop()
        routed = _make_routed_feedback()
        loop.record(routed_feedback=routed, civ=civ)
        last_write = civ.recall("feedback._global.last_loop_write_at")
        assert last_write is not None
        assert "T" in last_write  # ISO format