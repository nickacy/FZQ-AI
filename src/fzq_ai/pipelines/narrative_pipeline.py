# fzq_ai/pipelines/narrative_pipeline.py
# v13 NarrativePipeline 鈥?淇濈暀鍘熶笟鍔￠€昏緫 + 杞婚噺瀵归綈 v13

from __future__ import annotations

import asyncio

from fzq_ai.llm.router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.domain.models import ServiceResult


SUMMARY_TEMPLATE = PromptTemplate("""
You are a news narrative analysis expert. Generate a concise summary for the following topic:

Topic: $query
""")

KEYPOINTS_TEMPLATE = PromptTemplate("""
Generate 5 key points for the following topic:

Topic: $query
""")

STORYLINE_TEMPLATE = PromptTemplate("""
Generate a clear storyline for the following topic:

Topic: $query
""")

IMPLICATIONS_TEMPLATE = PromptTemplate("""
Analyze the potential implications for the next 30 days for the following topic:

Topic: $query
""")


@PipelineRegistry.register("narrative@v1", set_default=True)
class NarrativePipeline(BasePipeline):
    """Narrative analysis with concurrent sub-tasks."""

    name = "narrative"

    def __init__(self):
        self.llm = LLMRouter()

    async def run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        tasks = [
            self.llm.route("narrative_summary", SUMMARY_TEMPLATE.render(query=query)),
            self.llm.route("narrative_keypoints", KEYPOINTS_TEMPLATE.render(query=query)),
            self.llm.route("narrative_storyline", STORYLINE_TEMPLATE.render(query=query)),
            self.llm.route("narrative_implications", IMPLICATIONS_TEMPLATE.render(query=query)),
        ]

        summary, key_points, storyline, implications = await asyncio.gather(*tasks)

        return ServiceResult.ok({
            "summary": summary,
            "key_points": key_points,
            "storyline": storyline,
            "implications": implications,
        })

