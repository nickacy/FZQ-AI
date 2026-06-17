# fzq_ai/pipelines/news_pipeline.py

import asyncio
import uuid
from typing import List

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.pipelines.base_pipeline import BasePipeline
from fzq_ai.domain.models import ServiceResult, Article, IntelBundle, IntelMeta


MAX_TRANSLATE_CHARS = 1000


class NewsPipeline(BasePipeline):
    """News intelligence pipeline with LLM summary and article listing."""

    def __init__(self, llm=None):
        self.llm = llm or LLMRouter()
        self._articles: List[Article] = []

    async def _run_async(self, *args, query: str = "", topic: str = "", **kwargs) -> ServiceResult:
        query = query or topic
        articles = fetch_all_news(query)
        self._articles = articles

        if not articles:
            return ServiceResult.ok("No relevant news data available.")

        llm_summary = await self._generate_summary_async(query, articles)
        article_list = self._build_article_list(articles)
        result_text = self._compose(llm_summary, article_list, query)

        return ServiceResult.ok(result_text)

    async def _generate_summary_async(self, query: str, articles: List[Article]) -> str:
        if not articles:
            return "No relevant news data available."

        context_lines = []
        for i, a in enumerate(articles[:30], 1):
            context_lines.append(f"{i}. [{a.source_name}] {a.title_original}")
        context = "\n".join(context_lines)

        prompt = (
            f"You are a senior intelligence analyst. Below are recently fetched news headlines "
            f"({len(articles)} total):\n\n"
            f"{context}\n\n"
            f"Based on the above headlines, generate a Chinese intelligence summary "
            f"{'(Topic: ' + query + ')' if query else ''}:\n"
            f"1. Summarize core intelligence dynamics in 2-3 natural paragraphs\n"
            f"2. Identify key trends, events, and noteworthy changes\n"
            f"3. Use professional, objective intelligence analysis language\n"
            f"4. Synthesize rather than list items individually"
        )
        raw = await self.llm.route("news_intel", prompt)
        return raw.strip()

    def _build_article_list(self, articles: List[Article], max_items: int = 30) -> str:
        if not articles:
            return ""
        lines = ["## \U0001f4f0 Original News List\n"]
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
        header = f"## \U0001f4ca News Intelligence Report: {query}\n\n" if query else "## \U0001f4ca News Intelligence Report\n\n"
        header += f"*Based on {len(self._articles)} related news articles*\n\n"
        return "\n".join([header, summary, "\n---\n", article_list])
