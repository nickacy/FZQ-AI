"""
fzq_ai/scenarios/political_intel.py — v6.0 Political Intelligence Scenario.
"""

from __future__ import annotations
from typing import Any, Dict, List

from fzq_ai.domain.models import ServiceResult
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
from fzq_ai.scenarios.base import BaseScenario


class PoliticalIntelScenario(BaseScenario):
    """
    v6.0: Political intelligence — news + risk + sentiment.
    """

    name = "Political Intelligence"
    description = (
        "Analyze political developments: news fetch, risk scoring, "
        "and sentiment analysis for a given topic or region."
    )

    def execute(
        self, topic: str = "global politics", **kwargs: Any
    ) -> ServiceResult:
        """
        Run: news-intel -> risk -> sentiment pipeline chain.

        Args:
            topic: Political topic/region to analyze

        Returns:
            ServiceResult with {topic, news_summary, risk, sentiment}
        """
        try:
            # 1. News
            news = NewsPipeline()
            news_result = news.run(topic=topic)

            # 2. Risk (extract articles from news)
            articles = self._parse_articles(news_result)

            risk = RiskPipeline()
            risk_result = risk.run(articles=articles)

            # 3. Sentiment
            sentiment = SentimentPipeline()
            sentiment_result = sentiment.run(articles=articles)

            return ServiceResult.ok({
                "topic": topic,
                "news_summary": news_result[:500] if isinstance(news_result, str)
                else str(news_result),
                "risk": risk_result[:300] if isinstance(risk_result, str)
                else str(risk_result),
                "sentiment": sentiment_result[:300] if isinstance(sentiment_result, str)
                else str(sentiment_result),
            })
        except Exception as e:
            return ServiceResult.fail(f"PoliticalIntelScenario failed: {e}")

    def _parse_articles(self, result: Any) -> List:
        """Extract Article list from pipeline result."""
        if isinstance(result, ServiceResult):
            data = result.data or {}
            if isinstance(data, dict):
                bundle = data.get("intel_bundle", data)
                return getattr(bundle, "articles", [])
        return []
