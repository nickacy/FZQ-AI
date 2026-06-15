"""
pipelines/news_pipeline.py

FZQ‑AI v2.5/v2.6 — RSS-based News Intelligence Pipeline (同步修正版)

功能：
- RSS 多源新闻抓取
- LLM 自动摘要（同步）
- LLM 风险评分（同步）
- 返回统一的 ServiceResult（IntelBundle）
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Optional, Dict

import feedparser

from fzq_ai.domain.models import Article, IntelBundle, IntelMeta, ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.logger import get_logger

logger = get_logger(__name__)

LLM_TIMEOUT_SEC = 60
RSS_TIMEOUT_SEC = 30


class NewsPipeline:
    """
    RSS 多源新闻抓取 + 自动摘要 + 风险评分 Pipeline（同步版）

    工作流程：
    1. 遍历配置中的所有 RSS 源
    2. 筛选与 topic 相关的条目（短语 + 单词级匹配）
    3. 调用 LLM 生成摘要（同步）
    4. 调用 LLM 进行风险评分（同步）
    5. 构建 IntelBundle 并通过 ServiceResult 返回
    """

    def __init__(self, llm: Optional[LLMRouter] = None) -> None:
        from fzq_ai.config import get_config

        self.config: Dict[str, Any] = get_config()
        self.sources: List[Dict[str, Any]] = self.config.get("rss_sources", [])
        self.llm: LLMRouter = llm or LLMRouter()

    # ───────────────────────────────────────────────────────────────
    # RSS 抓取
    # ───────────────────────────────────────────────────────────────

    def _fetch_rss(self, url: str, name: str) -> List[Any]:
        try:
            feed = feedparser.parse(url)
            if hasattr(feed, "bozo") and feed.bozo:
                logger.warning(f"[RSS] 解析警告 {name}: {feed.bozo_exception}")
            return feed.entries
        except Exception as e:
            logger.error(f"[RSS] 抓取失败: {name} ({url}) — {e}")
            return []

    # ───────────────────────────────────────────────────────────────
    # LLM 摘要（同步修复版）
    # ───────────────────────────────────────────────────────────────

    def _summarize(self, title: str, content: str) -> str:
        prompt = (
            "你是一名新闻分析助手，请用中文总结以下新闻内容（不超过3句话）：\n\n"
            f"标题：{title}\n内容：{content[:2000]}\n"
        )
        try:
            raw = self.llm.run(prompt)     # ⭐ run() 已同步
            return str(raw).strip()        # ⭐ 强制转字符串，避免 coroutine.strip()
        except Exception as e:
            logger.warning(f"[LLM] 摘要生成失败: {e}")
            return content[:200] if content else title

    # ───────────────────────────────────────────────────────────────
    # LLM 风险评分（同步修复版）
    # ───────────────────────────────────────────────────────────────

    def _risk_score(self, title: str, summary: str) -> Dict[str, Any]:
        prompt = (
            "请对以下新闻进行风险评分（1-5），并给出风险类型：\n\n"
            f"标题：{title}\n摘要：{summary}\n\n"
            '输出 JSON：{"risk_level": 1-5, "risk_type": "政治/经济/社会/科技/其他"}'
        )
        try:
            result = self.llm.run_json(prompt)   # ⭐ 同步 JSON 输出
            return dict(result)
        except Exception as e:
            logger.warning(f"[LLM] 风险评分失败: {e}")
            return {"risk_level": 1, "risk_type": "未知"}

    # ───────────────────────────────────────────────────────────────
    # 主入口
    # ───────────────────────────────────────────────────────────────

    def run(self, topic: str) -> ServiceResult:
        logger.info(f"[NewsPipeline] 开始分析主题: '{topic}'")

        articles: List[Article] = []

        for src in self.sources:
            url = src.get("url", "")
            name = src.get("name", "unknown")

            if not url:
                continue

            entries = self._fetch_rss(url, name)

            for e in entries:
                title = e.get("title", "")
                content = e.get("summary", "") or e.get("description", "")
                link = e.get("link", "")

                # ── v2.6: 短语 + 单词级匹配 ───────────────────────
                if topic:
                    search_text = (title + " " + content).lower()
                    t_lower = topic.lower()

                    if t_lower not in search_text:
                        t_words = [w for w in t_lower.split() if len(w) >= 2]
                        if not any(w in search_text for w in t_words):
                            continue

                # ── LLM 摘要 + 风险评分 ─────────────────────────
                try:
                    summary = self._summarize(title, content)
                    risk = self._risk_score(title, summary)
                except Exception as e:
                    logger.error(f"[NewsPipeline] LLM 处理失败 for '{title}': {e}")
                    summary = content[:200]
                    risk = {"risk_level": 1, "risk_type": "未知"}

                articles.append(
                    Article(
                        title_original=title,
                        url=link,
                        content_original=summary,
                        source_name=name,
                        region=src.get("region", ""),
                        language=src.get("language", ""),
                        credibility=0.8,
                        bias=0.1,
                        fetched_at=datetime.now(timezone.utc),
                        risk=risk,
                    )
                )

        logger.info(f"[NewsPipeline] 匹配 {len(articles)} 条新闻")

        bundle = IntelBundle(
            meta=IntelMeta(
                topics=[topic] if topic else [],
                regions=[],
                depth="normal",
            ),
            articles=articles,
            events=[],
        )

        return ServiceResult.ok({"intel_bundle": bundle})
