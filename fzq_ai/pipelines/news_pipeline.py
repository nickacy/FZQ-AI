# fzq_ai/pipelines/news_pipeline.py

import asyncio
from typing import List

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.formatter import NewsFormatter
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.domain.models import ServiceResult,  Article
from fzq_ai.tools.translator import (
    translate_to_chinese,
    translate_to_english,
    is_english_or_chinese,
)

# 每个文章翻译时取的最大字符数（约前 10 行）
MAX_TRANSLATE_CHARS = 1000


class NewsPipeline:
    """
    新闻摘要 Pipeline（增强版）
    - 抓取真实新闻文章（RSS + NewsAPI + GDELT）
    - 调用 LLM 生成情报摘要
    - 生成原始新闻列表（含链接）
    - 非英/中文文章自动提供中英文翻译
    - 测试时可注入 mock_llm
    """

    def __init__(self, llm=None, llm_router=None):
        self.llm = llm or llm_router or LLMRouter()

    def run(self, query: str = "") -> ServiceResult:
        """
        执行新闻情报分析流程：
        1. 抓取相关新闻文章
        2. LLM 生成情报摘要（含文章上下文）
        3. 构建原文列表（含链接 + 翻译）
        """
        articles = fetch_all_news(query)

        # 1. LLM 摘要（传入文章标题列表作为上下文）
        llm_summary = self._generate_summary(query, articles)

        # 2. 构建原文列表
        article_list = self._build_article_list(articles, max_items=30)

        # 3. 组合最终输出
        return self._compose(llm_summary, article_list, query)

    # ── 私有方法 ──────────────────────────────────────────

    def _generate_summary(self, query: str, articles: List[Article]) -> ServiceResult:
        """调用 LLM 生成新闻情报摘要"""
        if not articles:
            return "（暂无相关新闻数据）"

        # 构建文章上下文（标题 + 来源）
        context_lines = []
        for i, a in enumerate(articles[:30], 1):
            context_lines.append(
                f"{i}. [{a.source_name}] {a.title_original}"
            )

        context = "\n".join(context_lines)
        prompt = (
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
        raw = asyncio.run(self.llm.run(prompt))
        return raw.strip()

    def _build_article_list(
        self, articles: List[Article], max_items: int = 30
    ) -> ServiceResult:
        """构建原始新闻列表（Markdown 格式），非英/中文文章附带翻译"""
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
            lang = a.language or ""

            # 标题行（带链接）
            if url:
                lines.append(f"{i}. **[{source}]** [{title}]({url})")
            else:
                lines.append(f"{i}. **[{source}]** {title}")

            # 翻译（非英/中文文章）
            if not is_english_or_chinese(title) and len(title) > 0:
                en_title = translate_to_english(title[:MAX_TRANSLATE_CHARS])
                zh_title = translate_to_chinese(title[:MAX_TRANSLATE_CHARS])
                lines.append(f"   > 🌐 EN: {en_title}")
                lines.append(f"   > 🇨🇳 CN: {zh_title}")

            lines.append("")  # 空行

        return "\n".join(lines)

    def _compose(self, summary: str, article_list: str, query: str) -> ServiceResult:
        """组合最终输出"""
        if query:
            header = f"## 📊 新闻情报报告：{query}\n\n"
        else:
            header = "## 📊 新闻情报报告\n\n"

        header += f"*基于 {sum(1 for a in fetch_all_news(query) if True)} 篇相关新闻生成*\n\n"

        parts = [header, summary, "\n---\n", article_list]
        return "\n".join(parts)
