# fzq_ai/pipelines/narrative_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate


SUMMARY_TEMPLATE = PromptTemplate(
    """
你是一名新闻叙事分析专家，请根据以下主题生成简短摘要：

主题：$query
"""
)

KEYPOINTS_TEMPLATE = PromptTemplate(
    """
请根据以下主题生成 5 条关键要点：

主题：$query
"""
)

STORYLINE_TEMPLATE = PromptTemplate(
    """
请根据以下主题生成一条清晰的叙事线（storyline）：

主题：$query
"""
)

IMPLICATIONS_TEMPLATE = PromptTemplate(
    """
请根据以下主题分析未来 30 天的潜在影响：

主题：$query
"""
)


class NarrativePipeline:
    """
    NarrativePipeline（增强版）
    - 保留旧行为（同步 run）
    - 新增 async run_async（并发执行 narrative 子任务）
    """

    def __init__(self):
        self.llm = LLMRouter()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为）
    # ---------------------------------------------------------
    def run(self, query: str):
        summary = asyncio.run(self.llm.route("narrative_summary", SUMMARY_TEMPLATE.render(query=query)))
        key_points = asyncio.run(self.llm.route("narrative_keypoints", KEYPOINTS_TEMPLATE.render(query=query)))
        storyline = asyncio.run(self.llm.route("narrative_storyline", STORYLINE_TEMPLATE.render(query=query)))
        implications = asyncio.run(self.llm.route("narrative_implications", IMPLICATIONS_TEMPLATE.render(query=query)))

        return {
            "summary": summary,
            "key_points": key_points,
            "storyline": storyline,
            "implications": implications,
        }

    # ---------------------------------------------------------
    # 异步入口（并发执行 narrative 子任务）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        tasks = [
            self.llm.route("narrative_summary", SUMMARY_TEMPLATE.render(query=query)),
            self.llm.route("narrative_keypoints", KEYPOINTS_TEMPLATE.render(query=query)),
            self.llm.route("narrative_storyline", STORYLINE_TEMPLATE.render(query=query)),
            self.llm.route("narrative_implications", IMPLICATIONS_TEMPLATE.render(query=query)),
        ]

        summary, key_points, storyline, implications = await asyncio.gather(*tasks)

        return {
            "summary": summary,
            "key_points": key_points,
            "storyline": storyline,
            "implications": implications,
        }
