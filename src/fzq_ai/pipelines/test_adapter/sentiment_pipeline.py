"""
FZQ-AI Pipelines – Test Adapter Sentiment Pipeline
Mock SentimentPipeline. Returns fixed SentimentAnalysis with NEUTRAL. No real LLM calls.
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
    SentimentLabel,
    ScenarioAnalysis,
    ModelProvider,
)


class MockSentimentPipeline:
    """Mock sentiment pipeline. Same interface as real SentimentPipeline. No real LLM calls."""

    def __init__(self):
        self.pipeline_name = "mock_sentiment_pipeline"

    async def run_async(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Return fixed mock PipelineOutput with SentimentAnalysis (NEUTRAL)."""
        analyzed_items: List[MultiDimensionAnalysis] = []

        for item in pipeline_input.items[:3]:
            sentiment = SentimentAnalysis(
                news_id=item.id,
                overall_sentiment=SentimentLabel.NEUTRAL,
                sentiment_score=0.0,
                headline_sentiment=SentimentLabel.NEUTRAL,
                headline_score=0.0,
                content_sentiment=SentimentLabel.NEUTRAL,
                content_score=0.0,
                confidence=1.0,
                model_used=ModelProvider.OPENAI,
            )
            analyzed_items.append(
                MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=NarrativeAnalysis(news_id=item.id),
                    risk=RiskAnalysis(news_id=item.id),
                    sentiment=sentiment,
                    scenario=ScenarioAnalysis(news_id=item.id),
                    aggregated_priority_score=0.0,
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
