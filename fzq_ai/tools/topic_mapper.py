# fzq_ai/tools/topic_mapper.py

from __future__ import annotations


class TopicMapper:
    """
    将用户输入映射到预定义主题。
    这是一个简单版本，后续我们会升级成 DeepSeek 语义分类。
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
        }

    def map_topic(self, query: str | None) -> str | None:
        if not query:
            return None

        q = query.lower()

        for key, topic in self.mapping.items():
            if key in q:
                return topic

        # 默认返回 geopolitics（可调整）
        return None
