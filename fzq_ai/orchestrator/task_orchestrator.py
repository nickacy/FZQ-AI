# fzq_ai/orchestrator/task_orchestrator.py

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.domain.models import ServiceResult
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline


class TaskOrchestrator:
    """
    统一调度所有 Pipeline 的 Orchestrator。
    注意：所有 Pipeline.run() 都是同步函数，因此这里不能使用 await。
    """

    def __init__(self):
        self.pipelines = {
            "news-intel": NewsPipeline(),
            "narrative": NarrativePipeline(),
            "risk": RiskPipeline(),
            "daily-report": DailyReportPipeline(),
        }

    def run_agent(self, agent_name: str, task: str, **kwargs) -> ServiceResult:
        """
        统一入口：根据 agent_name 调用对应 Pipeline。
        所有 Pipeline.run() 都是同步函数，因此这里必须同步调用。
        """

        if agent_name not in self.pipelines:
            return ServiceResult.fail(f"Unknown agent: {agent_name}")

        pipeline = self.pipelines[agent_name]

        try:
            # Pipeline.run() 是同步函数 → 不能 await
            result: ServiceResult = pipeline.run(**kwargs)

            # Pipeline 返回的就是 ServiceResult，不需要再包装
            return result

        except Exception as e:
            return ServiceResult.fail(str(e))
