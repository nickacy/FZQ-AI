# fzq_ai/pipelines/news_pipeline.py

from typing import List

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.formatter import NewsFormatter
from fzq_ai.pipelines.news_fetcher import fetch_all_news
from fzq_ai.domain.models import Article
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

    def __init__(self, llm=None):
        self.llm = llm or LLMRouter()

    def run(self, query: str = "") -> str:
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

    def _generate_summary(self, query: str, articles: List[Article]) -> str:
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
        raw = self.llm.run(prompt)
        return raw.strip()

    def _build_article_list(
        self, articles: List[Article], max_items: int = 30
    ) -> str:
        """构建原始新闻列表（Markdown 格式），非英/中文文章附带翻译"""
        if not articles:
            return ""

        lines = ["## 📋 原始新闻列表\n"]
        lines.append(
            f"*共抓取 {len(articles)} 篇相关新闻，"
            f"以下展示前 {min(len(articles), max_items)} 篇*\n"
        )

        for i, a in enumerate(articles[:max_items], 1):
            # 文章标题和来源
            source_label = a.source_name or "未知来源"
            region_label = f" [{a.region}]" if a.region else ""
            language_label = f" ({a.language})" if a.language else ""

            lines.append(f"### {i}. {a.title_original}")
            lines.append(f"**来源**: {source_label}{region_label}{language_label}")

            if a.url:
                lines.append(f"**链接**: [{a.url}]({a.url})")

            # 内容摘要 / 首段
            content = (a.content_original or "").strip()
            if content:
                truncated = content[:MAX_TRANSLATE_CHARS]
                if len(content) > MAX_TRANSLATE_CHARS:
                    truncated += "..."

                # 如果非英非中文，提供中英文翻译
                if not is_english_or_chinese(truncated):
                    lines.append("")
                    en_trans = translate_to_english(truncated)
                    zh_trans = translate_to_chinese(truncated)

                    lines.append(
                        f"<details>\n"
                        f"<summary>🌐 原文翻译（非英/中文）</summary>\n\n"
                        f"**🇬🇧 English**:\n{en_trans}\n\n"
                        f"**🇨🇳 中文**:\n{zh_trans}\n"
                        f"</details>"
                    )

            lines.append("")

        return "\n".join(lines)

    def _compose(
        self, summary: str, article_list: str, query: str
    ) -> str:
        """组合最终输出"""
        header = "## 📰 新闻情报分析"
        if query:
            header += f"：{query}"

        parts = [
            header,
            "",
            "### 📊 情报摘要",
            "",
            summary,
            "",
            "---",
            "",
            article_list,
            "",
            "---",
            "",
            "*由 FZQ-AI 自动生成（RSS + NewsAPI + GDELT + LLM 分析）*",
        ]
        return "\n".join(parts)
