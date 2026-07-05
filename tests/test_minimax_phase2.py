"""tests/test_minimax_phase2.py — Minimax Phase 2 structural feedback tests.

Covers:
  - StructuralFeedback model validation (3)
  - MinimaxFeedbackEngine (10)
  - MinimaxFeedbackRouter (6)
  - Commit Decision (1)
  - Mandatory Rules R1/R6 (2)

Total: 22 tests.
"""
from __future__ import annotations
import json
import pytest

from fzq_ai.minimax.phase2 import (
    StructuralFeedback,
    MinimaxFeedbackEngine,
    MinimaxFeedbackRouter,
)


# ============================================================
# (1) StructuralFeedback model — 3 tests
# ============================================================

class TestStructuralFeedbackModel:
    def test_model_validates_with_defaults(self):
        f = StructuralFeedback()
        assert f.source == "minimax_phase2"
        assert f.consistency_score == 0.0
        assert f.risk_score == 0.0
        assert f.missing_fields == []
        assert f.trace_id != ""
        assert f.generated_at != ""

    def test_target_models_default(self):
        f = StructuralFeedback()
        assert "glm" in f.target_models
        assert "deepseek" in f.target_models
        assert "doubao" in f.target_models
        assert "kimi" in f.target_models
        assert "qwen" in f.target_models

    def test_score_range_validation(self):
        # Valid scores
        for v in [0.0, 50.5, 100.0]:
            f = StructuralFeedback(consistency_score=v, risk_score=v)
            assert f.consistency_score == v
        # Invalid scores
        with pytest.raises(ValueError):
            StructuralFeedback(consistency_score=-1.0)
        with pytest.raises(ValueError):
            StructuralFeedback(consistency_score=101.0)
        with pytest.raises(ValueError):
            StructuralFeedback(risk_score=200.0)


# ============================================================
# (2) MinimaxFeedbackEngine — 10 tests
# ============================================================

class TestMinimaxFeedbackEngine:
    def test_missing_fields_detected(self):
        engine = MinimaxFeedbackEngine()
        f = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"facts": ["x"]},  # only facts in original
        )
        # All other top-level fields should be reported as missing
        assert "events" in f.missing_fields
        assert "actors" in f.missing_fields
        assert "narratives" in f.missing_fields
        assert "policy" in f.missing_fields
        assert "trend" in f.missing_fields
        assert "raw_quotes" in f.missing_fields

    def test_type_repairs_str_to_list(self):
        engine = MinimaxFeedbackEngine()
        f = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "John Doe"},  # str instead of list
        )
        assert any("actors" in r and "str" in r for r in f.type_repairs)

    def test_risk_repairs_list_to_dict(self):
        engine = MinimaxFeedbackEngine()
        f = engine.generate(
            strict_schema={"facts": [], "events": [], "actors": [], "narratives": [],
                          "risks": {"political": ["r1"], "economic": [], "social": [],
                          "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"risks": ["r1"]},  # list instead of dict
        )
        assert any("risks" in r and "list" in r for r in f.risk_repairs)

    def test_order_repairs_detected(self):
        engine = MinimaxFeedbackEngine()
        # Pass keys in non-canonical order
        strict = {"raw_quotes": [], "trend": [], "policy": [], "risks": {
            "international": [], "tech": [], "social": [], "economic": [], "political": []
        }, "narratives": [], "actors": [], "events": [], "facts": []}
        f = engine.generate(strict_schema=strict)
        assert len(f.order_repairs) >= 1
        assert any("order" in r.lower() for r in f.order_repairs)

    def test_consistency_score_empty_input(self):
        engine = MinimaxFeedbackEngine()
        # Empty strict schema (all lists empty)
        strict = {"facts": [], "events": [], "actors": [], "narratives": [],
                  "risks": {"political": [], "economic": [], "social": [],
                           "tech": [], "international": []},
                  "policy": [], "trend": [], "raw_quotes": []}
        f = engine.generate(strict_schema=strict)
        assert f.consistency_score == 0.0

    def test_consistency_score_full_input(self):
        engine = MinimaxFeedbackEngine()
        # All 13 fields populated
        strict = {"facts": ["x"], "events": ["y"], "actors": ["z"],
                  "narratives": ["n"], "risks": {"political": ["p"], "economic": ["e"],
                  "social": ["s"], "tech": ["t"], "international": ["i"]},
                  "policy": ["po"], "trend": ["tr"], "raw_quotes": ["q"]}
        f = engine.generate(strict_schema=strict)
        assert f.consistency_score == 100.0

    def test_risk_score_empty(self):
        engine = MinimaxFeedbackEngine()
        strict = {"facts": [], "events": [], "actors": [], "narratives": [],
                  "risks": {"political": [], "economic": [], "social": [],
                           "tech": [], "international": []},
                  "policy": [], "trend": [], "raw_quotes": []}
        f = engine.generate(strict_schema=strict)
        assert f.risk_score == 0.0

    def test_risk_score_full(self):
        engine = MinimaxFeedbackEngine()
        strict = {"facts": [], "events": [], "actors": [], "narratives": [],
                  "risks": {"political": ["p"], "economic": ["e"],
                           "social": ["s"], "tech": ["t"], "international": ["i"]},
                  "policy": [], "trend": [], "raw_quotes": []}
        f = engine.generate(strict_schema=strict)
        assert f.risk_score == 100.0

    def test_suggestions_generated(self):
        engine = MinimaxFeedbackEngine()
        f = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "Alice"},
        )
        assert len(f.suggestions) >= 1
        # Suggestions must be structural prose (no code markers)
        for s in f.suggestions:
            assert "def " not in s
            assert "class " not in s
            assert "import " not in s

    def test_phase2_does_not_modify_input(self):
        """R2/R3/R4: engine never mutates strict_schema or original_input."""
        engine = MinimaxFeedbackEngine()
        strict = {"facts": ["x"], "events": [], "actors": [], "narratives": [],
                  "risks": {"political": [], "economic": [], "social": [],
                           "tech": [], "international": []},
                  "policy": [], "trend": [], "raw_quotes": []}
        original = {"actors": "Alice"}
        strict_copy = dict(strict)
        original_copy = dict(original)
        engine.generate(strict_schema=strict, original_input=original)
        assert strict == strict_copy
        assert original == original_copy


# ============================================================
# (3) MinimaxFeedbackRouter — 6 tests
# ============================================================

class TestMinimaxFeedbackRouter:
    def test_route_returns_6_targets(self):
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "Alice"},
        )
        routed = router.route(feedback)
        assert set(routed.keys()) == {"glm", "deepseek", "doubao", "kimi", "qwen", "ds_commit_decision"}

    def test_glm_feedback_includes_missing_fields(self):
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"facts": ["x"]},  # many missing
        )
        routed = router.route(feedback)
        glm = routed["glm"]
        assert glm["target"] == "glm"
        assert len(glm["issues"]) >= 1
        assert glm["requires_action"] is True

    def test_deepseek_feedback_includes_structural_issues(self):
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": [], "events": [], "actors": ["Alice"],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "Alice"},  # type repair needed
        )
        routed = router.route(feedback)
        ds = routed["deepseek"]
        assert ds["target"] == "deepseek"
        # Should include type_repairs since actors was str
        assert any("actors" in i for i in ds["issues"])

    def test_doubao_feedback_focuses_on_formatting(self):
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "Alice"},  # str→list (format issue)
        )
        routed = router.route(feedback)
        doubao = routed["doubao"]
        assert doubao["target"] == "doubao"
        # Doubao gets list/str related issues
        assert isinstance(doubao["issues"], list)

    def test_kimi_feedback_focuses_on_interpretation(self):
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": [], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": ["r"], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"risks": ["r"]},  # list, missing 4 of 5 categories
        )
        routed = router.route(feedback)
        kimi = routed["kimi"]
        assert kimi["target"] == "kimi"
        assert isinstance(kimi["issues"], list)

    def test_qwen_feedback_focuses_on_engineering(self):
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        # Force low consistency to trigger Qwen signal
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
        )
        routed = router.route(feedback)
        qwen = routed["qwen"]
        assert qwen["target"] == "qwen"
        assert qwen["priority"] == "high"  # low consistency → high priority


# ============================================================
# (4) Commit Decision — 1 test
# ============================================================

class TestCommitDecision:
    def test_phase2_can_self_commit(self):
        """Phase 2 outputs are structural — Minimax can self-commit by default."""
        router = MinimaxFeedbackRouter()
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
        )
        routed = router.route(feedback)
        decision = routed["ds_commit_decision"]
        assert decision["minimax_can_commit"] is True
        assert "structural" in decision["reason"].lower()


# ============================================================
# (5) Mandatory Rules R1/R6 — 2 tests
# ============================================================

class TestMandatoryRules:
    def test_r1_no_code_in_suggestions(self):
        """R1: Suggestions must never contain code (def/class/import)."""
        engine = MinimaxFeedbackEngine()
        # Provide chaotic input to maximize suggestions
        f = engine.generate(
            strict_schema={"facts": [], "events": [], "actors": [],
                          "narratives": [], "risks": {"political": [], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "Alice", "events": {"k": "v"},
                          "risks": ["r"], "unknown_field": "x"},
        )
        for s in f.suggestions:
            assert "def " not in s, f"Found code in suggestion: {s}"
            assert "class " not in s, f"Found code in suggestion: {s}"
            assert "import " not in s, f"Found code in suggestion: {s}"
            assert "lambda " not in s, f"Found code in suggestion: {s}"

    def test_r6_output_is_json_serializable(self):
        """R6: All Phase 2 outputs must be JSON-serializable."""
        engine = MinimaxFeedbackEngine()
        router = MinimaxFeedbackRouter()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], "actors": ["y"],
                          "narratives": [], "risks": {"political": ["p"], "economic": [],
                          "social": [], "tech": [], "international": []},
                          "policy": [], "trend": [], "raw_quotes": []},
            original_input={"actors": "y"},
        )
        routed = router.route(feedback)
        # feedback.model_dump() is JSON-safe
        feedback_json = json.dumps(feedback.model_dump(), ensure_ascii=False)
        assert isinstance(feedback_json, str)
        # routed dict is JSON-safe
        routed_json = json.dumps(routed, ensure_ascii=False, default=str)
        assert isinstance(routed_json, str)
        # Round-trip
        reparsed = json.loads(feedback_json)
        assert reparsed["consistency_score"] == feedback.consistency_score