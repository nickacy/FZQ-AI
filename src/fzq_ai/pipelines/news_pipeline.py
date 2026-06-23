# fzq_ai/pipelines/news_pipeline.py
# v13 NewsPipeline – 保留原业务逻辑 + 统一 v13 Pipeline 接口

from __future__ import annotations

from typing import List, Dict, Any

from fzq_ai.llm.router import Router
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult, Article


MAX_TRANSLATE_CHARS = 1000


class NewsPipeline(BasePipeline):
    name = "news"

    def __init__(self):
        self.router = Router()
        self._articles: List[Article] = []

    # ---------------------------------------------------------
    # v13 preprocess：构造 prompt + 设置 task_type
    # ---------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        query = req.get("query") or req.get("topic") or req.get("input", "")

        # 1. 拉取新闻
        articles = fetch_all_news(query)
        self._articles = articles

        if not articles:
            req["prompt"] = "No relevant news data available."
            req["task_type"] = "analysis"
            return req

        # 2. 构造新闻标题上下文
        context_lines = []
        for i, a in enumerate(articles[:30], 1):
            context_lines.append(f"{i}. [{a.source_name}] {a.title_original}")
        context = "\n".join(context_lines)

        # 3. 构造 prompt（保留你原来的业务逻辑）
        prompt = (
            f"You are a senior intelligence analyst. Below are recently fetched news headlines "
            f"({len(articles)} total):\n\n"
            f"{context}\n\n"
            f"Generate a Chinese intelligence summary for topic: {query}"
        )

        req["prompt"] = prompt
        req["task_type"] = "analysis"
        return req

    # ---------------------------------------------------------
    # v13 postprocess：结构化输出
    # ---------------------------------------------------------
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        result = {
            "output": "...",
            "provider": "...",
            "model": "...",
            ...
        }
        """

        summary = result.get("output", "")
        article_list = self._build_article_list(self._articles)

        final_text = self._compose(summary, article_list)

        return {
            "summary": summary,
            "articles": article_list,
            "provider": result.get("provider"),
            "model": result.get("model"),
            "final_text": final_text,
        }

    # ---------------------------------------------------------
    # 保留你原来的业务逻辑（文章列表）
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 保留你原来的业务逻辑（最终组合）
    # ---------------------------------------------------------
    def _compose(self, summary: str, article_list: str) -> str:
        header = f"## 📊 News Intelligence Report\n\n"
        header += f"*Based on {len(self._articles)} related news articles*\n\n"
        return "\n".join([header, summary, "\n---\n", article_list])
