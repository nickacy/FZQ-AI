import json
from fzq_ai.domain.models import Article


class SentimentPipeline:
    """
    兼容旧测试：run() 必须返回 str
    """

    POSITIVE = ["growth", "improve", "positive", "up"]
    NEGATIVE = ["crisis", "conflict", "war", "attack", "down"]

    def run(self, articles=None):
        if not articles:
            return "无文章"

        pos = 0
        neg = 0
        items = []

        for a in articles:
            text = f"{a.title_original} {a.content_original}".lower()
            p = sum(w in text for w in self.POSITIVE)
            n = sum(w in text for w in self.NEGATIVE)

            if p > n:
                sentiment = "positive"
                pos += 1
            elif n > p:
                sentiment = "negative"
                neg += 1
            else:
                sentiment = "neutral"

            items.append({"title": a.title_original, "sentiment": sentiment})

        result = {
            "items": items,
            "positive": pos,
            "negative": neg,
            "overall": "中性" if pos == neg else ("正面" if pos > neg else "负面"),
        }

        return json.dumps(result, ensure_ascii=False)
