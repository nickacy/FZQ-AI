# fzq_ai/intel/event_clustering.py

from __future__ import annotations
from typing import List, Dict
from collections import defaultdict

from fzq_ai.intel.models import Article, EventCluster


class SimpleEventClusteringEngine:
    """
    Phase 5.4 简化事件聚类引擎：
    - 按来源区域 + 关键词粗聚类
    - 后续可以替换为 embedding + HDBSCAN
    """

    KEYWORDS = {
        "taiwan": ["taiwan", "台海", "台灣"],
        "ukraine": ["ukraine", "乌克兰"],
        "middle_east": ["gaza", "israel", "palestine", "加沙", "以色列"],
        "china_macro": ["china", "中国", "经济", "growth", "gdp"],
    }

    def cluster(self, articles: List[Article]) -> List[EventCluster]:
        buckets: Dict[str, List[str]] = defaultdict(list)

        for a in articles:
            text = (a.title_original + " " + a.content_original).lower()
            matched = False

            for key, words in self.KEYWORDS.items():
                if any(w in text for w in words):
                    buckets[key].append(a.id)
                    matched = True
                    break

            if not matched:
                buckets["misc"].append(a.id)

        clusters: List[EventCluster] = []
        for idx, (topic, ids) in enumerate(buckets.items(), start=1):
            clusters.append(
                EventCluster(
                    id=f"event-{idx}",
                    topic=topic,
                    article_ids=ids,
                )
            )

        return clusters
