"""Daily report pipeline: orchestrates all pipelines into a single DailyReport."""
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    MultiDimensionAnalysis,
    DailyReport,
    DailyReportSection,
    RawNewsItem,
    RiskAnalysis,
    NarrativeAnalysis,
    SentimentAnalysis,
    ScenarioAnalysis,
    ModelProvider,
    LLMRequest,
    LanguageCode,
    RegionCode,
)
from fzq_ai.llm.real.llm_router import LLMRouter
from fzq_ai.pipelines.real.news_pipeline import NewsPipeline
from fzq_ai.pipelines.real.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.real.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.real.sentiment_pipeline import SentimentPipeline
from fzq_ai.pipelines.real.scenario_pipeline import ScenarioPipeline


class DailyReportPipeline:
    """Async daily report pipeline that orchestrates all sub-pipelines."""

    def __init__(
        self,
        llm_router: LLMRouter,
        news_pipeline: Optional[NewsPipeline] = None,
        narrative_pipeline: Optional[NarrativePipeline] = None,
        risk_pipeline: Optional[RiskPipeline] = None,
        sentiment_pipeline: Optional[SentimentPipeline] = None,
        scenario_pipeline: Optional[ScenarioPipeline] = None,
    ):
        self.llm_router = llm_router
        self.news_pipeline = news_pipeline or NewsPipeline(llm_router)
        self.narrative_pipeline = narrative_pipeline or NarrativePipeline(llm_router)
        self.risk_pipeline = risk_pipeline or RiskPipeline(llm_router)
        self.sentiment_pipeline = sentiment_pipeline or SentimentPipeline(llm_router)
        self.scenario_pipeline = scenario_pipeline or ScenarioPipeline(llm_router)

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Orchestrate all pipelines and compile a DailyReport."""
        start = time.perf_counter()
        metrics = PipelineMetrics(pipeline_name="daily_report_pipeline")

        # Run all sub-pipelines concurrently
        news_out, narrative_out, risk_out, sentiment_out, scenario_out = await self._run_all(
            pipeline_input
        )

        # Aggregate results
        all_analyzed: Dict[str, MultiDimensionAnalysis] = {}
        for out in [news_out, narrative_out, risk_out, sentiment_out, scenario_out]:
            for item in out.analyzed_items:
                if item.news_id not in all_analyzed:
                    all_analyzed[item.news_id] = MultiDimensionAnalysis(
                        news_id=item.news_id,
                        narrative=item.narrative,
                        risk=item.risk,
                        sentiment=item.sentiment,
                        scenario=item.scenario,
                    )
                else:
                    existing = all_analyzed[item.news_id]
                    if item.narrative:
                        existing.narrative = item.narrative
                    if item.risk:
                        existing.risk = item.risk
                    if item.sentiment:
                        existing.sentiment = item.sentiment
                    if item.scenario:
                        existing.scenario = item.scenario

        analyzed_items = list(all_analyzed.values())
        failed_items: List[Dict[str, Any]] = []
        for out in [news_out, narrative_out, risk_out, sentiment_out, scenario_out]:
            failed_items.extend(out.failed_items)

        metrics.items_processed = len(analyzed_items)
        metrics.items_failed = len(failed_items)
        metrics.fallback_count = (
            news_out.metrics.fallback_count
            + narrative_out.metrics.fallback_count
            + risk_out.metrics.fallback_count
            + sentiment_out.metrics.fallback_count
            + scenario_out.metrics.fallback_count
        )
        metrics.translation_count = news_out.metrics.translation_count

        # Build daily report
        report = await self._build_daily_report(
            pipeline_input, analyzed_items, metrics
        )

        total_latency = int((time.perf_counter() - start) * 1000)
        metrics.total_latency_ms = total_latency
        if metrics.items_processed > 0:
            metrics.avg_latency_ms = total_latency / metrics.items_processed

        return PipelineOutput(
            input_summary=pipeline_input,
            analyzed_items=analyzed_items,
            failed_items=failed_items,
            metrics=metrics,
            daily_report=report,
        )

    async def _run_all(self, pipeline_input: PipelineInput) -> tuple:
        """Run all sub-pipelines concurrently."""
        import asyncio
        results = await asyncio.gather(
            self.news_pipeline.run(pipeline_input),
            self.narrative_pipeline.run(pipeline_input),
            self.risk_pipeline.run(pipeline_input),
            self.sentiment_pipeline.run(pipeline_input),
            self.scenario_pipeline.run(pipeline_input),
            return_exceptions=True,
        )
        # Handle exceptions gracefully
        outputs = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                empty = PipelineOutput(
                    input_summary=pipeline_input,
                    metrics=PipelineMetrics(pipeline_name=f"pipeline_{i}"),
                )
                outputs.append(empty)
            else:
                outputs.append(r)
        return tuple(outputs)

    async def _build_daily_report(
        self,
        pipeline_input: PipelineInput,
        analyzed_items: List[MultiDimensionAnalysis],
        metrics: PipelineMetrics,
    ) -> DailyReport:
        """Compile a DailyReport from all pipeline results."""
        report_id = f"daily-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        report_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        top_stories = pipeline_input.items[:5]
        risk_alerts = [a.risk for a in analyzed_items if a.risk]
        sentiment_summary = await self._generate_sentiment_summary(analyzed_items)
        scenario_highlights = await self._generate_scenario_highlights(analyzed_items)

        sections = [
            DailyReportSection(
                section_title="Daily Overview",
                section_type="overview",
                content=f"Processed {metrics.items_processed} stories with {metrics.items_failed} failures.",
                priority=8,
            ),
            DailyReportSection(
                section_title="Top Stories",
                section_type="highlight",
                content="Key news items analyzed today.",
                related_news_ids=[s.id for s in top_stories],
                priority=9,
            ),
            DailyReportSection(
                section_title="Risk Alerts",
                section_type="risk_alert",
                content=f"{len(risk_alerts)} risk assessments completed.",
                priority=7,
            ),
            DailyReportSection(
                section_title="Sentiment Trend",
                section_type="sentiment_trend",
                content=sentiment_summary or "No sentiment summary available.",
                priority=6,
            ),
            DailyReportSection(
                section_title="Scenario Watch",
                section_type="scenario_watch",
                content="\n".join(scenario_highlights) if scenario_highlights else "No scenarios available.",
                priority=5,
            ),
        ]

        return DailyReport(
            report_id=report_id,
            report_date=report_date,
            language=pipeline_input.target_language,
            region_focus=pipeline_input.region_filter[0] if pipeline_input.region_filter else None,
            sections=sections,
            top_stories=top_stories,
            risk_alerts=risk_alerts,
            sentiment_summary=sentiment_summary,
            scenario_highlights=scenario_highlights,
            model_used=ModelProvider.OPENAI,
            generation_latency_ms=metrics.total_latency_ms,
        )

    async def _generate_sentiment_summary(self, analyzed_items: List[MultiDimensionAnalysis]) -> Optional[str]:
        """Generate a natural-language sentiment summary via LLM."""
        if not analyzed_items:
            return None
        sentiments = [a.sentiment for a in analyzed_items if a.sentiment]
        if not sentiments:
            return None
        prompt = (
            "Summarize the following sentiment data into a concise daily sentiment trend paragraph.\n\n"
            + "\n".join(
                f"- {s.news_id}: {s.overall_sentiment.value} (score {s.sentiment_score})"
                for s in sentiments[:10]
            )
        )
        request = LLMRequest(prompt=prompt, provider=ModelProvider.OPENAI, max_tokens=500)
        response = await self.llm_router.generate(request)
        return response.content

    async def _generate_scenario_highlights(self, analyzed_items: List[MultiDimensionAnalysis]) -> List[str]:
        """Generate scenario highlights from analyzed items."""
        highlights = []
        for a in analyzed_items:
            if a.scenario and a.scenario.base_case:
                highlights.append(
                    f"[{a.news_id}] {a.scenario.base_case.scenario_name}: "
                    f"{a.scenario.base_case.description[:200]}"
                )
        return highlights[:10]
