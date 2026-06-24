# fzq_ai/pipelines/news_pipeline.py
# v13 NewsPipeline 鈥?淇濈暀鍘熶笟鍔￠€昏緫 + 缁熶竴 v13 Pipeline 鎺ュ彛

from __future__ import annotations

from typing import List, Dict, Any

from fzq_ai.llm.router import Router
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.pipelines.registry import PipelineRegistry
from fzq_ai.domain.models import ServiceResult, Article


MAX_TRANSLATE_CHARS = 1000


@PipelineRegistry.register("news@v1", set_default=True)
class NewsPipeline(BasePipeline):
    name = "news"

    def __init__(self):
        self.router = Router()
        self._articles: List[Article] = []

    # ---------------------------------------------------------
    # v13 preprocess锛氭瀯閫?prompt + 璁剧疆 task_type
    # ---------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        query = req.get("query") or req.get("topic") or req.get("input", "")

        # 1. 鎷夊彇鏂伴椈
        articles = fetch_all_news(query)
        self._articles = articles

        if not articles:
            req["prompt"] = "No relevant news data available."
            req["task_type"] = "analysis"
            return req

        # 2. 鏋勯€犳柊闂绘爣棰樹笂涓嬫枃
        context_lines = []
        for i, a in enumerate(articles[:30], 1):
            context_lines.append(f"{i}. [{a.source_name}] {a.title_original}")
        context = "\n".join(context_lines)

        # 3. 鏋勯€?prompt锛堜繚鐣欎綘鍘熸潵鐨勪笟鍔￠€昏緫锛?
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
    # v13 postprocess锛氱粨鏋勫寲杈撳嚭
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
    # 淇濈暀浣犲師鏉ョ殑涓氬姟閫昏緫锛堟枃绔犲垪琛?級
    # ---------------------------------------------------------
    def _build_article_list(self, articles: List[Article], max_items: int = 30) -> str:
        lines = ["## 馃摪 Original News List\n"]
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
    # 淇濈暀浣犲師鏉ョ殑涓氬姟閫昏緫锛堟渶缁堢粍鍚堬級
    # ---------------------------------------------------------
    def _compose(self, summary: str, article_list: str) -> str:
        header = f"## 馃搳 News Intelligence Report\n\n"
        header += f"*Based on {len(self._articles)} related news articles*\n\n"
        return "\n".join([header, summary, "\n---\n", article_list])

