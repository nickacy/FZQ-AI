# fzq_ai/pipelines/narrative_pipeline.py

from __future__ import annotations
from typing import List, Dict, Any
from collections import Counter
import re

from fzq_ai.domain.models import Article, ServiceResult

STOPWORDS = {
    "the",
    "and",
    "of",
    "to",
    "in",
    "for",
    "on",
    "at",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "by",
    "with",
    "from",
    "as",
    "that",
    "this",
    "it",
    "its",
    "be",
    "has",
    "have",
    "had",
    "will",
    "would",
    "about",
    "over",
    "after",
    "before",
    "into",
    "out",
    "up",
    "down",
}


class NarrativePipeline:
    """
    多阵营叙事分析（专业版）
    - 按 region 分阵营
    - 提取每个阵营的核心叙事主题（关键词）
    - 输出结构化结果，便于 UI 和日报使用
    """

    def __init__(self, llm_router: Any = None):
        self.llm_router = llm_router

    async def run(
        self,
        articles: List[Article],
        summary: str | None = None,
    ) -> ServiceResult:

        if not articles:
            return ServiceResult.fail("NarrativePipeline 需要 articles 参数")

        # 1. 按阵营分组
        buckets: Dict[str, List[Article]] = {
            "western": [],
            "east_asia": [],
            "middle_east": [],
            "other": [],
        }

        for a in articles:
            region = (a.region or "").lower()
            if region in ["western", "us", "europe"]:
                buckets["western"].append(a)
            elif region in ["east_asia", "japan", "korea", "china"]:
                buckets["east_asia"].append(a)
            elif region in ["middle_east"]:
                buckets["middle_east"].append(a)
            else:
                buckets["other"].append(a)

        # 2. 为每个阵营提取“叙事主题关键词”
        def extract_themes(items: List[Article]) -> List[str]:
            text = " ".join(a.title_original for a in items)
            text = text.lower()
            tokens = re.findall(r"[a-zA-Z]{3,}", text)
            tokens = [t for t in tokens if t not in STOPWORDS]
            counter = Counter(tokens)
            return [w for w, _ in counter.most_common(8)]

        def to_brief_list(items: List[Article]) -> List[Dict[str, Any]]:
            return [
                {
                    "title": a.title_original,
                    "source": a.source_name,
                    "region": a.region,
                    "url": a.url,
                }
                for a in items[:10]
            ]

        result = {
            "western": {
                "themes": (
                    extract_themes(buckets["western"]) if buckets["western"] else []
                ),
                "articles": to_brief_list(buckets["western"]),
            },
            "east_asia": {
                "themes": (
                    extract_themes(buckets["east_asia"]) if buckets["east_asia"] else []
                ),
                "articles": to_brief_list(buckets["east_asia"]),
            },
            "middle_east": {
                "themes": (
                    extract_themes(buckets["middle_east"])
                    if buckets["middle_east"]
                    else []
                ),
                "articles": to_brief_list(buckets["middle_east"]),
            },
            "other": {
                "themes": extract_themes(buckets["other"]) if buckets["other"] else [],
                "articles": to_brief_list(buckets["other"]),
            },
        }

        return ServiceResult.ok(result)
