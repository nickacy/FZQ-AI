"""tests/test_pipelines.py — Pipeline 测试"""
import pytest
from fzq_ai.schemas.test_adapter import PipelineInput, PipelineOutput, PipelineMetrics, LanguageCode
from fzq_ai.pipelines.test_adapter import (
    MockNewsPipeline,
    MockNarrativePipeline,
    MockRiskPipeline,
    MockSentimentPipeline,
    MockScenarioPipeline,
    MockDailyReportPipeline,
)


class TestMockNewsPipeline:
    @pytest.mark.asyncio
    async def test_run_returns_pipeline_output(self):
        pl = MockNewsPipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output, PipelineOutput)
        assert isinstance(output.metrics, PipelineMetrics)

    @pytest.mark.asyncio
    async def test_run_has_analyzed_items(self):
        pl = MockNewsPipeline()
        output = await pl.run(PipelineInput())
        assert len(output.analyzed_items) <= 3

    @pytest.mark.asyncio
    async def test_run_metrics_pipeline_name(self):
        pl = MockNewsPipeline()
        output = await pl.run(PipelineInput())
        assert output.metrics.pipeline_name == "mock_news_pipeline"

    @pytest.mark.asyncio
    async def test_run_with_empty_items(self):
        pl = MockNewsPipeline()
        output = await pl.run(PipelineInput(items=[]))
        assert len(output.analyzed_items) == 3


class TestMockNarrativePipeline:
    @pytest.mark.asyncio
    async def test_run_returns_pipeline_output(self):
        pl = MockNarrativePipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output, PipelineOutput)
        assert output.daily_report is None

    @pytest.mark.asyncio
    async def test_run_has_narrative_items(self):
        pl = MockNarrativePipeline()
        output = await pl.run(PipelineInput())
        for item in output.analyzed_items:
            assert item.narrative is not None


class TestMockRiskPipeline:
    @pytest.mark.asyncio
    async def test_run_returns_pipeline_output(self):
        pl = MockRiskPipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output, PipelineOutput)

    @pytest.mark.asyncio
    async def test_run_risk_level(self):
        from fzq_ai.schemas.test_adapter import RiskLevel
        pl = MockRiskPipeline()
        output = await pl.run(PipelineInput())
        for item in output.analyzed_items:
            assert item.risk.overall_risk_level in RiskLevel


class TestMockSentimentPipeline:
    @pytest.mark.asyncio
    async def test_run_returns_pipeline_output(self):
        pl = MockSentimentPipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output, PipelineOutput)

    @pytest.mark.asyncio
    async def test_run_sentiment_label(self):
        from fzq_ai.schemas.test_adapter import SentimentLabel
        pl = MockSentimentPipeline()
        output = await pl.run(PipelineInput())
        for item in output.analyzed_items:
            assert item.sentiment.overall_sentiment in SentimentLabel


class TestMockScenarioPipeline:
    @pytest.mark.asyncio
    async def test_run_returns_pipeline_output(self):
        pl = MockScenarioPipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output, PipelineOutput)

    @pytest.mark.asyncio
    async def test_run_has_scenario(self):
        pl = MockScenarioPipeline()
        output = await pl.run(PipelineInput())
        for item in output.analyzed_items:
            assert item.scenario is not None


class TestMockDailyReportPipeline:
    @pytest.mark.asyncio
    async def test_run_returns_pipeline_output(self):
        pl = MockDailyReportPipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output, PipelineOutput)

    @pytest.mark.asyncio
    async def test_run_has_daily_report(self):
        pl = MockDailyReportPipeline()
        output = await pl.run(PipelineInput())
        assert output.daily_report is not None

    @pytest.mark.asyncio
    async def test_run_daily_report_type(self):
        from fzq_ai.schemas.test_adapter import DailyReport
        pl = MockDailyReportPipeline()
        output = await pl.run(PipelineInput())
        assert isinstance(output.daily_report, DailyReport)

    @pytest.mark.asyncio
    async def test_all_pipelines_consistent_output(self):
        pipelines = [
            MockNewsPipeline(),
            MockNarrativePipeline(),
            MockRiskPipeline(),
            MockSentimentPipeline(),
            MockScenarioPipeline(),
            MockDailyReportPipeline(),
        ]
        inp = PipelineInput()
        for pl in pipelines:
            output = await pl.run(inp)
            assert isinstance(output, PipelineOutput)
            assert isinstance(output.metrics, PipelineMetrics)
            assert output.generated_at is not None

    @pytest.mark.asyncio
    async def test_pipeline_input_with_target_language(self):
        pl = MockNewsPipeline()
        inp = PipelineInput(target_language=LanguageCode.ZH)
        output = await pl.run(inp)
        assert isinstance(output, PipelineOutput)
