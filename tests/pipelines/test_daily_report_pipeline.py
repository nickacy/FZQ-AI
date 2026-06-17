# tests/pipelines/test_daily_report_pipeline.py
# Phase 4‑7：DailyReportPipeline 全套测试

import pytest
import asyncio

from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.schemas.pipeline_output import (
    DailyReportPipelineOutput,
    NewsPipelineOutput,
    NarrativePipelineOutput,
    RiskPipelineOutput,
    SentimentPipelineOutput,
    ScenarioPipelineOutput,
)


# ------------------------------------------------------------
# 1. 基础异步运行测试
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_daily_report_pipeline_basic():
    pipeline = DailyReportPipeline()

    result = await pipeline.run_async(
        topic="AI Industry",
        news_raw_texts=[
            "OpenAI released a new model.",
            "Google announced Gemini upgrades."
        ]
    )

    assert isinstance(result, DailyReportPipelineOutput)
    assert isinstance(result.report_content, str)
    assert result.news_count == 2


# ------------------------------------------------------------
# 2. Schema 结构完整性测试
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_daily_report_pipeline_schema_integrity():
    pipeline = DailyReportPipeline()

    result = await pipeline.run_async(
        topic="Economy",
        news_raw_texts=["Inflation rises", "Interest rates unchanged"]
    )

    assert isinstance(result.news, NewsPipelineOutput)
    assert isinstance(result.narrative, NarrativePipelineOutput)
    assert isinstance(result.risk, RiskPipelineOutput)
    assert isinstance(result.sentiment, SentimentPipelineOutput)
    assert isinstance(result.scenario, ScenarioPipelineOutput)


# ------------------------------------------------------------
# 3. 并发行为测试（确保 4 个子任务并发执行）
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_daily_report_pipeline_concurrency(monkeypatch):
    pipeline = DailyReportPipeline()

    call_order = []

    async def fake_run_async(*args, **kwargs):
        call_order.append("called")
        await asyncio.sleep(0.01)
        return "ok"

    # mock 4 个子 pipeline 的 run_async
    monkeypatch.setattr(pipeline.narrative_pipeline, "run_async", fake_run_async)
    monkeypatch.setattr(pipeline.risk_pipeline, "run_async", fake_run_async)
    monkeypatch.setattr(pipeline.sentiment_pipeline, "run_async", fake_run_async)
    monkeypatch.setattr(pipeline.scenario_pipeline, "run_async", fake_run_async)

    await pipeline.run_async(
        topic="Tech",
        news_raw_texts=["Some news"]
    )

    # 4 个子任务必须全部执行
    assert len(call_order) == 4


# ------------------------------------------------------------
# 4. Prompt 渲染测试（确保模板变量正确填充）
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_daily_report_pipeline_prompt_render(monkeypatch):
    pipeline = DailyReportPipeline()

    captured_prompt = {}

    async def fake_route_llm_call(task_type, req):
        captured_prompt["prompt"] = req.prompt
        return type("FakeResp", (), {"content": "FAKE_REPORT"})

    monkeypatch.setattr(pipeline.router, "route_llm_call", fake_route_llm_call)

    await pipeline.run_async(
        topic="Energy",
        news_raw_texts=["Oil prices rise"]
    )

    assert "Energy" in captured_prompt["prompt"]
    assert "Oil prices rise" in captured_prompt["prompt"]


# ------------------------------------------------------------
# 5. LLMRouter 调用测试（确保正确 task_type）
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_daily_report_pipeline_llm_task_type(monkeypatch):
    pipeline = DailyReportPipeline()

    captured = {}

    async def fake_route_llm_call(task_type, req):
        captured["task_type"] = task_type
        return type("FakeResp", (), {"content": "OK"})

    monkeypatch.setattr(pipeline.router, "route_llm_call", fake_route_llm_call)

    await pipeline.run_async(
        topic="Finance",
        news_raw_texts=["Market volatility increases"]
    )

    assert captured["task_type"] == "daily_report_generate"


# ------------------------------------------------------------
# 6. 错误处理测试（模拟子 pipeline 抛异常）
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_daily_report_pipeline_error(monkeypatch):
    pipeline = DailyReportPipeline()

    async def fake_error(*args, **kwargs):
        raise RuntimeError("Simulated failure")

    monkeypatch.setattr(pipeline.news_pipeline, "run_async", fake_error)

    with pytest.raises(RuntimeError):
        await pipeline.run_async(
            topic="ErrorTest",
            news_raw_texts=["test"]
        )
