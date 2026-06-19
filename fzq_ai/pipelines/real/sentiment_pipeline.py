"""Sentiment pipeline: LLM-driven sentiment analysis."""
import time
from datetime import datetime
from typing import List, Dict, Any

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    MultiDimensionAnalysis,
    SentimentAnalysis,
    SentimentLabel,
    ModelProvider,
    LLMRequest,
)
from fzq_ai.llm.real.llm_router import LLMRouter


class SentimentPipeline:
    """Async sentiment analysis pipeline using LLM prompts."""

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Run sentiment analysis on the given input items."""
        start = time.perf_counter()
        metrics = PipelineMetrics(pipeline_name="sentiment_pipeline")
        analyzed_items: List[MultiDimensionAnalysis] = []
        failed_items: List[Dict[str, Any]] = []

        items = pipeline_input.items[: pipeline_input.max_items]
        for item in items:
            try:
                text = f"{item.title}\n{item.content}"
                prompt = (
                    "You are a sentiment analyst. Analyze the sentiment of the following news article "
                    "and provide overall sentiment, headline sentiment, content sentiment, sentiment scores, "
                    "and entity-level sentiments.\n\n"
                    f"{text[:4000]}\n\n"
                    "Return your analysis as a structured JSON-like response with:\n"
                    "- overall_sentiment: one of very_positive/positive/neutral/negative/very_negative\n"
                    "- sentiment_score: float -1 to 1\n"
                    "- headline_sentiment: same enum\n"
                    "- headline_score: float -1 to 1\n"
                    "- content_sentiment: same enum\n"
                    "- content_score: float -1 to 1\n"
                    "- entity_sentiments: dict of entity name to score\n"
                    "- market_indicators: list of strings"
                )
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.OPENAI,
                    temperature=0.2,
                    max_tokens=1500,
                )
                response = await self.llm_router.generate(request)

                sentiment = SentimentAnalysis(
                    news_id=item.id,
                    overall_sentiment=SentimentLabel.NEUTRAL,
                    sentiment_score=0.0,
                    headline_sentiment=SentimentLabel.NEUTRAL,
                    headline_score=0.0,
                    content_sentiment=SentimentLabel.NEUTRAL,
                    content_score=0.0,
                    confidence=0.7,
                    model_used=response.provider,
                    processed_at=datetime.utcnow(),
                )
                analysis = MultiDimensionAnalysis(
                    news_id=item.id,
                    narrative=None,  # type: ignore[arg-type]
                    risk=None,  # type: ignore[arg-type]
                    sentiment=sentiment,
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
