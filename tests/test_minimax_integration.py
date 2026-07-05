"""tests/test_minimax_integration.py — Minimax integration with zh_tasks pipelines.

Verifies that when a ZhStructuredPipeline runs, the result includes a
`minimax` sub-dict with:
  - valid: bool (always True for well-formed pipeline results)
  - strict: dict (StrictSchema.model_dump() with 13 fields)
  - errors: list[str] (empty on success)

Covers both happy path (LLM returns valid JSON) and error paths
(JSON parse fail / schema validation fail / LLM exception).
"""
from __future__ import annotations
import json
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fzq_ai.pipelines.zh_policy_brief_pipeline import ZhPolicyBriefPipeline
from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline
from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultisourceMergePipeline


ALL_PIPELINES = [
    (ZhPolicyBriefPipeline, "zh_policy_brief"),
    (ZhRiskScanPipeline, "zh_risk_scan"),
    (ZhOpinionLandscapePipeline, "zh_opinion_landscape"),
    (ZhMultisourceMergePipeline, "zh_multisource_merge"),
]


VALID_POLICY_BRIEF_JSON = json.dumps({
    "task_type": "zh_policy_brief",
    "summary": "测试摘要",
    "key_points": [{"point": "要点1", "category": "目标", "evidence_span": "证据"}],
    "affected_entities": [{"entity": "实体A", "role": "执行方", "impact": "正面"}],
    "timeline": [],
    "quantitative_targets": [{"metric": "m", "value": "1", "deadline": "2025"}],
    "risk_flags": [],
    "confidence": 0.85,
}, ensure_ascii=False)


def _patch_call_llm(task_type, return_text=None):
    """Patch call_llm in _zh_pipeline to return a fixed string."""
    text = return_text if return_text is not None else VALID_POLICY_BRIEF_JSON
    return patch("fzq_ai.pipelines._zh_pipeline.call_llm", return_value=text)


# ============================================================
# Happy path: minimax sub-dict present + valid=True + strict has 13 fields
# ============================================================

class TestMinimaxHappyPath:
    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    @pytest.mark.asyncio
    async def test_minimax_subdict_present(self, cls, task_type):
        p = cls()
        with _patch_call_llm(task_type):
            result = await p.run(event_topic="测试话题")
        # Minimax sub-dict must be present
        assert "minimax" in result, "minimax sub-dict missing from result"
        m = result["minimax"]
        assert isinstance(m, dict)
        assert "valid" in m
        assert "strict" in m
        assert "errors" in m

    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    @pytest.mark.asyncio
    async def test_minimax_valid_true_on_happy_path(self, cls, task_type):
        p = cls()
        with _patch_call_llm(task_type):
            result = await p.run(event_topic="测试话题")
        assert result["minimax"]["valid"] is True
        assert result["minimax"]["errors"] == []

    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    @pytest.mark.asyncio
    async def test_minimax_strict_has_13_fields(self, cls, task_type):
        """StrictSchema dump must have all 8 top-level + 5 nested risks fields."""
        p = cls()
        with _patch_call_llm(task_type):
            result = await p.run(event_topic="x")
        strict = result["minimax"]["strict"]
        assert strict is not None
        # 8 top-level
        for field in ["facts", "events", "actors", "narratives",
                      "risks", "policy", "trend", "raw_quotes"]:
            assert field in strict, f"Missing top-level field: {field}"
        # 5 nested risks
        for field in ["political", "economic", "social", "tech", "international"]:
            assert field in strict["risks"], f"Missing risk sub-field: {field}"

    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    @pytest.mark.asyncio
    async def test_minimax_strict_all_lists(self, cls, task_type):
        """All StrictSchema list fields must be List[str] (R4 enforced)."""
        p = cls()
        with _patch_call_llm(task_type):
            result = await p.run(event_topic="x")
        strict = result["minimax"]["strict"]
        for field in ["facts", "events", "actors", "narratives",
                      "policy", "trend", "raw_quotes"]:
            assert isinstance(strict[field], list), f"{field} not a list"
        for field in ["political", "economic", "social", "tech", "international"]:
            assert isinstance(strict["risks"][field], list), f"risks.{field} not a list"


# ============================================================
# Original validated field untouched (R1, R5)
# ============================================================

class TestMinimaxDoesNotMutateValidated:
    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    @pytest.mark.asyncio
    async def test_validated_field_preserved(self, cls, task_type):
        """Minimax must NOT modify the original `validated` dict (R1, R5).

        Note: We use a minimal VALID_POLICY_BRIEF_JSON payload for all 4 pipelines
        — only policy_brief's schema matches; others get validated=None (expected).
        """
        p = cls()
        with _patch_call_llm(task_type):
            result = await p.run(event_topic="x")
        # validated field must exist in result (regardless of whether it's None)
        assert "validated" in result
        # If validated is non-None, it must be a dict (R5: minimax doesn't alter type)
        if result["validated"] is not None:
            assert isinstance(result["validated"], dict)
        # The minimax sub-dict is independent — must be present and valid
        assert result["minimax"]["valid"] is True


# ============================================================
# Error paths: minimax still runs and validates the error result
# ============================================================

class TestMinimaxOnErrorPaths:
    @pytest.mark.asyncio
    async def test_minimax_runs_on_invalid_json(self):
        p = ZhPolicyBriefPipeline()
        with _patch_call_llm("zh_policy_brief", return_text="not json {broken"):
            result = await p.run(event_topic="x")
        # Pipeline soft-fails; minimax still runs
        assert "minimax" in result
        # StrictSchema accepts the partial error result as input
        # (validated=None is valid input — minimax fills all empty)
        assert result["minimax"]["valid"] is True

    @pytest.mark.asyncio
    async def test_minimax_runs_on_schema_validation_fail(self):
        p = ZhPolicyBriefPipeline()
        bad = json.dumps({
            "task_type": "zh_policy_brief",
            "summary": "minimal",
            "key_points": [],
            "affected_entities": [],
            "timeline": [],
            "quantitative_targets": [],
            "risk_flags": [],
            "confidence": 2.0,  # OUT OF RANGE
        })
        with _patch_call_llm("zh_policy_brief", return_text=bad):
            result = await p.run(event_topic="x")
        assert result["status"] == "partial"
        assert "minimax" in result
        # minimax still passes (the partial result dict is structurally valid)
        assert result["minimax"]["valid"] is True

    @pytest.mark.asyncio
    async def test_minimax_runs_on_llm_exception(self):
        p = ZhPolicyBriefPipeline()
        with patch("fzq_ai.pipelines._zh_pipeline.call_llm",
                   side_effect=RuntimeError("LLM down")):
            result = await p.run(event_topic="x")
        assert result["status"] == "error"
        # Minimax still runs on error path (V25: error path carries minimax too)
        assert "minimax" in result
        assert result["minimax"]["valid"] is True


# ============================================================
# Minimax + civilization layer integration
# ============================================================

class TestMinimaxCivIntegration:
    @pytest.mark.asyncio
    async def test_minimax_writes_to_civilization(self):
        from fzq_ai.civilization.civilization_engine import CivilizationEngine
        civ = CivilizationEngine("test_minimax_integration")
        p = ZhPolicyBriefPipeline()
        # Use run_async (which receives civ kwarg) — run() doesn't process civ
        with _patch_call_llm("zh_policy_brief"):
            result = await p.run_async(event_topic="x", civilization=civ)
        assert result["minimax"]["valid"] is True
        # minimax wrote to civ
        assert civ.recall("minimax_last_validated_at") is not None
        # civ trace includes minimax (via run_async civ integration)
        assert "civilization_trace" in result


# ============================================================
# Backward compat: original pipeline fields still present
# ============================================================

class TestBackwardCompatibility:
    @pytest.mark.asyncio
    async def test_all_original_fields_still_present_via_run(self):
        """Adding minimax via sync run() must not remove any pre-existing result fields."""
        p = ZhPolicyBriefPipeline()
        with _patch_call_llm("zh_policy_brief"):
            result = await p.run(event_topic="x")
        # Original fields (V24.2.0)
        for field in ["task", "input", "output", "parsed", "validated",
                      "model", "warnings", "trace_id", "duration_ms",
                      "status", "fallback_chain"]:
            assert field in result, f"Missing original field: {field}"
        # V24.3.3 field (new)
        assert "minimax" in result

    @pytest.mark.asyncio
    async def test_all_fields_via_run_async(self):
        """run_async adds civilization_trace + minimax."""
        p = ZhPolicyBriefPipeline()
        with _patch_call_llm("zh_policy_brief"):
            result = await p.run_async(event_topic="x")
        # All sync run() fields + 2 more
        for field in ["task", "input", "output", "parsed", "validated",
                      "model", "warnings", "trace_id", "duration_ms",
                      "status", "fallback_chain",
                      "civilization_trace",  # run_async only
                      "minimax"]:            # V24.3.3
            assert field in result, f"Missing field: {field}"