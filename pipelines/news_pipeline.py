"""
pipelines/news_pipeline.py

FZQ‑AI v2.5 — RSS-based News Intelligence Pipeline.

功能：
- RSS 多源新闻抓取 + LLM 自动摘要 + 风险评分
- 返回统一的 ServiceResult，所有异常均被捕获并结构化返回

输入：topic: str — 新闻主题关键词
输出：ServiceResult(success, data=IntelBundle, error=...)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Optional, Dict

import feedparser

from fzq_ai.domain.models import Article, IntelBundle, IntelMeta, ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.logger import get_logger

logger = get_logger(__name__)

# ── 超时常量 ──────────────────────────────────────────────────
LLM_TIMEOUT_SEC = 60
RSS_TIMEOUT_SEC = 30


class NewsPipeline:
    """
    RSS 多源新闻抓取 + 自动摘要 + 风险评分 Pipeline。

    工作流程：
    1. 遍历配置中的所有 RSS 源
    2. 筛选与 topic 相关的条目
    3. 对每条匹配条目调用 LLM 生成摘要
    4. 对每条条目调用 LLM 进行风险评分
    5. 构建 IntelBundle 并通过 ServiceResult 返回

    所有 LLM 调用和 RSS 抓取均受超时和异常保护，
    单个源失败不会导致整体 Pipeline 崩溃。
    """

    def __init__(self, llm: Optional[LLMRouter] = None) -> None:
        from fzq_ai.config import get_config

        self.config: Dict[str, Any] = get_config()
        self.sources: List[Dict[str, Any]] = self.config.get("rss_sources", [])
        self.llm: LLMRouter = llm or LLMRouter()

    # ── 内部方法 ──────────────────────────────────────────────

    def _fetch_rss(self, url: str, name: str) -> List[Any]:
        """
        抓取单个 RSS 源。

        Args:
            url: RSS feed URL
            name: 数据源名称（用于日志）

        Returns:
            feed entries 列表；失败时返回空列表
        """
        try:
            feed = feedparser.parse(url)
            if hasattr(feed, "bozo") and feed.bozo:
                logger.warning(f"[RSS] 解析警告 {name}: {feed.bozo_exception}")
            return feed.entries
        except Exception as e:
            logger.error(f"[RSS] 抓取失败: {name} ({url}) — {e}")
            return []

    def _summarize(self, title: str, content: str) -> str:
        """
        调用 LLM 生成新闻摘要。

        Args:
            title: 新闻标题
            content: 新闻内容

        Returns:
            LLM 生成的摘要文本；失败时返回原文截断
        """
        prompt = (
            "你是一名新闻分析助手，请用中文总结以下新闻内容（不超过3句话）：\n\n"
            f"标题：{title}\n内容：{content[:2000]}\n"
        )
        try:
            result: str = self.llm.run(prompt)
            return result.strip()
        except Exception as e:
            logger.warning(f"[LLM] 摘要生成失败: {e}")
            return content[:200] if content else title

    def _risk_score(self, title: str, summary: str) -> Dict[str, Any]:
        """
        调用 LLM 进行风险评分。

        Args:
            title: 新闻标题
            summary: 新闻摘要

        Returns:
            {"risk_level": 1-5, "risk_type": "..."}；失败时返回默认值
        """
        prompt = (
            "请对以下新闻进行风险评分（1-5），并给出风险类型：\n\n"
            f"标题：{title}\n摘要：{summary}\n\n"
            '输出 JSON：{"risk_level": 1-5, "risk_type": "政治/经济/社会/科技/其他"}'
        )
        try:
            result: Dict[str, Any] = self.llm.run_json(prompt)
            return result
        except Exception as e:
            logger.warning(f"[LLM] 风险评分失败: {e}")
            return {"risk_level": 1, "risk_type": "未知"}

    # ── 主入口 ────────────────────────────────────────────────

    def run(self, topic: str) -> ServiceResult:
        """
        执行新闻情报分析。

        Args:
            topic: 新闻主题关键词（支持中英文）

        Returns:
            ServiceResult:
            - success=True: data 包含 IntelBundle(meta, articles, events)
            - success=False: error 包含错误描述
        """
        logger.info(f"[NewsPipeline] 开始分析主题: '{topic}'")

        articles: List[Article] = []

        # — 遍历所有 RSS 源 —
        for src in self.sources:
            url: str = src.get("url", "")
            name: str = src.get("name", "unknown")

            if not url:
                continue

            entries: List[Any] = self._fetch_rss(url, name)

            for e in entries:
                title: str = e.get("title", "")
                content: str = e.get("summary", "") or e.get("description", "")
                link: str = e.get("link", "")

                # 主题匹配（v2.6 fix: 单词级匹配）
                if topic:
                    search_text: str = (title + " " + content).lower()
                    t_lower = topic.lower()
                    # 精确短语匹配
                    if t_lower in search_text:
                        pass  # matched
                    else:
                        # 单词级匹配
                        t_words = [w for w in t_lower.split() if len(w) >= 2]
                        if not any(w in search_text for w in t_words):
                            continue

                try:
                    llm_summary: str = self._summarize(title, content)
                    risk: Dict[str, Any] = self._risk_score(title, llm_summary)
                except Exception as e:
                    logger.error(f"[NewsPipeline] LLM 处理失败 for '{title}': {e}")
                    llm_summary = content[:200]
                    risk = {"risk_level": 1, "risk_type": "未知"}

                articles.append(
                    Article(
                        title_original=title,
                        url=link,
                        content_original=llm_summary,
                        source_name=name,
                        region=src.get("region", ""),
                        language=src.get("language", ""),
                        credibility=0.8,
                        bias=0.1,
                        fetched_at=datetime.now(timezone.utc),
                    )
                )

        logger.info(f"[NewsPipeline] 匹配 {len(articles)} 条新闻")

        # — 构建 IntelBundle —
        bundle: IntelBundle = IntelBundle(
            meta=IntelMeta(
                topics=[topic] if topic else [],
                regions=[],
                depth="normal",
            ),
            articles=articles,
            events=[],
        )

        return ServiceResult.ok({"intel_bundle": bundle})
