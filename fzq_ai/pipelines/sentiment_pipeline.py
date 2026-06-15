"""
fzq_ai/pipelines/sentiment_pipeline.py

FZQ‑AI v2.5 — Sentiment Analysis Pipeline.

功能：
- 对新闻文章列表进行情感/态度分析
- 返回每篇文章的情感标签和置信度
- 汇总整体情感分布

输入：articles: List[Article]
输出：ServiceResult(success, data={sentiments, distribution})
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fzq_ai.domain.models import Article, ServiceResult

from fzq_ai.store.intel_store import IntelStore
import uuid

class SentimentPipeline:
    """

    """

    # ── 情感关键词字典 ─────────────────────────────────────────
        "en": {
            "positive": [
                "growth", "surge", "rally", "boost", "improve",
                "recovery", "optimism", "peace", "deal", "agreement",
                "success", "achievement", "innovation", "progress",
                "stable", "support", "cooperation", "win",
            "negative": [
                "crisis", "crash", "crash", "decline", "collapse",
                "war", "attack", "conflict", "sanction", "sanctions",
                "protest", "riot", "violence", "death", "killed",
                "disaster", "emergency", "threat", "fear", "risk",
                "recession", "inflation", "unemployment", "debt",
                "scandal", "corruption", "fraud", "crackdown",
        "zh": {
            "positive": [
                "增长", "上涨", "复苏", "突破", "合作",
                "和平", "协议", "成功", "创新", "进步",
                "稳定", "支持", "利好", "改善", "提升",
            "negative": [
                "危机", "下跌", "暴跌", "崩溃", "冲突",
                "战争", "攻击", "制裁", "抗议", "暴力",
                "死亡", "灾难", "威胁", "恐惧", "风险",
                "衰退", "通胀", "贪污", "腐败", "丑闻",

    def __init__(self, llm_router: Optional[Any] = None) -> None:
        self.llm_router: Optional[Any] = llm_router

    # ── 主入口 ────────────────────────────────────────────────

    def run(
        self,
        """

        """
        if not articles:
            return ServiceResult.fail("SentimentPipeline 需要 articles 参数")

            "positive": 0,
            "neutral": 0,
            "negative": 0,

        for a in articles:

            sentiment: str = self._classify(text)
            distribution[sentiment] += 1

                    "id": getattr(a, "id", ""),
                    "title": a.title_original,
                    "source": a.source_name,
                    "region": a.region,
                    "sentiment": sentiment,
                    "url": a.url,

        # 整体情感

        if positive_pct > negative_pct + 20:
        elif negative_pct > positive_pct + 20:
        else:

        result: Dict[str, Any] = {
            "items": items,
            "distribution": {
                "positive": distribution["positive"],
                "neutral": distribution["neutral"],
                "negative": distribution["negative"],
                "positive_pct": positive_pct,
                "negative_pct": negative_pct,
            "overall_sentiment": overall,
            "total_articles": len(articles),
        }

        # v2.7: persist to IntelStore
        try:
                articles=articles if "articles" in dir() else [],
                events=[],
        except Exception:
            pass  # never break main flow

        return ServiceResult.ok(result)

    # ── 内部方法 ──────────────────────────────────────────────

    def _classify(self, text: str) -> str:
        """

            "positive" | "neutral" | "negative"
        """

        for lang_kws in self.SENTIMENT_KEYWORDS.values():
            for kw in lang_kws.get("positive", []):
                if kw in text:
            for kw in lang_kws.get("negative", []):
                if kw in text:

        if pos_score > neg_score:
            return "positive"
        elif neg_score > pos_score:
            return "negative"
        else:
            return "neutral"
