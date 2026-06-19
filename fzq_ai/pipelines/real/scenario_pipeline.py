"""Scenario pipeline: LLM-driven scenario analysis."""
import time
from datetime import datetime
from typing import List, Dict, Any

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    MultiDimensionAnalysis,
    ScenarioAnalysis,
    ScenarioProjection,
    ModelProvider,
    LLMRequest,
)
from fzq_ai.llm.real.llm_router import LLMRouter


class ScenarioPipeline:
    """Async scenario analysis pipeline using LLM prompts."""

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Run scenario analysis on the given input items."""
        start = time.perf_counter()
        metrics = PipelineMetrics(pipeline_name="scenario_pipeline")
        analyzed_items: List[MultiDimensionAnalysis] = []
        failed_items: List[Dict[str, Any]] = []

        items = pipeline_input.items[: pipeline_input.max_items]
        for item in items:
            try:
                text = f"{item.title}\n{item.content}"
                prompt = (
                    "You are a scenario planner. Based on the following news article, project "
                    "base case, optimistic case, and pessimistic case scenarios.\n\n"
                    f"{text[:4000]}\n\n"
                    "Return your analysis as a structured JSON-like response with:\n"
                    "- base_case: object with scenario_name, description, probability, key_triggers, expected_outcomes, time_horizon\n"
                    "- optimistic_case: same structure\n"
                    "- pessimistic_case: same structure\n"
                    "- alternative_scenarios: list of scenario objects"
                )
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.OPENAI,
                    temperature=0.3,
                    max_tokens=2500,
                )
                response = await self.llm_router.generate(request)

                scenario = ScenarioAnalysis(
                    news_id=item.id,
                    base_case=ScenarioProjection(
                        scenario_name="Base Case",
                        description=response.content[:1000],
                        probability=0.5,
                        time_horizon="medium_term",
                    ),
                    confidence=0.65,
                    model_used=response.provider,
                    processed_at=datetime.utcnow(),
                )
                analysis = MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=None,  # type: ignore[arg-type]
                    risk=None,  # type: ignore[arg-type]
                    sentiment=None,  # type: ignore[arg-type]
                    scenario=scenario,
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
