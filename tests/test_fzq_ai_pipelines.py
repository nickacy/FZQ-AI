"""
FZQ-AI v2.5 -- Pipeline Tests
Covers all pipelines: normal and error paths.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


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


class TestRiskPipeline:

    @pytest.mark.asyncio
    async def test_risk_pipeline_with_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        from fzq_ai.domain.models import Article
        pipeline = RiskPipeline()
        articles = [
            Article(title_original="Election crisis deepens", region="western"),
            Article(title_original="Market rallies on data", region="western"),
        ]
        result = await pipeline.run(articles=articles)
        assert result.success is True
        assert "overall_risk_score" in result.data

    @pytest.mark.asyncio
    async def test_risk_pipeline_empty_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        pipeline = RiskPipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False


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
        assert "FZQ-AI" in result.data

    @pytest.mark.asyncio
    async def test_daily_report_empty_articles(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        pipeline = DailyReportPipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False


class TestSentimentPipeline:

    @pytest.mark.asyncio
    async def test_sentiment_pipeline_with_articles(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        from fzq_ai.domain.models import Article
        pipeline = SentimentPipeline()
        articles = [
            Article(title_original="Growth surges", content_original="positive growth improvement"),
            Article(title_original="Crisis deepens", content_original="conflict war attack"),
        ]
        result = await pipeline.run(articles=articles)
        assert result.success is True
        assert "distribution" in result.data

    @pytest.mark.asyncio
    async def test_sentiment_pipeline_empty_articles(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        pipeline = SentimentPipeline()
        result = await pipeline.run(articles=[])
        assert result.success is False
