# fzq_ai/pipelines/sentiment_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate


SENTIMENT_SCORE_TEMPLATE = PromptTemplate(
    """
请根据以下主题给出情绪倾向评分（-1 到 +1）：

主题：$query
"""
)

SENTIMENT_SUMMARY_TEMPLATE = PromptTemplate(
    """
请根据以下主题生成情绪倾向总结（正面/中性/负面）并说明原因：

主题：$query
"""
)


class SentimentPipeline:
    """
    SentimentPipeline（增强版）
    - 保留旧行为（同步 run）
    - 新增 async run_async（并发执行 sentiment 子任务）
    """

    def __init__(self):
        self.llm = LLMRouter()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为）
    # ---------------------------------------------------------
    def run(self, query: str):
        score = asyncio.run(self.llm.route("sentiment_score", SENTIMENT_SCORE_TEMPLATE.render(query=query)))
        summary = asyncio.run(self.llm.route("sentiment_summary", SENTIMENT_SUMMARY_TEMPLATE.render(query=query)))

        return {
            "score": score,
            "summary": summary,
        }

    # ---------------------------------------------------------
    # 异步入口（并发执行 sentiment 子任务）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        tasks = [
            self.llm.route("sentiment_score", SENTIMENT_SCORE_TEMPLATE.render(query=query)),
            self.llm.route("sentiment_summary", SENTIMENT_SUMMARY_TEMPLATE.render(query=query)),
        ]

        score, summary = await asyncio.gather(*tasks)

        return {
            "score": score,
            "summary": summary,
        }
