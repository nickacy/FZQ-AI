# fzq_ai/pipelines/sentiment_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult


SENTIMENT_SCORE_TEMPLATE = PromptTemplate("""
Give a sentiment score (-1 to +1) for the following topic:

Topic: $query
""")

SENTIMENT_SUMMARY_TEMPLATE = PromptTemplate("""
Generate a sentiment tendency summary (positive/neutral/negative) and explain why:

Topic: $query
""")


class SentimentPipeline(BasePipeline):
    """Sentiment analysis with concurrent sub-tasks."""

    def __init__(self):
        self.llm = LLMRouter()

    async def _run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        tasks = [
            self.llm.route("sentiment_score", SENTIMENT_SCORE_TEMPLATE.render(query=query)),
            self.llm.route("sentiment_summary", SENTIMENT_SUMMARY_TEMPLATE.render(query=query)),
        ]
        score, summary = await asyncio.gather(*tasks)
        return ServiceResult.ok({
            "score": score,
            "summary": summary,
        })
