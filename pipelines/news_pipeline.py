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
            if hasattr(feed, "bozo") and feed.bozo:
                logger.warning(f"[RSS] 解析警告 {name}: {feed.bozo_exception}")
            return feed.entries
        except Exception as e:
            return []

    # ───────────────────────────────────────────────────────────────
    # LLM 摘要（同步修复版）
    # ───────────────────────────────────────────────────────────────

    def _summarize(self, title: str, content: str) -> str:
        prompt = (
            "你是一名新闻分析助手，请用中文总结以下新闻内容（不超过3句话）：\n\n"
        try:
            raw = self.llm.run(prompt)     # ⭐ run() 已同步
            return str(raw).strip()        # ⭐ 强制转字符串，避免 coroutine.strip()
        except Exception as e:
            return content[:200] if content else title

    # ───────────────────────────────────────────────────────────────
    # LLM 风险评分（同步修复版）
    # ───────────────────────────────────────────────────────────────

    def _risk_score(self, title: str, summary: str) -> Dict[str, Any]:
        prompt = (
            "请对以下新闻进行风险评分（1-5），并给出风险类型：\n\n"
            '输出 JSON：{"risk_level": 1-5, "risk_type": "政治/经济/社会/科技/其他"}'
        try:
            result = self.llm.run_json(prompt)   # ⭐ 同步 JSON 输出
            return dict(result)
        except Exception as e:
            return {"risk_level": 1, "risk_type": "未知"}

    # ───────────────────────────────────────────────────────────────
    # 主入口
    # ───────────────────────────────────────────────────────────────

    def run(self, topic: str) -> ServiceResult:
        logger.info(f"[NewsPipeline] 开始分析主题: '{topic}'")

        for src in self.sources:

            if not url:

            entries = self._fetch_rss(url, name)

            for e in entries:

                # ── v2.6: 短语 + 单词级匹配 ───────────────────────
                if topic:

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

                topics=[topic] if topic else [],

        return ServiceResult.ok({"intel_bundle": bundle})
