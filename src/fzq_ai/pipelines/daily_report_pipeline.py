# fzq_ai/pipelines/daily_report_pipeline.py
# v13 DailyReportPipeline – 保留原业务逻辑 + 轻量对齐 v13

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult


EXEC_OVERVIEW_TEMPLATE = PromptTemplate("""
You are a senior intelligence officer. Based on the topic below, generate an
executive overview in 2–3 concise paragraphs, focusing on:
- Core developments
- Strategic significance
- Immediate watchpoints

Topic: $query
""")

TOP_STORIES_TEMPLATE = PromptTemplate("""
List 5 top stories or focal events related to the following topic. For each item,
provide:
- A short title
- 1–2 sentence description
- Why it matters (impact / risk / opportunity)

Topic: $query
""")

RISK_ALERTS_TEMPLATE = PromptTemplate("""
Generate a short risk alert section for the following topic, including:
- Key emerging risks
- Short-term triggers (next 7–30 days)
- Suggested monitoring indicators

Topic: $query
""")

OUTLOOK_TEMPLATE = PromptTemplate("""
Provide a 30–90 day outlook for the following topic, including:
- Likely trajectory
- Scenario highlights
- Recommended focus areas for intelligence monitoring

Topic: $query
""")


class DailyReportPipeline(BasePipeline):
    """Daily intelligence report pipeline built from multiple LLM sections."""

    name = "daily_report"

    def __init__(self):
        self.llm = LLMRouter()

    async def run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        # 并发生成各个报告段落
        tasks = [
            self.llm.route("daily_exec_overview", EXEC_OVERVIEW_TEMPLATE.render(query=query)),
            self.llm.route("daily_top_stories", TOP_STORIES_TEMPLATE.render(query=query)),
            self.llm.route("daily_risk_alerts", RISK_ALERTS_TEMPLATE.render(query=query)),
            self.llm.route("daily_outlook", OUTLOOK_TEMPLATE.render(query=query)),
        ]

        exec_overview, top_stories, risk_alerts, outlook = await asyncio.gather(*tasks)

        report = {
            "report_id": f"daily-report-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "topic": query,
            "sections": {
                "executive_overview": exec_overview,
                "top_stories": top_stories,
                "risk_alerts": risk_alerts,
                "outlook": outlook,
            },
        }

        return ServiceResult.ok(report)
