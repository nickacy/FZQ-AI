# fzq_ai/intel/news_intel_service.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import yaml
import asyncio

from fzq_ai.intel.models import (
    Article,
    SourceConfig,
    IntelBundle,
    IntelMeta,
    EventCluster,
    Narrative,
)
from fzq_ai.intel.translation_manager import TranslationManager
from fzq_ai.intel.denoising_and_scoring import (
    DenoisingEngine,
    CredibilityScorer,
    BiasScorer,
    PropagandaTagger,
)
from fzq_ai.intel.event_clustering import SimpleEventClusteringEngine
from fzq_ai.intel.narrative_engine import NarrativeEngine

# ---------------------------------------------------------
# 配置加载（支持 YAML）
# ---------------------------------------------------------
@dataclass
class NewsIntelConfig:

    @staticmethod
    def from_yaml(path: str) -> "NewsIntelConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for s in data.get("sources", []):
            sources.append(
                SourceConfig(
                    id=s["id"],

        return NewsIntelConfig(sources=sources)

# ---------------------------------------------------------
# 多源抓取器（RSS）
# ---------------------------------------------------------
class MultiSourceFetcher:
    def __init__(self, sources: List[SourceConfig]) -> None:
        self.sources = [s for s in sources if s.enabled]

    async def fetch(
        self,

        for src in self.sources:
            if regions and src.region not in regions:
            if topics and src.topic_tags:
                if not any(t in src.topic_tags for t in topics):
                    continue

            try:
            except Exception:

            for idx, entry in enumerate(feed.entries):
                if len(articles) >= max_items:
                    break

        return articles

# ---------------------------------------------------------
# NewsIntelService（异步 NarrativeEngine 版本）
# ---------------------------------------------------------
class NewsIntelService:
    """
    """

    def __init__(self, config: NewsIntelConfig) -> None:
        self.config = config
        self.fetcher = MultiSourceFetcher(config.sources)
        self.event_engine = SimpleEventClusteringEngine()
        self.narrative_engine = NarrativeEngine()

    async def gather_intel(
        self,

        # 1. 多源抓取
        articles = await self.fetcher.fetch(
            topics=topics,

        # 2. 去噪
        for a in articles:

        # 3. 翻译（并行执行）
        await asyncio.gather(*[translator.process_article(a) for a in articles])

        # 4. 可信度 / 偏见 / 宣传标签
        for a in articles:

        # 5. 事件聚类
        events: List[EventCluster] = self.event_engine.cluster(articles)

        # 6. 多阵营叙事（异步并行）
        for ev in events:
            ev_articles = [a for a in articles if a.id in ev.article_ids]
                self.narrative_engine.generate_async(ev_articles, ev.id)
            )

        # 7. 打包返回

        return IntelBundle(
            meta=meta,
