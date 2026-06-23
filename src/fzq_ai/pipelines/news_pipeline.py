# fzq_ai/pipelines/news_pipeline.py

import asyncio
import uuid
from typing import List

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult, Article


MAX_TRANSLATE_CHARS = 1000


class NewsPipeline(BasePipeline):

    def __init__(self, llm=None):
        self.llm = llm or LLMRouter()
        self._articles: List[Article] = []

    async def run_async(self, *args, query: str = "", topic: str = "", **kwargs) -> ServiceResult:
        return await self._measure("news_pipeline", self._run_impl(query or topic))

    async def _run_impl(self, query: str) -> ServiceResult:
        articles = fetch_all_news(query)
        self._articles = articles

        if not articles:
            return ServiceResult.ok("No relevant news data available.")

        llm_summary = await self._generate_summary_async(query, articles)
        article_list = self._build_article_list(articles)
        result_text = self._compose(llm_summary, article_list, query)

        return ServiceResult.ok(result_text)

    async def _generate_summary_async(self, query: str, articles: List[Article]) -> str:
        context_lines = []
        for i, a in enumerate(articles[:30], 1):
            context_lines.append(f"{i}. [{a.source_name}] {a.title_original}")
        context = "\n".join(context_lines)

        prompt = (
            f"You are a senior intelligence analyst. Below are recently fetched news headlines "
            f"({len(articles)} total):\n\n"
            f"{context}\n\n"
            f"Generate a Chinese intelligence summary for topic: {query}"
        )
        raw = await self.llm.route("news_intel", prompt)
        return raw.strip()

    def _build_article_list(self, articles: List[Article], max_items: int = 30) -> str:
        lines = ["## 📰 Original News List\n"]
        lines.append(f"*{len(articles)} articles fetched, showing top {min(len(articles), max_items)}*\n")
        for i, a in enumerate(articles[:max_items], 1):
            title = a.title_original or "(No title)"
            source = a.source_name or "Unknown source"
            url = a.url or ""
            if url:
                lines.append(f"{i}. **[{source}]** [{title}]({url})")
            else:
                lines.append(f"{i}. **[{source}]** {title}")
            lines.append("")
        return "\n".join(lines)

    def _compose(self, summary: str, article_list: str, query: str) -> str:
        header = f"## 📊 News Intelligence Report: {query}\n\n"
        header += f"*Based on {len(self._articles)} related news articles*\n\n"
        return "\n".join([header, summary, "\n---\n", article_list])
