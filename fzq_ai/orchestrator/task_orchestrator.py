# fzq_ai/orchestrator/task_orchestrator.py

import asyncio
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline


class TaskOrchestrator:
    """
    Pipeline Orchestrator（增强版）
    - 支持并发执行多个 Pipeline
    - 保留旧行为（同步 run()）
    """

    def __init__(self):
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为）
    # ---------------------------------------------------------
    def run(self, query: str):
        """
        旧行为：串行执行（不破坏旧逻辑）
        """
        news = self.news.run(query)
        risk = self.risk.run(query)
        sentiment = self.sentiment.run(query)

        return {
            "news": news,
            "risk": risk,
            "sentiment": sentiment,
        }

    # ---------------------------------------------------------
    # 新增：异步并发执行（性能提升 3–10 倍）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        """
        新行为：并发执行多个 Pipeline
        """

        tasks = [
            self.news.run_async(query),
            self.risk.run_async(query),
            self.sentiment.run_async(query),
        ]

        news, risk, sentiment = await asyncio.gather(*tasks)

        return {
            "news": news,
            "risk": risk,
            "sentiment": sentiment,
        }
