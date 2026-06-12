from typing import List, Dict, Any
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline


class AgentHub:
    def __init__(self, config: Dict[str, Any]):
        # 初始化 LLM 路由器（自动 Key Routing）
        self.router = LLMRouter(config)

        # 初始化所有 Pipeline
        self.news_pipeline = NewsPipeline(self.router)
        self.narrative_pipeline = NarrativePipeline(self.router)
        self.risk_pipeline = RiskPipeline(self.router)
        self.daily_report_pipeline = DailyReportPipeline(self.router)

    # ---------------- 任务入口 ----------------

    def run_news(self, items: List[str]) -> str:
        return self.news_pipeline.run(items)

    def run_narrative(self, items: List[str]) -> Dict[str, Any]:
        merged = "\n".join(items)
        return self.narrative_pipeline.run({
            "merged_news": merged,
            "news_items": items
        })

    def run_risk(self, items: List[str]) -> Dict[str, Any]:
        return self.risk_pipeline.run(items)

    def run_daily_report(self, items: List[str]) -> Dict[str, Any]:
        return self.daily_report_pipeline.run(items)

    # ---------------- Metrics 输出 ----------------

    def get_metrics(self):
        return self.router.metrics.dump()
