# fzq_ai/pipelines/news_pipeline.py

import asyncio
from typing import List, Optional

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.formatter import NewsFormatter
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.domain.models import ServiceResult, Article
from fzq_ai.tools.translator import (
    translate_to_chinese,
    translate_to_english,
    is_english_or_chinese,
)
from fzq_ai.storage.intel_store import IntelStore
import uuid

MAX_TRANSLATE_CHARS = 1000


class NewsPipeline:
    """
    Legacy 新闻摘要 Pipeline（保留全部旧功能）
    - P0 修复：fetch_all_news() 只调用一次
    - P0 修复：asyncio.run() 安全化（新增 run_async）
    - P0 修复：返回值统一为 ServiceResult
    """

    def __init__(self, llm=None, llm_router=None):
        self.llm = llm or llm_router or LLMRouter()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为 + 包装 ServiceResult）
    # ---------------------------------------------------------
    def run(self, query: str = "", topic: str = "") -> ServiceResult:
        query = query or topic

        articles = fetch_all_news(query)

        llm_summary = self._generate_summary_sync(query, articles)

        article_list = self._build_article_list(articles, max_items=30)

        try:
            store = IntelStore()
            run_id = str(uuid.uuid4())
            from fzq_ai.domain.models import IntelBundle, IntelMeta
            bundle = IntelBundle(
                meta=IntelMeta(topics=[query], regions=[], depth="normal"),
                articles=articles,
                events=[],
            )
            store.save_bundle(run_id, query, bundle, {"pipeline": "news_pipeline"})
        except Exception:
            pass

        # ⭐ P0‑4：包装为 ServiceResult
        return ServiceResult.ok(
            self._compose(llm_summary, article_list, query, articles)
        )

    # ---------------------------------------------------------
    # 异步入口（新增，不破坏旧逻辑）
    # ---------------------------------------------------------
    async def run_async(self, query: str = "", topic: str = "") -> ServiceResult:
        query = query or topic

        articles = fetch_all_news(query)

        llm_summary = await self._generate_summary_async(query, articles)

        article_list = self._build_article_list(articles, max_items=30)

        try:
            store = IntelStore()
            run_id = str(uuid.uuid4())
            from fzq_ai.domain.models import IntelBundle, IntelMeta
            bundle = IntelBundle(
                meta=IntelMeta(topics=[query], regions=[], depth="normal"),
                articles=articles,
                events=[],
            )
            store.save_bundle(run_id, query, bundle, {"pipeline": "news_pipeline"})
        except Exception:
            pass

        # ⭐ P0‑4：包装为 ServiceResult
        return ServiceResult.ok(
            self._compose(llm_summary, article_list, query, articles)
        )

    # ---------------------------------------------------------
    # 同步摘要（旧逻辑保留）
    # ---------------------------------------------------------
    def _generate_summary_sync(self, query: str, articles: List[Article]) -> str:
        if not articles:
            return "（暂无相关新闻数据）"

        prompt = self._build_prompt(query, articles)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.ensure_future(self.llm.route("news_intel", prompt))
                return ""
            else:
                raw = loop.run_until_complete(self.llm.route("news_intel", prompt))
        except RuntimeError:
            raw = asyncio.run(self.llm.route("news_intel", prompt))

        return raw.strip()

    # ---------------------------------------------------------
    # 异步摘要（新增）
    # ---------------------------------------------------------
    async def _generate_summary_async(self, query: str, articles: List[Article]) -> str:
        if not articles:
            return "（暂无相关新闻数据）"

        prompt = self._build_prompt(query, articles)
        raw = await self.llm.route("news_intel", prompt)
        return raw.strip()

    # ---------------------------------------------------------
    # Prompt 构建（旧逻辑保留）
    # ---------------------------------------------------------
    def _build_prompt(self, query: str, articles: List[Article]) -> str:
        context_lines = []
        for i, a in enumerate(articles[:30], 1):
            context_lines.append(f"{i}. [{a.source_name}] {a.title_original}")

        context = "\n".join(context_lines)

        return (
            f"你是一名资深情报分析师。以下是最近抓取的相关新闻标题列表"
            f"（共 {len(articles)} 篇）：\n\n"
            f"{context}\n\n"
            f"请根据以上新闻标题，生成一份中文情报摘要"
            f"{'（主题：' + query + '）' if query else ''}"
            f"，要求：\n"
            f"1. 用 2-3 个自然段概述核心情报动态\n"
            f"2. 识别主要趋势、关键事件和值得关注的变化\n"
            f"3. 使用专业、客观的情报分析语言\n"
            f"4. 不需要逐条罗列，而是提炼整合"
        )

    # ---------------------------------------------------------
    # 构建原始新闻列表（旧逻辑保留）
    # ---------------------------------------------------------
    def _build_article_list(self, articles: List[Article], max_items: int = 30) -> str:
        if not articles:
            return ""

        lines = ["## 📋 原始新闻列表\n"]
        lines.append(
            f"*共抓取 {len(articles)} 篇相关新闻，"
            f"以下展示前 {min(len(articles), max_items)} 篇*\n"
        )

        for i, a in enumerate(articles[:max_items], 1):
            title = a.title_original or "（无标题）"
            source = a.source_name or "未知来源"
            url = a.url or ""

            if url:
                lines.append(f"{i}. **[{source}]** [{title}]({url})")
            else:
                lines.append(f"{i}. **[{source}]** {title}")

            if not is_english_or_chinese(title) and len(title) > 0:
                en_title = translate_to_english(title[:MAX_TRANSLATE_CHARS])
                zh_title = translate_to_chinese(title[:MAX_TRANSLATE_CHARS])
                lines.append(f"   > 🌐 EN: {en_title}")
                lines.append(f"   > 🇨🇳 CN: {zh_title}")

            lines.append("")

        return "\n".join(lines)

    # ---------------------------------------------------------
    # 组合最终输出（旧逻辑保留 + P0 修复）
    # ---------------------------------------------------------
    def _compose(self, summary: str, article_list: str, query: str, articles: List[Article]) -> str:
        if query:
            header = f"## 📊 新闻情报报告：{query}\n\n"
        else:
            header = "## 📊 新闻情报报告\n\n"

        header += f"*基于 {len(articles)} 篇相关新闻生成*\n\n"

        parts = [header, summary, "\n---\n", article_list]
        return "\n".join(parts)
