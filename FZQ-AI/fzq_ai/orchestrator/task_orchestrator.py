# fzq_ai/orchestrator/task_orchestrator.py

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.domain.models import ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline


class TaskOrchestrator:
    """
    统一调度所有 Pipeline 的 Orchestrator。
    """

    def __init__(self, agent_hub: Any = None):
        # 如果传入了 AgentHub，则复用其 router
        if agent_hub is not None:
            router = agent_hub.router
        else:
            router = LLMRouter()

        self.pipelines = {
            "news-intel": NewsPipeline(llm_router=router),
            "narrative": NarrativePipeline(llm_router=router),
            "risk": RiskPipeline(llm_router=router),
            "daily-report": DailyReportPipeline(llm_router=router),
        }

    def run(self, agent_name: str, items: list = None, **kwargs) -> Dict[str, Any]:
        """
        统一入口：根据 agent_name 调用对应 Pipeline。

        为兼容 run_agent_demo.py 的调用方式，
        当 agent_name == "daily_report" 时自动转为文章列表调用。
        """
        if items is None:
            items = []

        from fzq_ai.domain.models import Article
        articles = [Article(title_original=str(i)) for i in items]

        if agent_name == "daily_report":
            return self.run_agent("daily-report", articles=articles, **kwargs)
        elif agent_name == "daily-report":
            return self.run_agent("daily-report", articles=articles, **kwargs)
        elif agent_name == "narrative":
            return self.run_agent("narrative", articles=articles, **kwargs)
        elif agent_name == "risk":
            return self.run_agent("risk", articles=articles, **kwargs)
        elif agent_name == "news-intel":
            result = self.pipelines["news-intel"].run(topic=" ".join(items))
            return {"success": result.success, "data": result.data, "error": result.error}
        else:
            return {"error": f"Unknown agent: {agent_name}"}

    def run_agent(self, agent_name: str, articles: list = None, **kwargs) -> Dict[str, Any]:
        """
        底层调用：以 Article 列表调用 Pipeline。
        """
        if agent_name not in self.pipelines:
            return {"error": f"Unknown agent: {agent_name}"}

        pipeline = self.pipelines[agent_name]

        try:
            import asyncio
            result: ServiceResult = asyncio.run(
                pipeline.run(articles=articles, **kwargs)
            )
            return {"success": result.success, "data": result.data, "error": result.error}

        except Exception as e:
            return {"success": False, "error": str(e)}
