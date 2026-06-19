"""
FZQ-AI Orchestrator — Test Adapter Task Orchestrator
MockTaskOrchestrator. Same interface as real TaskOrchestrator. No real pipeline calls.
No concurrency. Returns fixed DailyReport with 1 section and 1 story.
Sync methods (run() returns DailyReport directly, not awaitable).
Has schedule_daily(callback), stop_schedule(), trigger_scheduled().
"""
from typing import Optional, Callable, List
from datetime import datetime

from fzq_ai.schemas.test_adapter import (
    PipelineInput,
    DailyReport,
    DailyReportSection,
    RawNewsItem,
    NewsSource,
    LanguageCode,
    RegionCode,
    ModelProvider,
)


class MockTaskOrchestrator:
    """Mock task orchestrator. Same interface as real TaskOrchestrator. No real pipeline calls."""

    def __init__(self):
        self._schedule_callback: Optional[Callable] = None

    def run(self, pipeline_input: PipelineInput) -> DailyReport:
        """Return a fixed DailyReport with 1 section and 1 story."""
        section = DailyReportSection(
            section_title="Mock Daily Section",
            section_type="overview",
            content="This is a mock daily report section for testing.",
            priority=1,
        )
        story = RawNewsItem(
            id="mock-story-1",
            title="Mock Top Story",
            content="Mock story content for testing purposes.",
            source=NewsSource(name="Mock Source"),
            published_at=datetime.utcnow(),
            language=LanguageCode.EN,
            region=RegionCode.GLOBAL,
        )
        return DailyReport(
            report_id="MOCK-DR-001",
            report_date=datetime.utcnow(),
            language=LanguageCode.EN,
            region_focus=pipeline_input.region_filter[0] if pipeline_input.region_filter else None,
            sections=[section],
            top_stories=[story],
            model_used=ModelProvider.OPENAI,
            generation_latency_ms=1,
            metadata={"mock": True},
        )

    def run_daily(self, topic: str = '', news_raw_texts: Optional[List[str]] = None) -> DailyReport:
        """Return a fixed DailyReport for daily runs."""
        return self.run(PipelineInput())

    def schedule_daily(self, callback: Callable) -> None:
        """Register a daily scheduled callback."""
        self._schedule_callback = callback

    def stop_schedule(self) -> None:
        """Stop the daily schedule."""
        self._schedule_callback = None

    def trigger_scheduled(self) -> Optional[DailyReport]:
        """Manually trigger the scheduled callback with a mock report."""
        if self._schedule_callback is None:
            return None
        report = self.run(PipelineInput())
        self._schedule_callback(report)
        return report
