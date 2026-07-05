import pytest
from fzq_ai.interpreter.kimi_interpreter import KimiInterpreter

SAMPLE_SCHEMA = {
    "facts": [{"what": "A did B"}],
    "actors": [{"name": "Alice"}],
    "narratives": [{"theme": "stability", "stance": "positive"}],
    "events": [{"level": 1}, {"level": 2}],
    "trend": [{"trend": "growth", "time_horizon": "short-term"}],
    "raw_quotes": [{"text": "We will act", "speaker": "Minister"}],
    "risks": {"political": [{"description": "tension"}]}
}

def test_requires_action_prefix():
    ki = KimiInterpreter()
    fb = {"requires_action": True}
    res = ki.interpret(SAMPLE_SCHEMA, feedback_context=fb)
    assert res.policy_brief.startswith("[ACTION REQUIRED] ")
    assert res.risk_summary.startswith("[ACTION REQUIRED] ")

def test_low_consistency_adds_warning():
    ki = KimiInterpreter()
    fb = {"consistency_score": 60}
    res = ki.interpret(SAMPLE_SCHEMA, feedback_context=fb)
    assert "结构一致性提醒" in res.risk_summary

def test_suggestions_appended_to_narrative():
    ki = KimiInterpreter()
    fb = {"suggestions": ["补齐 facts 字段", "risks 子项应为列表"]}
    res = ki.interpret(SAMPLE_SCHEMA, feedback_context=fb)
    assert "结构建议摘要" in res.narrative_analysis
