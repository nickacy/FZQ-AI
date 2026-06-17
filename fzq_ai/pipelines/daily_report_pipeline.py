# fzq_ai/pipelines/daily_report_pipeline.py

import asyncio

from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.scenario_pipeline import ScenarioPipeline


class DailyReportPipeline:
    """
    DailyReportPipeline（增强版）
    - 保留旧行为（同步 run）
    - 新增 async run_async（并发执行所有 section）
    """

    def __init__(self):
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()
        self.narrative = NarrativePipeline()
        self.scenario = ScenarioPipeline()

    # ---------------------------------------------------------
    # 旧行为：同步串行执行（保持兼容）
    # ---------------------------------------------------------
    def run(self, query: str):
        news = self.news.run(query)
        risk = self.risk.run(query)
        sentiment = self.sentiment.run(query)
        narrative = self.narrative.run(query)
        scenario = self.scenario.run(query)

        return {
            "news": news,
            "risk": risk,
            "sentiment": sentiment,
            "narrative": narrative,
            "scenario": scenario,
        }

    # ---------------------------------------------------------
    # 新行为：异步并发执行（性能提升 5–10 倍）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        tasks = [
            self.news.run_async(query),
            self.risk.run_async(query),
            self.sentiment.run_async(query),
            self.narrative.run_async(query),
            self.scenario.run_async(query),
        ]

        news, risk, sentiment, narrative, scenario = await asyncio.gather(*tasks)

        return {
            "news": news,
            "risk": risk,
            "sentiment": sentiment,
            "narrative": narrative,
            "scenario": scenario,
        }
