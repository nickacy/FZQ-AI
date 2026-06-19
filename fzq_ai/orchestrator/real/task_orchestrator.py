"""
FZQ-AI Orchestrator — Real Task Orchestrator
Coordinates all 6 pipelines. Concurrent execution via asyncio.gather.
Aggregates into DailyReport. Has run(pipeline_input) → DailyReport.
Error handling. Fallback. Metrics. Scheduling support.
"""
import asyncio
import inspect
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    DailyReport,
    DailyReportSection,
    MultiDimensionAnalysis,
    ModelProvider,
    LanguageCode,
    RegionCode,
    PipelineMetrics,
)
from fzq_ai.pipelines.real import (
    NewsPipeline,
    NarrativePipeline,
    RiskPipeline,
    SentimentPipeline,
    ScenarioPipeline,
    DailyReportPipeline,
)


class TaskOrchestrator:
    """
    Coordinates all 6 pipelines with concurrent execution via asyncio.gather.
    Aggregates outputs into a DailyReport with error handling and fallback.
    """

    def __init__(self):
        self.news_pipeline = NewsPipeline()
        self.narrative_pipeline = NarrativePipeline()
        self.risk_pipeline = RiskPipeline()
        self.sentiment_pipeline = SentimentPipeline()
        self.scenario_pipeline = ScenarioPipeline()
        self.daily_report_pipeline = DailyReportPipeline()
        self._metrics: List[PipelineMetrics] = []
        self._schedule_callback: Optional[Callable] = None

    async def run(self, pipeline_input: PipelineInput) -> DailyReport:
        """Execute all 6 pipelines concurrently and aggregate into DailyReport."""
        start_time = time.perf_counter()

        tasks = [
            self._run_pipeline("news", self.news_pipeline, pipeline_input),
            self._run_pipeline("narrative", self.narrative_pipeline, pipeline_input),
            self._run_pipeline("risk", self.risk_pipeline, pipeline_input),
            self._run_pipeline("sentiment", self.sentiment_pipeline, pipeline_input),
            self._run_pipeline("scenario", self.scenario_pipeline, pipeline_input),
            self._run_pipeline("daily_report", self.daily_report_pipeline, pipeline_input),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        outputs: Dict[str, Optional[PipelineOutput]] = {}
        errors: List[str] = []
        for i, name in enumerate(
            ["news", "narrative", "risk", "sentiment", "scenario", "daily_report"]
        ):
            result = results[i]
            if isinstance(result, Exception):
                errors.append(f"{name} pipeline failed: {result}")
                outputs[name] = None
            else:
                outputs[name] = result
                if hasattr(result, "metrics"):
                    self._metrics.append(result.metrics)

        # Extract daily report from daily_report pipeline if available
        daily_report: Optional[DailyReport] = None
        if outputs.get("daily_report") is not None:
            daily_report = outputs["daily_report"].daily_report

        # Fallback: build a report from other pipeline outputs
        if daily_report is None:
            daily_report = self._build_fallback_daily_report(outputs, pipeline_input)

        # Attach orchestrator metadata
        total_latency_ms = int((time.perf_counter() - start_time) * 1000)
        daily_report.metadata["orchestrator_latency_ms"] = total_latency_ms
        daily_report.metadata["pipeline_errors"] = errors
        daily_report.metadata["fallback_used"] = outputs.get("daily_report") is None

        return daily_report

    async def _run_pipeline(
        self, name: str, pipeline, pipeline_input: PipelineInput
    ) -> PipelineOutput:
        """Run a single pipeline and return its output."""
        return await pipeline.run(pipeline_input)

    def _build_fallback_daily_report(
        self,
        outputs: Dict[str, Optional[PipelineOutput]],
        pipeline_input: PipelineInput,
    ) -> DailyReport:
        """Build a fallback DailyReport from available pipeline outputs."""
        merged_items: List[MultiDimensionAnalysis] = []
        for key in ["news", "narrative", "risk", "sentiment", "scenario"]:
            output = outputs.get(key)
            if output is not None and hasattr(output, "analyzed_items"):
                merged_items.extend(output.analyzed_items)

        # Deduplicate by news_id
        seen: set = set()
        unique_items: List[MultiDimensionAnalysis] = []
        for item in merged_items:
            if item.news_id not in seen:
                seen.add(item.news_id)
                unique_items.append(item)

        sections = [
            DailyReportSection(
                section_title="Executive Overview",
                section_type="overview",
                content="Aggregated report from available pipeline outputs.",
                priority=1,
            ),
            DailyReportSection(
                section_title="Risk Alerts",
                section_type="risk_alert",
                content="\n".join(
                    [f"- {m.news_id}: {m.risk.overall_risk_level.value}" for m in unique_items]
                ),
                priority=2,
            ),
            DailyReportSection(
                section_title="Sentiment Trends",
                section_type="sentiment_trend",
                content="\n".join(
                    [f"- {m.news_id}: {m.sentiment.overall_sentiment.value}" for m in unique_items]
                ),
                priority=3,
            ),
            DailyReportSection(
                section_title="Scenario Watch",
                section_type="scenario_watch",
                content="\n".join(
                    [f"- {m.news_id}: {m.scenario.base_case.scenario_name}" for m in unique_items]
                ),
                priority=4,
            ),
        ]

        return DailyReport(
            report_id=f"DR-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            report_date=datetime.utcnow(),
            language=pipeline_input.target_language,
            region_focus=pipeline_input.region_filter[0] if pipeline_input.region_filter else None,
            sections=sections,
            top_stories=[],
            risk_alerts=[
                m.risk
                for m in unique_items
                if m.risk.overall_risk_level.value in ("critical", "high")
            ],
            sentiment_summary="Aggregated sentiment from all analyzed items.",
            scenario_highlights=[m.scenario.base_case.scenario_name for m in unique_items],
            model_used=ModelProvider.OPENAI,
            generation_latency_ms=0,
            metadata={"fallback": True},
        )

    def schedule_daily(self, callback: Callable) -> None:
        """Register a daily scheduled callback."""
        self._schedule_callback = callback

    def stop_schedule(self) -> None:
        """Stop the daily schedule."""
        self._schedule_callback = None

    async def trigger_scheduled(self) -> Optional[DailyReport]:
        """Manually trigger the scheduled callback."""
        if self._schedule_callback is None:
            return None
        result = self._schedule_callback()
        if inspect.isawaitable(result):
            return await result
        return result
