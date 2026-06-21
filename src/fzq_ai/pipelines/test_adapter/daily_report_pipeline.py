"""
FZQ-AI Pipelines — Test Adapter Daily Report Pipeline
Mock DailyReportPipeline. Returns fixed DailyReport in PipelineOutput. No real LLM calls.
"""
from typing import List
from datetime import datetime

from fzq_ai.schemas.test_adapter import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    MultiDimensionAnalysis,
    NarrativeAnalysis,
    RiskAnalysis,
    SentimentAnalysis,
    ScenarioAnalysis,
    DailyReport,
    DailyReportSection,
    ModelProvider,
    LanguageCode,
)


class MockDailyReportPipeline:
    """Mock daily report pipeline. Same interface as real DailyReportPipeline. No real LLM calls."""

    def __init__(self):
        self.pipeline_name = "mock_daily_report_pipeline"

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Return fixed mock PipelineOutput with DailyReport."""
        analyzed_items: List[MultiDimensionAnalysis] = []

        for item in pipeline_input.items[:3]:
            md = MultiDimensionAnalysis(
                news_id=item.id,
                narrative=NarrativeAnalysis(news_id=item.id),
                risk=RiskAnalysis(news_id=item.id),
                sentiment=SentimentAnalysis(news_id=item.id),
                scenario=ScenarioAnalysis(news_id=item.id),
                aggregated_priority_score=0.5,
            )
            analyzed_items.append(md)

        report = DailyReport(
            report_id="mock-daily-report-001",
            report_date=datetime.utcnow(),
            language=LanguageCode.EN,
            sections=[
                DailyReportSection(
                    section_title="Mock Executive Overview",
                    section_type="overview",
                    content="This is a mock daily report for testing.",
                    priority=1,
                ),
                DailyReportSection(
                    section_title="Mock Risk Alerts",
                    section_type="risk_alert",
                    content="No risk alerts in mock mode.",
                    priority=2,
                ),
            ],
            sentiment_summary="Mock sentiment summary: neutral.",
            scenario_highlights=["Mock Base Scenario"],
            model_used=ModelProvider.OPENAI,
            generation_latency_ms=1,
        )

        metrics = PipelineMetrics(
            pipeline_name=self.pipeline_name,
            items_processed=len(analyzed_items),
            items_failed=0,
            avg_latency_ms=1.0,
            total_latency_ms=1.0,
            fallback_count=0,
            translation_count=0,
            timestamp=datetime.utcnow(),
        )

        return PipelineOutput(
            input_summary=pipeline_input,
            analyzed_items=analyzed_items,
            failed_items=[],
            metrics=metrics,
            daily_report=report,
        )
