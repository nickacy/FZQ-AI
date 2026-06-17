# fzq_ai/pipelines/daily_report_pipeline.py

import asyncio
from fzq_ai.pipelines.base_pipeline import BasePipeline
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.scenario_pipeline import ScenarioPipeline
from fzq_ai.domain.models import ServiceResult


class DailyReportPipeline(BasePipeline):
    """Daily report: concurrent execution of all analysis sections."""

    def __init__(self):
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()
        self.narrative = NarrativePipeline()
        self.scenario = ScenarioPipeline()

    async def _run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        """Concurrent execution of all 5 sub-pipelines via asyncio.gather."""
        tasks = [
            self.news.run_async(query=query),
            self.risk.run_async(query=query),
            self.sentiment.run_async(query=query),
            self.narrative.run_async(query=query),
            self.scenario.run_async(query=query),
        ]
        news, risk, sentiment, narrative, scenario = await asyncio.gather(*tasks)

        return ServiceResult.ok({
            "news": news.data if news.success else str(news.error),
            "risk": risk.data if risk.success else str(risk.error),
            "sentiment": sentiment.data if sentiment.success else str(sentiment.error),
            "narrative": narrative.data if narrative.success else str(narrative.error),
            "scenario": scenario.data if scenario.success else str(scenario.error),
        })
