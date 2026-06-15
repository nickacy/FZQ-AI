# fzq_ai/tools/topic_mapper.py

from __future__ import annotations

class TopicMapper:
    """
    """

    def __init__(self):
        # 简单关键词映射
        self.mapping = {
            "china": "geopolitics",
            "us": "geopolitics",
            "america": "geopolitics",
            "russia": "geopolitics",
            "ukraine": "geopolitics",
            "war": "geopolitics",
            "conflict": "geopolitics",
            "election": "politics",
            "policy": "politics",
            "economy": "economy",
            "inflation": "economy",
            "stock": "economy",
            "market": "economy",
            "tech": "technology",
            "ai": "technology",
            "science": "technology",
            "japan": "east_asia",
            "korea": "east_asia",
            "australia": "oceania",

    def map_topic(self, query: str | None) -> str | None:
        if not query:
            return None

        for key, topic in self.mapping.items():
            if key in q:
                return topic

        # 默认返回 geopolitics（可调整）
        return None
