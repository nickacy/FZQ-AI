"""
FZQ-AI Pipelines – Test Adapter News Pipeline
Mock NewsPipeline. Same interface as real NewsPipeline. Async run_async() → PipelineOutput.
No real fetching. No translation. Returns fixed mock data with up to 3 dummy
MultiDimensionAnalysis items.
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
)


class MockNewsPipeline:
    """Mock news pipeline. Same interface as real NewsPipeline. No real fetching or translation."""

    def __init__(self):
        self.pipeline_name = "mock_news_pipeline"

    async def run_async(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Return fixed mock PipelineOutput with up to 3 dummy MultiDimensionAnalysis items."""
        analyzed_items: List[MultiDimensionAnalysis] = []

        source_items = pipeline_input.items[:3] if pipeline_input.items else []
        if not source_items:
            for i in range(3):
                news_id = f"mock-news-{i + 1}"
                analyzed_items.append(
                    MultiDimensionAnalysis(
                        news_id=news_id,
                        narrative=NarrativeAnalysis(news_id=news_id),
                        risk=RiskAnalysis(news_id=news_id),
                        sentiment=SentimentAnalysis(news_id=news_id),
                        scenario=ScenarioAnalysis(news_id=news_id),
                        aggregated_priority_score=0.5,
                    )
                )
        else:
            for item in source_items:
                analyzed_items.append(
                    MultiDimensionAnalysis(
                        news_id=item.id,
                        narrative=NarrativeAnalysis(news_id=item.id),
                        risk=RiskAnalysis(news_id=item.id),
                        sentiment=SentimentAnalysis(news_id=item.id),
                        scenario=ScenarioAnalysis(news_id=item.id),
                        aggregated_priority_score=0.5,
                    )
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
        )
