"""Narrative pipeline: LLM-driven narrative analysis."""
import time
from datetime import datetime
from typing import List, Dict, Any

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    MultiDimensionAnalysis,
    NarrativeAnalysis,
    ModelProvider,
    LLMRequest,
    AnalysisDimension,
)
from fzq_ai.llm.real.llm_router import LLMRouter


class NarrativePipeline:
    """Async narrative analysis pipeline using LLM prompts."""

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Run narrative analysis on the given input items."""
        start = time.perf_counter()
        metrics = PipelineMetrics(pipeline_name="narrative_pipeline")
        analyzed_items: List[MultiDimensionAnalysis] = []
        failed_items: List[Dict[str, Any]] = []

        items = pipeline_input.items[: pipeline_input.max_items]
        for item in items:
            try:
                text = f"{item.title}\n{item.content}"
                prompt = (
                    "You are a geopolitical narrative analyst. Analyze the following news article "
                    "and extract its primary narrative, secondary narratives, key actors, key themes, "
                    "timeline indicators, and related events.\n\n"
                    f"{text[:4000]}\n\n"
                    "Return your analysis as a structured JSON-like response with the following fields:\n"
                    "- primary_narrative: string\n"
                    "- secondary_narratives: list of strings\n"
                    "- narrative_strength: float 0-1\n"
                    "- key_actors: list of strings\n"
                    "- key_themes: list of strings\n"
                    "- timeline_indicators: list of strings\n"
                    "- related_events: list of strings"
                )
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.OPENAI,
                    temperature=0.2,
                    max_tokens=2000,
                )
                response = await self.llm_router.generate(request)

                narrative = NarrativeAnalysis(
                    news_id=item.id,
                    primary_narrative=response.content[:1000],
                    narrative_strength=0.75,
                    confidence=0.75,
                    model_used=response.provider,
                    processed_at=datetime.utcnow(),
                )
                analysis = MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=narrative,
                    risk=None,  # type: ignore[arg-type]
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
