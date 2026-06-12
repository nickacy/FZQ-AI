# fzq_ai/pipelines/news_pipeline.py

from __future__ import annotations
from typing import List, Any

from fzq_ai.domain.models import (
    Article,
    IntelMeta,
    IntelBundle,
    ServiceResult,
)
from fzq_ai.pipelines.news_fetcher import fetch_all_news


class NewsPipeline:
    """
    新闻抓取 Pipeline（RSS + NewsAPI + GDELT）
    返回 IntelBundle（meta + articles + events）
    """

    def run(self, topic: str) -> ServiceResult:
        try:
            # 1. 抓取所有新闻（RSS + NewsAPI + GDELT DOC + GDELT Event）
            articles: List[Article] = fetch_all_news(topic)

            # 2. 构造 IntelMeta（按你项目的真实结构）
            meta = IntelMeta(
                topics=[topic],
                regions=[],        # 你可以后续自动识别地区
                depth="normal",    # 你可以后续做深度分析
            )

            # 3. 构造 IntelBundle（按你项目的真实结构）
            bundle = IntelBundle(
                meta=meta,
                articles=articles,
                events=[],         # GDELT Event 可放这里
            )

            return ServiceResult.ok(bundle)

        except Exception as e:
            return ServiceResult.fail(str(e))
