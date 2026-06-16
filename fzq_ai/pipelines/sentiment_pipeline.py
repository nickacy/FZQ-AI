import json
from typing import List, Dict, Any, Optional
from fzq_ai.domain.models import Article, ServiceResult


class SentimentPipeline:
    """
    最终稳定版：
    - 支持 llm_router 参数（orchestrator 需要）
    - run() 返回 ServiceResult（tests 需要）
    - data 中包含 distribution（tests 需要）
    """

    POSITIVE = ["growth", "improve", "positive", "up"]
    NEGATIVE = ["crisis", "conflict", "war", "attack", "down"]

    def __init__(self, llm_router=None):
        self.llm_router = llm_router

    def _classify(self, text: str) -> str:
        p = sum(w in text for w in self.POSITIVE)
        n = sum(w in text for w in self.NEGATIVE)
        if p > n:
            return "positive"
        if n > p:
            return "negative"
        return "neutral"

    def run(self, articles: Optional[List[Article]] = None) -> ServiceResult:
        """
        tests 要求：
        - 返回 ServiceResult
        - data 中必须包含 distribution
        """

        if not articles:
            return ServiceResult.fail("SentimentPipeline 需要 articles 参数")

        items: List[Dict[str, Any]] = []
        distribution = {"positive": 0, "neutral": 0, "negative": 0}

        for a in articles:
            text = f"{a.title_original} {a.content_original}".lower()
            sentiment = self._classify(text)

            distribution[sentiment] += 1

            items.append(
                {
                    "id": getattr(a, "id", ""),
                    "title": a.title_original,
                    "source": a.source,
                    "region": a.region,
                    "sentiment": sentiment,
                    "url": a.url,
                }
            )

        total = len(articles)
        pos = distribution["positive"]
        neg = distribution["negative"]

        overall = "中性"
        if pos > neg:
            overall = "正面"
        elif neg > pos:
            overall = "负面"

        data = {
            "items": items,
            "distribution": distribution,
            "overall_sentiment": overall,
            "total_articles": total,
        }

        return ServiceResult.ok(data)
