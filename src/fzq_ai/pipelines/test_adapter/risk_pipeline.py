"""
FZQ-AI Pipelines – Test Adapter Risk Pipeline
Mock RiskPipeline. Returns fixed RiskAnalysis with MEDIUM risk. No real LLM calls.
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
    RiskFactor,
    RiskLevel,
    SentimentAnalysis,
    ScenarioAnalysis,
    ModelProvider,
)


class MockRiskPipeline:
    """Mock risk pipeline. Same interface as real RiskPipeline. No real LLM calls."""

    def __init__(self):
        self.pipeline_name = "mock_risk_pipeline"

    async def run_async(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Return fixed mock PipelineOutput with RiskAnalysis (MEDIUM risk)."""
        analyzed_items: List[MultiDimensionAnalysis] = []

        for item in pipeline_input.items[:3]:
            risk = RiskAnalysis(
                news_id=item.id,
                overall_risk_level=RiskLevel.MEDIUM,
                composite_risk_score=0.4,
                risk_factors=[
                    RiskFactor(
                        risk_type="mock_risk",
                        description="Mock risk factor for testing",
                        level=RiskLevel.MEDIUM,
                        probability=0.4,
                        impact_score=0.4,
                    )
                ],
                confidence=1.0,
                model_used=ModelProvider.OPENAI,
            )
            analyzed_items.append(
                MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=NarrativeAnalysis(news_id=item.id),
                    risk=risk,
                    sentiment=SentimentAnalysis(news_id=item.id),
                    scenario=ScenarioAnalysis(news_id=item.id),
                    aggregated_priority_score=0.4,
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
