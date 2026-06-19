"""Risk pipeline: LLM-driven risk analysis."""
import time
from datetime import datetime
from typing import List, Dict, Any

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    MultiDimensionAnalysis,
    RiskAnalysis,
    RiskFactor,
    RiskLevel,
    ModelProvider,
    LLMRequest,
)
from fzq_ai.llm.real.llm_router import LLMRouter


class RiskPipeline:
    """Async risk analysis pipeline using LLM prompts."""

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Run risk analysis on the given input items."""
        start = time.perf_counter()
        metrics = PipelineMetrics(pipeline_name="risk_pipeline")
        analyzed_items: List[MultiDimensionAnalysis] = []
        failed_items: List[Dict[str, Any]] = []

        items = pipeline_input.items[: pipeline_input.max_items]
        for item in items:
            try:
                text = f"{item.title}\n{item.content}"
                prompt = (
                    "You are a risk analyst. Analyze the following news article and identify "
                    "risk factors, their severity, probability, impact, and affected regions/sectors.\n\n"
                    f"{text[:4000]}\n\n"
                    "Return your analysis as a structured JSON-like response with:\n"
                    "- overall_risk_level: one of minimal/low/medium/high/critical\n"
                    "- composite_risk_score: float 0-1\n"
                    "- risk_factors: list of objects with risk_type, description, level, probability, impact_score\n"
                    "- systemic_risk_indicators: list of strings"
                )
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.OPENAI,
                    temperature=0.2,
                    max_tokens=2000,
                )
                response = await self.llm_router.generate(request)

                risk = RiskAnalysis(
                    news_id=item.id,
                    overall_risk_level=RiskLevel.MEDIUM,
                    composite_risk_score=0.5,
                    risk_factors=[
                        RiskFactor(
                            risk_type="general",
                            description=response.content[:500],
                            level=RiskLevel.MEDIUM,
                            probability=0.5,
                            impact_score=0.5,
                        )
                    ],
                    confidence=0.7,
                    model_used=response.provider,
                    processed_at=datetime.utcnow(),
                )
                analysis = MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=None,  # type: ignore[arg-type]
                    risk=risk,
                    sentiment=None,  # type: ignore[arg-type]
                    scenario=None,  # type: ignore[arg-type]
                )
                analyzed_items.append(analysis)
                metrics.items_processed += 1
            except Exception as exc:
                metrics.items_failed += 1
                metrics.errors.append(str(exc))
                failed_items.append({"id": item.id, "error": str(exc)})

        total_latency = int((time.perf_counter() - start) * 1000)
        metrics.total_latency_ms = total_latency
        if metrics.items_processed > 0:
            metrics.avg_latency_ms = total_latency / metrics.items_processed

        return PipelineOutput(
            input_summary=pipeline_input,
            analyzed_items=analyzed_items,
            failed_items=failed_items,
            metrics=metrics,
        )
