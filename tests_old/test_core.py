"""
FZQ-AI Test Suite — Comprehensive tests for core modules.
Run with: python -m pytest tests/ -v
"""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# ── Config Tests ──────────────────────────────────────────────


class TestConfig:
    """Test configuration loading."""

    def test_deepseek_api_key_loaded(self):
        """Verify DEEPSEEK_API_KEY can be loaded from env."""
        from fzq_ai.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
        # These should at least be strings (may be empty if no .env)
        assert isinstance(DEEPSEEK_API_KEY, str)
        assert isinstance(DEEPSEEK_BASE_URL, str)
        assert DEEPSEEK_MODEL in ("deepseek-chat", "deepseek-reasoner", "")

    def test_base_url_normalization(self):
        """DeepSeekClient should normalize base_url correctly."""
        from fzq_ai.llm.providers.deepseek_client import DeepSeekClient

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test"}):
            # Test that /v1 is not doubled
            client = DeepSeekClient(
                api_key="sk-test",
                base_url="https://api.deepseek.com/v1",
            )
            assert client.base_url == "https://api.deepseek.com/v1"

            client2 = DeepSeekClient(
                api_key="sk-test",
                base_url="https://api.deepseek.com",
            )
            assert client2.base_url == "https://api.deepseek.com/v1"


# ── Domain Model Tests ────────────────────────────────────────


class TestDomainModels:
    """Test domain model integrity."""

    def test_service_result_ok(self):
        from fzq_ai.domain.models import ServiceResult
        result = ServiceResult.ok({"key": "value"})
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None

    def test_service_result_fail(self):
        from fzq_ai.domain.models import ServiceResult
        result = ServiceResult.fail("something broke")
        assert result.success is False
        assert result.error == "something broke"
        assert result.data is None

    def test_article_defaults(self):
        from fzq_ai.domain.models import Article
        a = Article(title_original="Test Title")
        assert a.title_original == "Test Title"
        assert a.credibility == 0.0
        assert a.propaganda_tags == []
        assert a.fetched_at is not None

    def test_intel_bundle_defaults(self):
        from fzq_ai.domain.models import IntelBundle, IntelMeta
        bundle = IntelBundle()
        assert bundle.articles == []
        assert isinstance(bundle.meta, IntelMeta)


# ── Formatter Tests ───────────────────────────────────────────


class TestFormatters:
    """Test formatting utilities."""

    def test_news_formatter(self):
        from fzq_ai.utils.formatter import NewsFormatter
        result = NewsFormatter.format("Breaking news summary")
        assert "### 📰 新闻摘要" in result
        assert "Breaking news summary" in result

    def test_narrative_formatter(self):
        from fzq_ai.utils.formatter import NarrativeFormatter
        result = NarrativeFormatter.format("Narrative analysis text")
        assert "### 📚 叙事分析" in result

    def test_risk_formatter_json(self):
        from fzq_ai.utils.formatter import RiskFormatter
        result = RiskFormatter.format('{"risk_level": "high"}')
        assert result == {"risk_level": "high"}

    def test_risk_formatter_fallback(self):
        from fzq_ai.utils.formatter import RiskFormatter
        result = RiskFormatter.format("not json")
        assert "raw" in result

    def test_daily_report_formatter(self):
        from fzq_ai.utils.formatter import DailyReportFormatter
        result = DailyReportFormatter.format("News", "Narrative", "Risk")
        assert "# 📅 每日简报" in result
        assert "News" in result
        assert "Narrative" in result
        assert "Risk" in result


# ── Error Handling Tests ──────────────────────────────────────


class TestErrors:
    """Test domain error classes."""

    def test_fzqai_error(self):
        from fzq_ai.domain.errors import FZQAIError
        err = FZQAIError("test message", code="TEST")
        assert "TEST: test message" in str(err)
        assert err.code == "TEST"

    def test_llm_error(self):
        from fzq_ai.domain.errors import LLMError
        err = LLMError("timeout")
        assert isinstance(err, Exception)
        assert "timeout" in str(err)

    def test_pipeline_error(self):
        from fzq_ai.domain.errors import PipelineError
        err = PipelineError("step failed")
        assert isinstance(err, Exception)


# ── Enums Tests ───────────────────────────────────────────────


class TestEnums:
    """Test domain enumerations."""

    def test_risk_levels(self):
        from fzq_ai.domain.enums import RiskLevel
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.HIGH.value == "HIGH"

    def test_sentiment(self):
        from fzq_ai.domain.enums import Sentiment
        assert Sentiment.POSITIVE.value == "positive"
        assert Sentiment.NEGATIVE.value == "negative"


# ── LLM Router Tests ──────────────────────────────────────────


class TestLLMRouter:
    """Test LLM router with mocked providers."""

    @pytest.mark.asyncio
    async def test_router_initialization(self):
        """Router should initialize with available providers."""
        with patch.dict(os.environ, {
            "DEEPSEEK_API_KEY": "sk-test",
            "OPENAI_API_KEY": "",
            "GEMINI_API_KEY": "",
        }):
            from fzq_ai.llm.llm_router import LLMRouter
            # Will fail if no key, but with test key it should init
            # Skip if key validation is strict
            try:
                router = LLMRouter()
                assert router.primary_provider in ("deepseek", "openai", "gemini")
            except (ValueError, RuntimeError) as e:
                pytest.skip(f"Router init requires real API keys: {e}")

    def test_router_metrics(self):
        """Metrics should return dict with provider states."""
        with patch.dict(os.environ, {
            "DEEPSEEK_API_KEY": "sk-test",
            "OPENAI_API_KEY": "",
            "GEMINI_API_KEY": "",
        }):
            from fzq_ai.llm.llm_router import LLMRouter
            try:
                router = LLMRouter()
                metrics = router.metrics
                assert "deepseek" in metrics
                assert "healthy" in metrics["deepseek"]
            except (ValueError, RuntimeError):
                pytest.skip("Router init requires real API keys")


# ── Pipeline Tests ────────────────────────────────────────────


class TestNewsPipeline:
    """Test news pipeline with mocked dependencies."""

    def test_pipeline_creation(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        pipeline = NewsPipeline()
        assert pipeline is not None

    def test_pipeline_run_no_topic(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        pipeline = NewsPipeline()
        result = pipeline.run("")
        assert isinstance(result, str) and len(result) > 0


class TestRiskPipeline:
    """Test risk analysis pipeline."""

    def test_risk_pipeline_with_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        from fzq_ai.domain.models import Article

        pipeline = RiskPipeline()
        articles = [
            Article(
                title_original="Election crisis deepens amid protests",
                region="western",
            ),
            Article(
                title_original="Market rallies on inflation data",
                region="western",
            ),
        ]
        result = pipeline.run(articles=articles)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_risk_pipeline_empty_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline

        pipeline = RiskPipeline()
        result = pipeline.run(articles=[])
        assert isinstance(result, str)


class TestNarrativePipeline:
    """Test narrative analysis pipeline."""

    def test_narrative_pipeline(self):
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        from fzq_ai.domain.models import Article

        pipeline = NarrativePipeline()
        articles = [
            Article(title_original="US sanctions expand", region="western"),
            Article(title_original="China GDP growth slows", region="east_asia"),
        ]
        result = pipeline.run(articles=articles)
        assert isinstance(result, str)
        assert len(result) > 0


class TestDailyReportPipeline:
    """Test daily report generation."""

    def test_daily_report(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        from fzq_ai.domain.models import Article

        pipeline = DailyReportPipeline()
        articles = [
            Article(title_original="Conflict escalates in region", region="middle_east"),
            Article(title_original="Tech stocks surge", region="western"),
        ]
        result = pipeline.run(articles=articles)
        assert isinstance(result, str)
        assert len(result) > 0
