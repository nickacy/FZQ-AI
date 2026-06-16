import json
from typing import List, Dict, Any
from fzq_ai.domain.models import Article


class SentimentPipeline:
    """
    完整功能版 + 测试兼容版
    - 保留情感分析逻辑
    - 最终返回 JSON 字符串（tests 要求）
    """

    POSITIVE = ["growth", "improve", "positive", "up"]
    NEGATIVE = ["crisis", "conflict", "war", "attack", "down"]

    def _classify(self, text: str) -> str:
        p = sum(w in text for w in self.POSITIVE)
        n = sum(w in text for w in self.NEGATIVE)
        if p > n:
            return "positive"
        if n > p:
            return "negative"
        return "neutral"

    def run(self, articles: List[Article]):
        if not articles:
            return "[]"

        items: List[Dict[str, Any]] = []
        pos = neg = neu = 0

        for a in articles:
            text = f"{a.title_original} {a.content_original}".lower()
            sentiment = self._classify(text)

            if sentiment == "positive":
                pos += 1
            elif sentiment == "negative":
                neg += 1
            else:
                neu += 1

            items.append(
                {
                    "title": a.title_original,
                    "region": a.region,
                    "sentiment": sentiment,
                }
            )

        result = {
            "items": items,
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "total_articles": len(articles),
            "overall_sentiment": (
                "正面" if pos > neg else ("负面" if neg > pos else "中性")
            ),
        }

        # ⭐ tests 要求返回 str
        return json.dumps(result, ensure_ascii=False)
