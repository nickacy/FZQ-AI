# agents/fzq_agent.py

from core.config import Config
from pipelines.news_pipeline import NewsPipeline
from pipelines.narrative_pipeline import NarrativePipeline
from tui.dashboard import dashboard_main

class FZQAgent:
    """
    """

    def __init__(self):
        self.config = Config()
        self.news_pipeline = NewsPipeline(self.config)
        self.narrative_pipeline = NarrativePipeline(self.config)

    def run(self):
        # 1) 抓取新闻 + 摘要 + 风险评分
        articles = self.news_pipeline.run()

        # 2) 叙事分析（新版使用 run()）
        narrative = self.narrative_pipeline.run(articles)

        # 3) 启动 TUI Dashboard

        return narrative
