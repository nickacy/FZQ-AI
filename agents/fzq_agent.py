# agents/fzq_agent.py

from core.config import Config
from pipelines.news_pipeline import NewsPipeline
from pipelines.narrative_pipeline import NarrativePipeline
from tui.dashboard import dashboard_main


class FZQAgent:
    """
    FZQ‑AI Agent v1.5
    主控制器：负责 orchestrate 全流程
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
        dashboard_main(
            summary=narrative["global_summary"],
            clusters=narrative["clusters"],
            tension_matrix=narrative["tension_matrix"],
            articles=articles
        )

        return narrative
