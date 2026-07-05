"""Kimi Interpreter — R1-R6 compliance tests + integration."""

from __future__ import annotations
import json
import pytest
from fzq_ai.interpreter.kimi_interpreter import KimiInterpreter
from fzq_ai.interpreter.models import ExplanationResult


SAMPLE_SCHEMA = {
    "facts": [
        {"who": "国务院", "what": "宣布AI新政策", "when": "今日", "where": "北京"},
        {"who": "Fed", "what": "raised rates 25bp", "when": "today"},
    ],
    "events": [
        {"level": 1, "summary": "AI政策发布", "actors": ["国务院"]},
        {"level": 2, "summary": "加息25bp", "actors": ["Fed"]},
        {"level": 2, "summary": "EU碳关税", "actors": ["EU"]},
    ],
    "actors": ["国务院", "华为", "阿里巴巴", "Fed", "EU"],
    "narratives": [
        {"theme": "AI产业监管", "stance": "positive", "confidence": 0.8},
        {"theme": "通胀担忧", "stance": "negative", "confidence": 0.9},
    ],
    "risks": {
        "political": ["政策不确定性"],
        "economic": ["通胀风险", "贸易战风险"],
        "social": [],
        "tech": ["AI安全风险"],
        "international": ["地缘竞争"],
    },
    "policy": [
        {"signal": "AI安全审查", "domain": "regulation", "direction": "tightening"},
        {"signal": "碳边境税", "domain": "environment", "direction": "new"},
    ],
    "trend": [
        {"trend": "AI监管趋严", "time_horizon": "medium-term"},
        {"trend": "利率上升趋势", "time_horizon": "short-term"},
    ],
    "raw_quotes": [
        {"text": "我们将保持警惕", "speaker": "Fed Powell", "language": "zh"},
        {"text": "我们对市场非常乐观", "speaker": "蒂姆·库克", "language": "zh"},
    ],
}


@pytest.fixture
def kimi():
    return KimiInterpreter()


@pytest.fixture
def result(kimi):
    return kimi.interpret(SAMPLE_SCHEMA)


# ── R1: No inference ─────────────────────────────────────

class TestKimiR1_NoInference:
    def test_no_fabricated_facts(self, result):
        assert isinstance(result.policy_brief, str)
        assert "alien" not in result.policy_brief.lower()

    def test_empty_handling(self, kimi):
        r = kimi.interpret({})
        assert r.policy_brief is not None
        assert len(r.policy_brief) > 0


# ── R2: No supplementation ───────────────────────────────

class TestKimiR2_NoSupplementation:
    def test_structured_passthrough(self, result):
        assert result.structured_explanation == SAMPLE_SCHEMA

    def test_no_fake_quotes(self, result):
        assert "anonymous source" not in result.quotes_analysis.lower()


# ── R3: No invention ─────────────────────────────────────

class TestKimiR3_NoInvention:
    def test_actor_not_invented(self, result):
        assert "Zorg" not in result.policy_brief


# ── R4: No structural change ─────────────────────────────

class TestKimiR4_NoStructuralChange:
    def test_structure_identical(self, result):
        assert result.structured_explanation == SAMPLE_SCHEMA


# ── R5: Natural language ─────────────────────────────────

class TestKimiR5_NaturalLanguage:
    def test_all_fields_non_empty(self, result):
        assert len(result.policy_brief) > 10
        assert len(result.risk_summary) > 10
        assert len(result.narrative_analysis) > 10
        assert len(result.trend_insights) > 10
        assert len(result.quotes_analysis) > 10


# ── R6: Valid JSON (Pydantic) ────────────────────────────

class TestKimiR6_ValidOutput:
    def test_pydantic_model(self, result):
        assert isinstance(result, ExplanationResult)
        d = result.model_dump()
        assert len(d) == 6
        assert all(isinstance(d[k], (str, dict)) for k in d)

    def test_json_serializable(self, result):
        json_str = json.dumps(result.model_dump(), ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["policy_brief"] == result.policy_brief


# ── Integration ──────────────────────────────────────────

class TestKimiIntegration:
    def test_field_count(self, result):
        d = result.model_dump()
        expected = ["policy_brief", "risk_summary", "narrative_analysis",
                     "trend_insights", "quotes_analysis", "structured_explanation"]
        for e in expected:
            assert e in d

    def test_civ_ready(self, result):
        """Output can be persisted to civilization memory."""
        d = result.model_dump()
        assert isinstance(d, dict)
        assert len(json.dumps(d, ensure_ascii=False)) < 100_000  # reasonable size
