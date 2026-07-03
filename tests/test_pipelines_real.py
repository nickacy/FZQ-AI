"""V25 — Real pipeline tests with mocked LLM.

Verifies the 4 zh_tasks pipelines end-to-end:
  - Prompt loading via importlib.resources
  - JSON parsing (direct, fenced, prose-wrapped)
  - Pydantic schema validation
  - Failover chain surfaced
  - Soft-failure semantics (no exception raised to caller)
"""
from __future__ import annotations
import os
import sys
import json
import pytest
from unittest.mock import patch

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


# ============================================================
# Fixtures — return minimal but schema-valid LLM JSON
# ============================================================

def _minimal_policy_brief_json() -> str:
    return json.dumps({
        "task_type": "zh_policy_brief",
        "summary": "国务院发布关于加强数据要素市场建设的指导意见",
        "key_points": [
            {"point": "建立数据交易所", "category": "目标", "evidence_span": "国务院文件"},
        ],
        "affected_entities": [
            {"entity": "国务院", "role": "执行方", "impact": "正面"},
        ],
        "timeline": [],
        "quantitative_targets": [
            {"metric": "数据交易规模", "value": "1万亿元", "deadline": "2025年"},
        ],
        "risk_flags": [],
        "confidence": 0.85,
    }, ensure_ascii=False)


def _minimal_risk_scan_json() -> str:
    return json.dumps({
        "task_type": "zh_risk_scan",
        "risks": [
            {
                "risk_id": "R-001",
                "category": "金融",
                "level": "中",
                "title": "市场波动风险",
                "summary": "近期市场出现明显波动",
                "evidence": [{"item_id": "i1", "span": "市场波动原文", "source": "news"}],
                "convey_chain": [],
                "affected_entities": ["A股"],
                "suggested_action": "持续监控",
                "confidence": 0.7,
            }
        ],
        "overall_risk_level": "中",
        "entity_watchlist": ["A股"],
        "suggested_actions": ["持续监控"],
        "summary": "整体风险中等",
        "confidence": 0.7,
    }, ensure_ascii=False)


def _minimal_opinion_json() -> str:
    return json.dumps({
        "task_type": "zh_opinion_landscape",
        "topic": "AI 监管",
        "time_range": "2026-07",
        "clusters": [
            {
                "cluster_id": "C-001",
                "label": "支持方",
                "stance": "支持",
                "sentiment": "正面",
                "size": 100,
                "key_arguments": ["需要监管"],
                "representative_quotes": [{"item_id": "i1", "span": "支持监管的引用"}],
            }
        ],
        "stance_map": ["支持"],
        "sentiment_map": ["正面"],
        "key_frames": [],
        "influencers": [],
        "heat_trend": [],
        "representative_quotes": [],
        "confidence": 0.8,
    }, ensure_ascii=False)


def _minimal_merge_json() -> str:
    return json.dumps({
        "task_type": "zh_multisource_merge",
        "event_id": "evt-001",
        "main_axis": {
            "what": {"value": "数据要素市场建设", "status": "一致"},
            "when": {"value": "2025年", "status": "一致"},
            "where": {"value": "全国", "status": "一致"},
            "who": {"value": "国务院", "status": "一致"},
            "why": {"value": "推动数字经济", "status": "一致"},
            "how": {"value": "建立数据交易所", "status": "一致"},
        },
        "perspective_diffs": [],
        "source_reliability": [
            {"source": "新华社", "score": 0.95, "reason": "权威官方"}
        ],
        "consistency_score": 0.9,
        "missing_sources": [],
        "conflict_sources": [],
        "evidence_map": [],
    }, ensure_ascii=False)


JSON_BY_TASK = {
    "zh_policy_brief": _minimal_policy_brief_json,
    "zh_risk_scan": _minimal_risk_scan_json,
    "zh_opinion_landscape": _minimal_opinion_json,
    "zh_multisource_merge": _minimal_merge_json,
}


def _patch_call_llm(task_type: str, return_text: str | None = None):
    """Patch call_llm to return a fixed string (default: minimal valid JSON)."""
    text = return_text if return_text is not None else JSON_BY_TASK[task_type]()
    return patch("fzq_ai.pipelines._zh_pipeline.call_llm", return_value=text)


# ============================================================
# Test 1: All 4 pipelines instantiate
# ============================================================

class TestPipelineInstantiation:
    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    def test_pipeline_instantiates(self, cls, task_type):
        p = cls()
        assert p.task_type == task_type
        assert p.prompt_path.endswith(".txt")
        assert p.output_schema is not None, f"Schema not registered for {task_type}"


# ============================================================
# Test 2: Happy path — LLM returns valid JSON → fully validated
# ============================================================

class TestHappyPath:
    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    @pytest.mark.asyncio
    async def test_valid_json_passes_validation(self, cls, task_type):
        p = cls()
        with _patch_call_llm(task_type):
            result = await p.run(event_topic="测试话题")
        assert result["status"] == "ok"
        assert result["task"] == task_type
        assert result["parsed"] is not None
        assert result["validated"] is not None
        assert result["warnings"] == []
        assert result["trace_id"]
        assert result["model"]
        assert result["duration_ms"] >= 0
        assert result["fallback_chain"]  # non-empty list


# ============================================================
# Test 3: JSON parsing — fenced / prose-wrapped
# ============================================================

class TestJsonParsing:
    @pytest.mark.asyncio
    async def test_fenced_json_block(self):
        p = ZhPolicyBriefPipeline()
        fenced = "Here is the result:\n```json\n" + JSON_BY_TASK["zh_policy_brief"]() + "\n```\nDone."
        with _patch_call_llm("zh_policy_brief", return_text=fenced):
            result = await p.run(event_topic="x")
        assert result["parsed"] is not None
        assert result["validated"] is not None

    @pytest.mark.asyncio
    async def test_prose_wrapped_json(self):
        p = ZhPolicyBriefPipeline()
        wrapped = "Let me think... " + JSON_BY_TASK["zh_policy_brief"]() + " ... hope this helps."
        with _patch_call_llm("zh_policy_brief", return_text=wrapped):
            result = await p.run(event_topic="x")
        assert result["parsed"] is not None
        assert result["validated"] is not None

    @pytest.mark.asyncio
    async def test_invalid_json_soft_fails(self):
        p = ZhPolicyBriefPipeline()
        with _patch_call_llm("zh_policy_brief", return_text="not json at all {broken"):
            result = await p.run(event_topic="x")
        assert result["parsed"] is None
        assert result["validated"] is None
        assert "json_parse_failed" in result["warnings"]
        assert result["status"] == "partial"

    @pytest.mark.asyncio
    async def test_json_valid_but_schema_invalid_soft_fails(self):
        p = ZhPolicyBriefPipeline()
        # Valid JSON but `confidence: 2.0` is out of [0.0, 1.0] range → validation fails
        bad = json.dumps({
            "task_type": "zh_policy_brief",
            "summary": "minimal",
            "key_points": [],
            "affected_entities": [],
            "timeline": [],
            "quantitative_targets": [],
            "risk_flags": [],
            "confidence": 2.0,  # OUT OF RANGE — should fail validation
        })
        with _patch_call_llm("zh_policy_brief", return_text=bad):
            result = await p.run(event_topic="x")
        # Parsed succeeds but validation fails
        assert result["parsed"] is not None
        assert result["validated"] is None
        assert any("schema_validation_failed" in w for w in result["warnings"])


# ============================================================
# Test 4: LLM call failure → soft-fail (no exception)
# ============================================================

class TestLLMFailure:
    @pytest.mark.asyncio
    async def test_llm_exception_soft_fails(self):
        p = ZhPolicyBriefPipeline()
        with patch("fzq_ai.pipelines._zh_pipeline.call_llm",
                   side_effect=RuntimeError("simulated LLM outage")):
            result = await p.run(event_topic="x")
        assert result["status"] == "error"
        assert result["parsed"] is None
        assert result["output"] == ""
        # Error captured in warnings
        assert any("simulated LLM outage" in w for w in result["warnings"])


# ============================================================
# Test 5: Input extraction — accept multiple kwarg names
# ============================================================

class TestInputExtraction:
    @pytest.mark.parametrize("kwarg_name", ["event_topic", "content", "input", "text", "query"])
    @pytest.mark.asyncio
    async def test_accepts_multiple_input_kwarg_names(self, kwarg_name):
        p = ZhPolicyBriefPipeline()
        with _patch_call_llm("zh_policy_brief"):
            result = await p.run(**{kwarg_name: "test input"})
        assert result["input"] == "test input"


# ============================================================
# Test 6: Pipeline registry integration
# ============================================================

class TestPipelineRegistry:
    @pytest.mark.parametrize("cls,task_type", ALL_PIPELINES)
    def test_pipeline_registered(self, cls, task_type):
        from fzq_ai.pipelines.registry import PipelineRegistry
        instance = PipelineRegistry.get(task_type)
        assert isinstance(instance, cls)
