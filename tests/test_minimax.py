"""tests/test_minimax.py — Minimax Strict Schema Validator tests.

Covers Mandatory Rules R1-R6:
  R1: Do NOT fabricate facts
  R2: Do NOT infer
  R3: MUST fill missing fields
  R4: MUST repair types
  R5: MUST maintain field consistency
  R6: Do NOT output natural language
"""
from __future__ import annotations
import json
import pytest

from fzq_ai.minimax import (
    StrictSchema,
    StrictRisks,
    StrictSchemaValidator,
    SchemaRepairError,
    repair_structure,
    repair_types,
    parse_json_text,
)
from fzq_ai.civilization.civilization_engine import CivilizationEngine


# ============================================================
# R1: Do NOT fabricate facts
# ============================================================

class TestR1NoFabrication:
    """Validator must never invent string content. Empty fields stay empty."""

    def test_empty_input_yields_all_empty(self):
        v = StrictSchemaValidator()
        s = v.validate({})
        assert s.facts == []
        assert s.events == []
        assert s.actors == []
        assert s.narratives == []
        assert s.policy == []
        assert s.trend == []
        assert s.raw_quotes == []
        assert s.risks.political == []
        assert s.risks.economic == []
        assert s.risks.social == []
        assert s.risks.tech == []
        assert s.risks.international == []

    def test_none_input_strict_raises(self):
        v = StrictSchemaValidator(strict=True)
        with pytest.raises(SchemaRepairError):
            v.validate(None)

    def test_none_input_lenient_returns_empty(self):
        v = StrictSchemaValidator(strict=False)
        s = v.validate(None)
        assert s.facts == []

    def test_partial_input_only_preserves_provided(self):
        """R1+R3: provided facts are kept verbatim; missing fields stay empty."""
        v = StrictSchemaValidator()
        s = v.validate({"facts": ["earth is round"]})
        assert s.facts == ["earth is round"]  # preserved
        assert s.events == []  # filled, not fabricated
        assert s.actors == []  # filled, not fabricated


# ============================================================
# R2: Do NOT infer
# ============================================================

class TestR2NoInference:
    """Validator must not interpret or extrapolate content."""

    def test_partial_risks_kept_verbatim(self):
        v = StrictSchemaValidator()
        s = v.validate({"risks": {"political": ["election"]}})
        assert s.risks.political == ["election"]
        # Other risk categories remain empty (no inference)
        assert s.risks.economic == []
        assert s.risks.social == []
        assert s.risks.tech == []
        assert s.risks.international == []

    def test_string_facts_not_split_or_inferred(self):
        v = StrictSchemaValidator()
        s = v.validate({"facts": "single fact string"})
        # R4 repairs to list but R2 does not split, infer, or expand
        assert s.facts == ["single fact string"]


# ============================================================
# R3: MUST fill missing fields
# ============================================================

class TestR3FillMissing:
    """Every missing field is filled with empty list / empty StrictRisks."""

    def test_all_top_level_fields_present(self):
        v = StrictSchemaValidator()
        s = v.validate({"facts": ["x"]})
        # All 8 top-level fields must exist
        assert all(hasattr(s, f) for f in [
            "facts", "events", "actors", "narratives",
            "risks", "policy", "trend", "raw_quotes"
        ])

    def test_all_risk_subfields_present(self):
        v = StrictSchemaValidator()
        s = v.validate({})
        # All 5 risk sub-fields must exist
        assert all(hasattr(s.risks, f) for f in [
            "political", "economic", "social", "tech", "international"
        ])
        assert s.risks.political == []
        assert s.risks.economic == []
        assert s.risks.social == []
        assert s.risks.tech == []
        assert s.risks.international == []

    def test_field_order_canonical(self):
        """R3+R5: output dict has canonical field order."""
        v = StrictSchemaValidator()
        # Pass fields in reverse order to verify ordering is enforced
        s = v.validate({"raw_quotes": ["q"], "trend": ["t"], "policy": ["p"]})
        dumped = s.model_dump()
        keys = list(dumped.keys())
        assert keys == ["facts", "events", "actors", "narratives",
                        "risks", "policy", "trend", "raw_quotes"]


# ============================================================
# R4: MUST repair types
# ============================================================

class TestR4TypeRepair:
    """String -> list, dict -> list, list-of-dict -> list-of-str, etc."""

    def test_string_actors_becomes_list(self):
        v = StrictSchemaValidator()
        s = v.validate({"actors": "John Doe"})
        assert s.actors == ["John Doe"]

    def test_dict_events_becomes_list_of_one_serialized_str(self):
        v = StrictSchemaValidator()
        s = v.validate({"events": {"date": "2025-01-01", "name": "X"}})
        assert len(s.events) == 1
        # dict is JSON-serialized to a deterministic string
        assert "date" in s.events[0]
        assert "2025-01-01" in s.events[0]

    def test_list_with_none_elements_filtered(self):
        v = StrictSchemaValidator()
        s = v.validate({"facts": ["a", None, "b", None]})
        assert s.facts == ["a", "b"]  # None filtered out

    def test_risks_as_list_converted_to_dict(self):
        """R4: risks is array -> dict (political bucket by default)."""
        v = StrictSchemaValidator()
        s = v.validate({"risks": ["risk1", "risk2"]})
        assert s.risks.political == ["risk1", "risk2"]
        assert s.risks.economic == []

    def test_risks_list_with_category_tagged(self):
        v = StrictSchemaValidator()
        s = v.validate({"risks": [
            {"category": "economic", "text": "inflation"},
            {"category": "tech", "text": "AI"},
        ]})
        assert "inflation" in s.risks.economic
        assert "AI" in s.risks.tech

    def test_int_events_becomes_list(self):
        v = StrictSchemaValidator()
        s = v.validate({"events": 42})
        assert s.events == ["42"]


# ============================================================
# R5: MUST maintain field consistency
# ============================================================

class TestR5FieldConsistency:
    """Field names must match the Strict Schema exactly."""

    def test_field_names_match_schema(self):
        v = StrictSchemaValidator()
        s = v.validate({"facts": ["x"], "unknown_field": ["ignored"]})
        dumped = s.model_dump()
        # All keys must be in canonical schema (no rogue "unknown_field")
        assert "unknown_field" not in dumped
        assert set(dumped.keys()) == {
            "facts", "events", "actors", "narratives",
            "risks", "policy", "trend", "raw_quotes"
        }

    def test_canonical_field_order_preserved(self):
        v = StrictSchemaValidator()
        s = v.validate({"policy": ["p"], "actors": ["a"]})
        keys = list(s.model_dump().keys())
        assert keys[0] == "facts"
        assert keys[-1] == "raw_quotes"


# ============================================================
# R6: Do NOT output natural language
# ============================================================

class TestR6NoNaturalLanguage:
    """Output is always a Pydantic StrictSchema, never a string or dict with prose."""

    def test_output_is_pydantic_model(self):
        v = StrictSchemaValidator()
        s = v.validate({"facts": ["x"]})
        assert isinstance(s, StrictSchema)
        # Not a string, not a dict
        assert not isinstance(s, str)
        assert not isinstance(s, dict)

    def test_string_input_parsed_to_dict_no_prose_in_output(self):
        v = StrictSchemaValidator()
        s = v.validate('{"facts": ["x"]}')
        assert isinstance(s, StrictSchema)
        # All string fields are facts/quotes/etc — no explanatory text added
        assert all(isinstance(x, str) for x in s.facts)


# ============================================================
# JSON text input path (covers LLM-style raw text)
# ============================================================

class TestJsonTextInput:
    def test_parse_json_text_direct(self):
        assert parse_json_text('{"a": 1}') == {"a": 1}

    def test_parse_json_text_fenced(self):
        text = 'Some intro\n```json\n{"a": 2}\n```\nTrailing prose'
        assert parse_json_text(text) == {"a": 2}

    def test_parse_json_text_no_json(self):
        assert parse_json_text("just plain text") is None

    def test_validate_accepts_json_string(self):
        v = StrictSchemaValidator()
        s = v.validate('{"actors": "Alice", "facts": ["x"]}')
        assert s.actors == ["Alice"]
        assert s.facts == ["x"]

    def test_validate_accepts_fenced_json_string(self):
        v = StrictSchemaValidator()
        text = '```json\n{"policy": ["p1", "p2"]}\n```'
        s = v.validate(text)
        assert s.policy == ["p1", "p2"]


# ============================================================
# Repair primitives (unit tests)
# ============================================================

class TestRepairPrimitives:
    def test_repair_structure_adds_missing_fields(self):
        out = repair_structure({"facts": ["x"]})
        assert "events" in out
        assert "actors" in out
        assert "risks" in out
        assert out["events"] == []

    def test_repair_types_coerces_dict(self):
        repaired = repair_structure({"events": {"k": "v"}})
        repaired = repair_types(repaired)
        assert isinstance(repaired["events"], list)
        assert len(repaired["events"]) == 1

    def test_repair_structure_raises_on_non_dict(self):
        with pytest.raises(SchemaRepairError):
            repair_structure("not a dict")  # type: ignore[arg-type]


# ============================================================
# Civilization integration (V24.3.1)
# ============================================================

class TestCivilizationIntegration:
    def test_civ_remember_on_validate(self):
        v = StrictSchemaValidator()
        civ = CivilizationEngine("test_minimax")
        s = v.validate_with_civ({"facts": ["x"]}, civ=civ)
        assert s.facts == ["x"]
        assert civ.recall("minimax_last_facts_count") == "1"
        assert civ.recall("minimax_last_validated_at") is not None

    def test_civ_none_falls_back_to_plain_validate(self):
        v = StrictSchemaValidator()
        s = v.validate_with_civ({"actors": "Bob"}, civ=None)
        assert s.actors == ["Bob"]


# ============================================================
# End-to-end: malformed input gracefully handled
# ============================================================

class TestEndToEnd:
    def test_minimal_input(self):
        v = StrictSchemaValidator()
        s = v.validate({})
        assert isinstance(s, StrictSchema)
        # All fields are empty but present
        assert s.model_dump() == {
            "facts": [], "events": [], "actors": [], "narratives": [],
            "risks": {
                "political": [], "economic": [], "social": [],
                "tech": [], "international": []
            },
            "policy": [], "trend": [], "raw_quotes": []
        }

    def test_chaotic_input_full_repair(self):
        v = StrictSchemaValidator()
        chaotic = {
            "facts": "single fact",
            "events": {"date": "2025-01"},
            "actors": ["Alice", None, 42],
            "risks": ["r1", {"category": "tech", "text": "AI risk"}],
            # missing: narratives, policy, trend, raw_quotes
            # rogue: unknown_field
            "unknown_field": ["ignored"],
        }
        s = v.validate(chaotic)
        assert s.facts == ["single fact"]
        assert len(s.events) == 1
        assert s.actors == ["Alice", "42"]  # None filtered, int str'd
        assert "r1" in s.risks.political
        assert "AI risk" in s.risks.tech
        assert s.narratives == []
        assert s.policy == []
        assert s.trend == []
        assert s.raw_quotes == []
        # unknown_field dropped (R5)
        assert "unknown_field" not in s.model_dump()

    def test_dump_is_json_serializable(self):
        """R6: output is JSON-serializable (no prose, no non-JSON types)."""
        v = StrictSchemaValidator()
        s = v.validate({"facts": ["x"], "actors": ["y"]})
        dumped = s.model_dump()
        # Should not raise
        json_str = json.dumps(dumped, ensure_ascii=False)
        # Round-trip
        reparsed = json.loads(json_str)
        assert reparsed["facts"] == ["x"]
        assert reparsed["actors"] == ["y"]