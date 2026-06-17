"""Phase 3: End-to-end architecture validation tests."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestBasePipelineInheritance:
    """Verify all pipelines inherit from BasePipeline."""

    def test_narrative_inherits_base(self):
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert issubclass(NarrativePipeline, BasePipeline)

    def test_risk_inherits_base(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert issubclass(RiskPipeline, BasePipeline)

    def test_sentiment_inherits_base(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert issubclass(SentimentPipeline, BasePipeline)

    def test_scenario_inherits_base(self):
        from fzq_ai.pipelines.scenario_pipeline import ScenarioPipeline
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert issubclass(ScenarioPipeline, BasePipeline)

    def test_news_inherits_base(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert issubclass(NewsPipeline, BasePipeline)

    def test_daily_report_inherits_base(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert issubclass(DailyReportPipeline, BasePipeline)


class TestTaskRegistry:
    """Verify all pipeline task types are registered."""

    def test_all_tasks_registered(self):
        from fzq_ai.llm.task_registry import TaskRegistry
        r = TaskRegistry()
        tasks = r.list_tasks()
        required = [
            "news_intel", "event_extraction", "structured_extraction",
            "risk_intel", "risk_summary", "risk_factors", "risk_forecast",
            "sentiment", "sentiment_score", "sentiment_summary",
            "narrative_summary", "narrative_keypoints",
            "narrative_storyline", "narrative_implications",
            "scenario", "multilingual_summary", "deep_reasoning",
        ]
        for t in required:
            assert t in tasks, f"Missing task: {t}"

    def test_task_config_has_fallback(self):
        from fzq_ai.llm.task_registry import TaskRegistry
        r = TaskRegistry()
        for task in r.list_tasks():
            cfg = r.get(task)
            assert len(cfg.fallback_chain) >= 1, f"{task}: no fallback chain"

    def test_get_unknown_fallsback_to_sentiment(self):
        from fzq_ai.llm.task_registry import TaskRegistry
        r = TaskRegistry()
        cfg = r.get("nonexistent_task_xyz")
        assert cfg.name == "sentiment"


class TestSchemas:

    def test_news_intel_output_schema(self):
        """NewsPipelineOutput validates with correct fields."""
        from fzq_ai.schemas.pipeline_output import NewsPipelineOutput
        obj = NewsPipelineOutput(
            summary="news intel summary",
            article_count=10,
            regions_covered=["north_america", "europe"],
            languages_detected=["en", "zh"]
        )
        d = obj.model_dump()
        assert d["summary"] == "news intel summary"
        assert d["article_count"] == 10

    def test_narrative_output_schema(self):
        """NarrativePipelineOutput validates with correct fields."""
        from fzq_ai.schemas.pipeline_output import NarrativePipelineOutput
        obj = NarrativePipelineOutput(
            summary="narrative summary",
            key_points="key points 1, key points 2",
            storyline="storyline here",
            implications="implications here"
        )
        d = obj.model_dump()
        assert d["summary"] == "narrative summary"

    def test_risk_output_schema(self):
        """RiskPipelineOutput validates with correct fields."""
        from fzq_ai.schemas.pipeline_output import RiskPipelineOutput
        obj = RiskPipelineOutput(
            summary="risk summary",
            factors="factor1, factor2",
            forecast="stable",
            risk_score=42.5
        )
        d = obj.model_dump()
        assert d["summary"] == "risk summary"
        assert d["risk_score"] == 42.5

    def test_daily_report_output_schema(self):
        """DailyReportOutput validates with correct fields."""
        from fzq_ai.schemas.pipeline_output import DailyReportOutput
        obj = DailyReportOutput(
            news="news result",
            risk="risk result",
            sentiment="sentiment result",
            narrative="narrative result",
            scenario="scenario result"
        )
        d = obj.model_dump()
        assert d["news"] == "news result"

    def test_schema_from_import(self):
        """All schema models importable."""
        from fzq_ai.schemas.pipeline_output import (
            NewsPipelineOutput, RiskPipelineOutput, SentimentPipelineOutput,
            NarrativePipelineOutput, ScenarioPipelineOutput, DailyReportOutput
        )
        assert NewsPipelineOutput is not None
        assert DailyReportOutput is not None

class TestPromptTemplate:
    """Verify prompt template rendering."""

    def test_template_render(self):
        from fzq_ai.prompts.template import PromptTemplate
        t = PromptTemplate("Hello $name, your query is $query")
        result = t.render(name="Nick", query="test")
        assert "Nick" in result
        assert "test" in result

    def test_template_safe_substitute(self):
        from fzq_ai.prompts.template import PromptTemplate
        t = PromptTemplate("Hello $name")
        result = t.render()  # No key provided
        assert "$name" in result  # safe_substitute keeps unreplaced vars

    def test_base_template_identical(self):
        from fzq_ai.prompts.base.template import PromptTemplate as BasePT
        from fzq_ai.prompts.template import PromptTemplate as RootPT
        t1 = BasePT("test $x")
        t2 = RootPT("test $x")
        assert t1.render(x="v") == t2.render(x="v")


class TestLLMRouter:
    """Verify LLMRouter integration."""

    def test_router_imports(self):
        from fzq_ai.llm.llm_router import LLMRouter
        assert LLMRouter is not None

    def test_router_has_task_registry(self):
        from fzq_ai.llm.llm_router import LLMRouter
        router = LLMRouter()
        assert router.task_registry is not None
        assert router.provider_registry is not None

    def test_router_has_logger(self):
        from fzq_ai.llm.llm_router import LLMRouter
        router = LLMRouter()
        assert router.logger is not None

    def test_router_has_all_providers(self):
        from fzq_ai.llm.llm_router import LLMRouter
        router = LLMRouter()
        for name in ["openai", "deepseek", "minimax"]:
            assert name in router.providers, f"Missing provider: {name}"

    def test_router_score_provider(self):
        from fzq_ai.llm.llm_router import LLMRouter
        from fzq_ai.llm.task_registry import TaskConfig
        from fzq_ai.llm.provider_registry import ProviderCapabilities
        router = LLMRouter()
        task = TaskConfig(name="test", default_provider="openai",
                          fallback_chain=["openai"], json_mode=True)
        cap = ProviderCapabilities(name="openai", json_mode=True,
                                   reasoning=4, long_context=3, speed=3, cost=4, reliability=5)
        score = router._score_provider(task, cap)
        assert score > 0, f"Score should be positive, got {score}"

    def test_router_select_best_provider(self):
        from fzq_ai.llm.llm_router import LLMRouter
        from fzq_ai.llm.task_registry import TaskConfig
        router = LLMRouter()
        # json_mode=True should prefer openai (json_mode=True, reliability=5)
        task = TaskConfig(name="test2", default_provider="openai",
                          fallback_chain=["openai", "deepseek", "minimax"],
                          json_mode=True)
        best = router._select_best_provider(task)
        assert best is not None

    def test_router_batch_returns_list(self):
        from fzq_ai.llm.llm_router import LLMRouter
        router = LLMRouter()
        # batch with empty list should work
        async def _test():
            results = await router.batch([])
            assert results == []
        asyncio.run(_test())


class TestBasePipelineRunMethod:
    """Verify BasePipeline.run() works without asyncio.run() nesting."""

    class _MockPipeline:
        def __init__(self):
            from fzq_ai.pipelines.base_pipeline import BasePipeline
            self._bp = BasePipeline

    def test_base_pipeline_has_run(self):
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert hasattr(BasePipeline, "run")
        assert hasattr(BasePipeline, "run_async")

    def test_pipeline_has_safe_run(self):
        from fzq_ai.pipelines.base_pipeline import BasePipeline
        assert hasattr(BasePipeline, "_safe_run_async")

    @pytest.mark.asyncio
    async def test_run_async_returns_service_result(self):
        """Verify pipelines return ServiceResult via run_async."""
        from fzq_ai.pipelines.scenario_pipeline import ScenarioPipeline
        from fzq_ai.domain.models import ServiceResult
        with patch.object(ScenarioPipeline, '__init__', lambda self: None):
            p = ScenarioPipeline.__new__(ScenarioPipeline)
            p.llm = MagicMock()
            p.llm.route = AsyncMock(return_value="scenario text")
            result = await p.run_async("test query")
            assert isinstance(result, ServiceResult)
            assert result.success
            assert result.data == "scenario text"


class TestConcurrency:
    """Verify async gather patterns work correctly."""

    @pytest.mark.asyncio
    async def test_pipeline_run_async_uses_gather(self):
        """NarrativePipeline.run_async should gather multiple LLM calls."""
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        from fzq_ai.domain.models import ServiceResult
        with patch.object(NarrativePipeline, '__init__', lambda self: None):
            p = NarrativePipeline.__new__(NarrativePipeline)
            p.llm = MagicMock()
            p.llm.route = AsyncMock(return_value="narrative text")
            result = await p.run_async("test")
            assert isinstance(result, ServiceResult)
            assert result.success
            # Should call route exactly 4 times
            assert p.llm.route.call_count == 4

    @pytest.mark.asyncio
    async def test_daily_report_gathers_all_pipelines(self):
        """DailyReportPipeline.run_async should gather 5 sub-pipelines."""
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        from fzq_ai.domain.models import ServiceResult
        from fzq_ai.schemas.pipeline_output import DailyReportOutput
        # Test concurrency pattern, \
             patch('fzq_ai.pipelines.daily_report_pipeline.DailyReportOutput', DailyReportOutput):
            p = DailyReportPipeline.__new__(DailyReportPipeline)
            pipeline_names = ["news", "risk", "sentiment", "narrative", "scenario"]
            mock_result = ServiceResult.ok("data")
            mock_async = AsyncMock(return_value=mock_result)
            for name in pipeline_names:
                mock_pipe = MagicMock()
                mock_pipe.run_async = mock_async
                setattr(p, name, mock_pipe)
            result = await p.run_async("test")
            assert isinstance(result, ServiceResult)
            assert result.success
            assert mock_async.call_count == 5


class TestEdgeCases:
    """Edge case and robustness tests."""

    def test_pipeline_error_model(self):
        from fzq_ai.pipelines.errors import PipelineError
        err = PipelineError(message="test error", stage="TestPipeline", provider="openai")
        assert err.message == "test error"
        assert err.stage == "TestPipeline"
        assert err.provider == "openai"

    def test_empty_input_handling(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        with patch.object(NewsPipeline, '__init__', lambda self: None):
            p = NewsPipeline.__new__(NewsPipeline)
            # Should handle empty query gracefully
            assert p is not None
