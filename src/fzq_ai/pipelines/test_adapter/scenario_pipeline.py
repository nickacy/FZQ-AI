"""
FZQ-AI Pipelines – Test Adapter Scenario Pipeline
Mock ScenarioPipeline. Returns fixed ScenarioAnalysis. No real LLM calls.
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
    ScenarioProjection,
    ModelProvider,
)


class MockScenarioPipeline:
    """Mock scenario pipeline. Same interface as real ScenarioPipeline. No real LLM calls."""

    def __init__(self):
        self.pipeline_name = "mock_scenario_pipeline"

    async def run_async(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Return fixed mock PipelineOutput with ScenarioAnalysis."""
        analyzed_items: List[MultiDimensionAnalysis] = []

        for item in pipeline_input.items[:3]:
            scenario = ScenarioAnalysis(
                news_id=item.id,
                base_case=ScenarioProjection(
                    scenario_name="Mock Base Scenario",
                    description="Mock scenario for testing purposes",
                    probability=0.5,
                    time_horizon="short_term",
                ),
                confidence=1.0,
                model_used=ModelProvider.OPENAI,
            )
            analyzed_items.append(
                MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=NarrativeAnalysis(news_id=item.id),
                    risk=RiskAnalysis(news_id=item.id),
                    sentiment=SentimentAnalysis(news_id=item.id),
                    scenario=scenario,
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
