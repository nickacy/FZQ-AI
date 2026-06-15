""
FZQ-AI v2.5 — Pipeline 全面测试
覆盖所有 Pipeline 的正常路径和异常路径。
运行: python -m pytest tests/test_fzq_ai_pipelines.py -v
""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ── NewsPipeline 测试 ─────────────────────────────────────────

class TestNewsPipeline:

    def test_pipeline_creation(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        pipeline = NewsPipeline()
        assert pipeline is not None

    def test_run_no_topic(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        pipeline = NewsPipeline()
        result = pipeline.run("")
        assert result.success is True

    def test_run_with_topic_returns_service_result(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        pipeline = NewsPipeline()
        result = pipeline.run("test")
        assert hasattr(result, "success")
        assert hasattr(result, "data")
        assert hasattr(result, "error")


# ── RiskPipeline 测试 ─────────────────────────────────────────

class TestRiskPipeline:

    @pytest.mark.asyncio
    async def test_risk_pipeline_with_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        from fzq_ai.domain.models import Article
        pipeline = RiskPipeline()
        articles = [
            Article(title_original="Election crisis deepens amid protests", region="western"),
            Article(title_original="Market rallies on inflation data", region="western"),
        ]
        result = await pipeline.run(articles=articles)
        assert result.success is True
        assert "overall_risk_score" in result.data
        assert "category_intensity" in result.data

    @pytest.mark.asyncio
    async def test_risk_pipeline_empty_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        pipeline = RiskPipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False
        assert "articles" in result.error.lower()


# ── NarrativePipeline 测试 ────────────────────────────────────

class TestNarrativePipeline:

    @pytest.mark.asyncio
    async def test_narrative_pipeline_with_articles(self):
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        from fzq_ai.domain.models import Article
        pipeline = NarrativePipeline()
        articles = [
            Article(title_original="US sanctions expand", region="western"),
            Article(title_original="China GDP growth slows", region="east_asia"),
        ]
        result = await pipeline.run(articles=articles)
        assert result.success is True
        assert "western" in result.data
        assert "east_asia" in result.data

    @pytest.mark.asyncio
    async def test_narrative_pipeline_empty_articles(self):
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        pipeline = NarrativePipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False


# ── DailyReportPipeline 测试 ──────────────────────────────────

class TestDailyReportPipeline:

    @pytest.mark.asyncio
    async def test_daily_report_with_articles(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        from fzq_ai.domain.models import Article
        pipeline = DailyReportPipeline()
        articles = [
            Article(title_original="Conflict escalates", region="middle_east"),
            Article(title_original="Tech stocks surge", region="western"),
        ]
        result = await pipeline.run(articles=articles)
        assert result.success is True
        assert isinstance(result.data, str)
        assert "FZQ-AI" in result.data

    @pytest.mark.asyncio
    async def test_daily_report_empty_articles(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        pipeline = DailyReportPipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False

# ── SentimentPipeline 测试 ────────────────────────────────────

class TestSentimentPipeline:

    @pytest.mark.asyncio
    async def test_sentiment_pipeline_with_articles(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        from fzq_ai.domain.models import Article
        pipeline = SentimentPipeline()
        articles = [
            Article(title_original="Growth surges amid recovery", content_original="positive growth improvement"),
            Article(title_original="Crisis deepens as war continues", content_original="conflict war attack"),
        ]
        result = await pipeline.run(articles=articles)
        assert result.success is True
        assert "distribution" in result.data
        assert "overall_sentiment" in result.data

    @pytest.mark.asyncio
    async def test_sentiment_pipeline_empty_articles(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        pipeline = SentimentPipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False

