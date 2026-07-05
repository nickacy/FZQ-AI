"""Doubao Formatter — R1-R6 compliance tests + integration.

Rules:
  R1: No inference — never add facts
  R2: No supplementation — never fill missing fields
  R3: No invention — never create content
  R4: No structural change — preserve field names and order
  R5: Preserve field order — output fields in input order
  R6: Output must be valid JSON
"""

from __future__ import annotations
import json
import pytest
from fzq_ai.doubao.formatter import DoubaoFormatter


@pytest.fixture
def fmt():
    return DoubaoFormatter()


# ── R1: No inference ─────────────────────────────────────

class TestDoubaoR1_NoInference:
    def test_does_not_add_fields(self, fmt):
        data = {"facts": [{"who": "A"}]}
        result = fmt.format(data)
        assert len(result) == 1

    def test_does_not_add_values_to_empty(self, fmt):
        data = {"actors": []}
        result = fmt.format(data)
        assert result["actors"] == []

    def test_preserves_null(self, fmt):
        data = {"trend": None}
        result = fmt.format(data)
        assert result["trend"] is None


# ── R2: No supplementation ───────────────────────────────

class TestDoubaoR2_NoSupplementation:
    def test_missing_field_stays_missing(self, fmt):
        data = {"facts": [{"who": "A"}]}
        result = fmt.format(data)
        assert "events" not in result

    def test_partial_fact_stays_partial(self, fmt):
        data = {"facts": [{"who": "A"}]}
        result = fmt.format(data)
        fact = result["facts"][0]
        assert "what" not in fact


# ── R3: No invention ─────────────────────────────────────

class TestDoubaoR3_NoInvention:
    def test_empty_dict_returns_empty(self, fmt):
        result = fmt.format({})
        assert result == {}

    def test_values_unmodified(self, fmt):
        data = {"policy": ["signal 1", "signal 2"]}
        result = fmt.format(data)
        assert result["policy"] == ["signal 1", "signal 2"]


# ── R4: No structural change ─────────────────────────────

class TestDoubaoR4_NoStructuralChange:
    def test_nested_structure_preserved(self, fmt):
        data = {
            "risks": {
                "political": ["risk A"],
                "economic": ["risk B"],
            }
        }
        result = fmt.format(data)
        assert result["risks"]["political"] == ["risk A"]
        assert result["risks"]["economic"] == ["risk B"]

    def test_list_of_dicts_preserved(self, fmt):
        data = {"events": [{"level": 1, "summary": "E1"}, {"level": 2, "summary": "E2"}]}
        result = fmt.format(data)
        assert len(result["events"]) == 2
        assert result["events"][0]["level"] == 1


# ── R5: Preserve field order ─────────────────────────────

class TestDoubaoR5_FieldOrder:
    def test_top_level_order(self, fmt):
        data = {"facts": [], "events": [], "actors": []}
        result = fmt.format(data)
        keys = list(result.keys())
        assert keys.index("facts") < keys.index("events") < keys.index("actors")

    def test_all_fields_preserved(self, fmt):
        data = {"custom_field": "value", "facts": [], "extra": True}
        result = fmt.format(data)
        assert "custom_field" in result
        assert "extra" in result

    def test_full_schema_order(self, fmt):
        data = {
            "raw_quotes": [], "trend": [], "facts": [], "policy": [],
            "risks": {}, "events": [], "actors": [], "narratives": [],
        }
        result = fmt.format(data)
        keys = list(result.keys())
        for f in ["facts", "events", "actors", "narratives"]:
            assert f in keys


# ── R6: Valid JSON output ───────────────────────────────

class TestDoubaoR6_ValidJSON:
    def test_format_to_json_returns_string(self, fmt):
        result = fmt.format_to_json({"facts": [{"who": "A"}]})
        assert isinstance(result, str)

    def test_format_to_json_is_valid(self, fmt):
        result = fmt.format_to_json({"facts": [{"who": "A"}]})
        assert DoubaoFormatter.is_valid_json(result)

    def test_is_valid_json_rejects_bad(self):
        assert not DoubaoFormatter.is_valid_json("not json")

    def test_format_to_json_parseable(self, fmt):
        result = fmt.format_to_json({"facts": [{"who": "A", "what": "X"}]})
        parsed = json.loads(result)
        assert parsed["facts"][0]["who"] == "A"


# ── Integration ──────────────────────────────────────────

class TestDoubaoIntegration:
    def test_handles_pydantic_model(self, fmt):
        from fzq_ai.glm.schema import GLMCoreFact
        m = GLMCoreFact(who="A", what="X")
        result = fmt.format(m)
        assert result["who"] == "A"

    def test_pipeline_compatible(self, fmt):
        """Output can be consumed by downstream (Kimi, Qwen)."""
        data = {
            "facts": [{"who": "Alice", "what": "announced policy"}],
            "events": [{"level": 1, "summary": "Policy change", "actors": ["Alice"]}],
            "actors": ["Alice", "Bob"],
            "narratives": ["Economic reform"],
            "risks": {"political": ["Instability"], "economic": []},
            "policy": ["New regulation"],
            "trend": ["Upward"],
            "raw_quotes": ["We will act"],
        }
        result = fmt.format_to_json(data)
        parsed = json.loads(result)
        assert len(parsed["facts"]) == 1
        assert len(parsed["events"]) == 1
        assert len(parsed["policy"]) == 1
