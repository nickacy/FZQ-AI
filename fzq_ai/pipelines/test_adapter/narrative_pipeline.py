"""
FZQ-AI Pipelines — Test Adapter Narrative Pipeline
Mock NarrativePipeline. Same interface. Returns fixed NarrativeAnalysis. No real LLM calls.
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
    ModelProvider,
)


class MockNarrativePipeline:
    """Mock narrative pipeline. Same interface as real NarrativePipeline. No real LLM calls."""

    def __init__(self):
        self.pipeline_name = "mock_narrative_pipeline"

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Return fixed mock PipelineOutput with NarrativeAnalysis."""
        analyzed_items: List[MultiDimensionAnalysis] = []

        for item in pipeline_input.items[:3]:
            narrative = NarrativeAnalysis(
                news_id=item.id,
                primary_narrative="Mock primary narrative for testing",
                secondary_narratives=["Mock secondary narrative"],
                narrative_strength=0.5,
                key_actors=["Mock Actor A"],
                key_themes=["Mock Theme A"],
                confidence=1.0,
                model_used=ModelProvider.OPENAI,
            )
            analyzed_items.append(
                MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=narrative,
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
