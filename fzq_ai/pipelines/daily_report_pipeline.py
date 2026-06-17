# fzq_ai/pipelines/daily_report_pipeline.py

import asyncio
from typing import List

from .base_pipeline import BasePipeline
from .news_pipeline import NewsPipeline
from .narrative_pipeline import NarrativePipeline
from .risk_pipeline import RiskPipeline
from .sentiment_pipeline import SentimentPipeline
from .scenario_pipeline import ScenarioPipeline

from fzq_ai.schemas.pipeline_output import (
    NewsPipelineOutput,
    NarrativePipelineOutput,
    RiskPipelineOutput,
    SentimentPipelineOutput,
    ScenarioPipelineOutput,
    DailyReportPipelineOutput,
)

from fzq_ai.prompts.template_loader import load_prompt_template
from fzq_ai.llm.router import LLMRouter
from fzq_ai.schemas.llm import LLMRequestSchema


class DailyReportPipeline(BasePipeline[DailyReportPipelineOutput]):

    def __init__(self) -> None:
        super().__init__()
        self.news_pipeline = NewsPipeline()
        self.narrative_pipeline = NarrativePipeline()
        self.risk_pipeline = RiskPipeline()
        self.sentiment_pipeline = SentimentPipeline()
        self.scenario_pipeline = ScenarioPipeline()
        self.router = LLMRouter()

    async def run_async(
        self,
        topic: str,
        news_raw_texts: List[str],
    ) -> DailyReportPipelineOutput:

        # ------------------------------------------------------------
        # 1. 先跑 NewsPipeline（顺序依赖）
        # ------------------------------------------------------------
        news_result: NewsPipelineOutput = await self.news_pipeline.run_async(
            news_raw_texts=news_raw_texts
        )

        combined_summary = "\n".join(news_result.summaries)

        # ------------------------------------------------------------
        # 2. 并发执行 Narrative / Risk / Sentiment / Scenario
        # ------------------------------------------------------------
        (
            narrative_result,
            risk_result,
            sentiment_result,
            scenario_result,
        ) = await asyncio.gather(
            self.narrative_pipeline.run_async(summary_text=combined_summary),
            self.risk_pipeline.run_async(topic=topic),
            self.sentiment_pipeline.run_async(topic=topic),
            self.scenario_pipeline.run_async(topic=topic),
        )

        # ------------------------------------------------------------
        # 3. 用 LLM 生成最终日报（替换手写 compose）
        # ------------------------------------------------------------
        template = load_prompt_template("daily_report_generate.j2")

        filled_prompt = template.render(
            topic=topic,
            news="\n".join(news_result.summaries),
            narrative=narrative_result.narrative_text,
            risk=risk_result.summary,
            sentiment=sentiment_result.summary,
            scenario=scenario_result.scenarios,
        )

        llm_resp = await self.router.route_llm_call(
            task_type="daily_report_generate",
            req=LLMRequestSchema(prompt=filled_prompt),
        )

        final_report = llm_resp.content

        # ------------------------------------------------------------
        # 4. 返回完整结构化情报对象（Phase 4‑5 Schema）
        # ------------------------------------------------------------
        return DailyReportPipelineOutput(
            report_content=final_report,
            news=news_result,
            narrative=narrative_result,
            risk=risk_result,
            sentiment=sentiment_result,
            scenario=scenario_result,
            news_count=news_result.raw_input_count,
            task_status="completed",
        )
