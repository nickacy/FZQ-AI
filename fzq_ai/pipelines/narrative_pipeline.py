# fzq_ai/pipelines/narrative_pipeline.py

from __future__ import annotations
from typing import List, Dict, Any, Optional
from collections import Counter
import re

from fzq_ai.domain.models import ServiceResult,  Article, ServiceResult
from fzq_ai.pipelines.news_fetcher import fetch_all_news

from fzq_ai.store.intel_store import IntelStore
import uuid

STOPWORDS = {
    "the", "and", "of", "to", "in", "for", "on", "at", "a", "an",
    "is", "are", "was", "were", "by", "with", "from", "as", "that",
    "this", "it", "its", "be", "has", "have", "had", "will", "would",
    "about", "over", "after", "before", "into", "out", "up", "down",
}

class NarrativePipeline:
    """
    """

    def __init__(self, llm_router: Any = None):
        self.llm_router = llm_router

    def run(
        self,
        """
        """
        if articles is None:

        if not articles:
            return "暂无数据，无法进行叙事分析。请提供文章数据或有效的搜索关键词。"

        # 1. 按阵营分组
            "western": [],
            "east_asia": [],
            "middle_east": [],
            "other": [],

        for a in articles:
            if region in ["western", "us", "europe"]:
            elif region in ["east_asia", "japan", "korea", "china"]:
            elif region in ["middle_east"]:
            else:

        # 2. 为每个阵营提取"叙事主题关键词"
        def extract_themes(items: List[Article]) -> List[str]:
            text_blob = " ".join(a.title_original for a in items)
            text_blob = text_blob.lower()
            tokens = re.findall(r"[a-zA-Z]{3,}", text_blob)
            tokens = [t for t in tokens if t not in STOPWORDS]
            return [w for w, _ in counter.most_common(8)]

        # 3. 构建可读输出
        lines = ["# 🌥 多阵营叙事分析报告\n"]

            "western": "西方阵营",
            "east_asia": "东亚阵营",
            "middle_east": "中东阵营",
            "other": "其他阵营",

        for key, label in labels.items():
            lines.append(f"## {label}")
            articles_in_bucket = buckets[key]
            if not articles_in_bucket:

            lines.append(f"**核心叙事主题**: {', '.join(themes) if themes else '（无显著主题）'}")
            lines.append(f"**文章数**: {len(articles_in_bucket)}")
            lines.append("")
            for a in articles_in_bucket[:5]:

        # v2.7: persist to IntelStore
        try:
                articles=articles if "articles" in dir() else [],
                events=[],
        except Exception:
            pass  # never break main flow

        return "\n".join(lines)

if __name__ == "__main__":
    print("Running NarrativePipeline test...")
    pipeline = NarrativePipeline()
    result = pipeline.run(text="global economy")
    print("Result:")
    print(result)
