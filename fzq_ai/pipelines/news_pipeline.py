# fzq_ai/pipelines/news_pipeline.py

from __future__ import annotations
from typing import List, Any, Optional, Dict

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

    def __init__(self, llm_router: Optional[Any] = None):
        # 可选：LLM 路由，供 Agent 层调用
        self.llm_router = llm_router

    # ---- 同步入口（供 Streamlit 等同步上下文使用） ----

    def run(self, topic: str = "") -> ServiceResult:
        try:
            articles: List[Article] = fetch_all_news(topic)

            meta = IntelMeta(
                topics=[topic] if topic else [],
                regions=[],
                depth="normal",
            )

            bundle = IntelBundle(
                meta=meta,
                articles=articles,
                events=[],
            )

            return ServiceResult.ok({"intel_bundle": bundle})

        except Exception as e:
            return ServiceResult.fail(str(e))

    def run_sync(self, topic: str = "") -> Dict[str, Any]:
        """run_sync 别名：返回 dict，供 main.py / app.py 使用"""
        result = self.run(topic)
        if result.success:
            return result.data
        else:
            return {"error": result.error}


if __name__ == "__main__":
    print("Running NewsPipeline test...")
    pipeline = NewsPipeline()
    result = pipeline.run("澳洲房地产趋势")
    print("Result:")
    print(result)
