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
        assert pipeline is not None

    def test_run_no_topic(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        result = pipeline.run("")
        assert isinstance(result, str) and len(result) > 0

    def test_run_with_topic_returns_service_result(self):
        from fzq_ai.pipelines.news_pipeline import NewsPipeline
        result = pipeline.run("test")
        assert isinstance(result, str)
        assert len(result) > 0

class TestRiskPipeline:

    def test_risk_pipeline_with_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        result = pipeline.run(articles=articles)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_risk_pipeline_empty_articles(self):
        from fzq_ai.pipelines.risk_pipeline import RiskPipeline
        result = pipeline.run(articles=[])
        assert isinstance(result, str)

class TestNarrativePipeline:

    def test_narrative_pipeline_with_articles(self):
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        result = pipeline.run(articles=articles)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_narrative_pipeline_empty_articles(self):
        from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
        result = pipeline.run(articles=[])
        assert isinstance(result, str)

class TestDailyReportPipeline:

    def test_daily_report_with_articles(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        result = pipeline.run(articles=articles)
        assert isinstance(result, str) and len(result) > 0
        assert "FZQ-AI" in result

    def test_daily_report_empty_articles(self):
        from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
        result = pipeline.run(articles=[])
        assert isinstance(result, str)

class TestSentimentPipeline:

    def test_sentiment_pipeline_with_articles(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        result = pipeline.run(articles=articles)
        assert isinstance(result, str) and len(result) > 0
        assert "distribution" in result.data

    def test_sentiment_pipeline_empty_articles(self):
        from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
        result = pipeline.run(articles=[])
        assert isinstance(result, str)
