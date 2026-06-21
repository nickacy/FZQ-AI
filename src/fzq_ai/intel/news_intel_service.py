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
    sources: List[SourceConfig]
    default_target_language: str = "zh"
    cache_enabled: bool = False

    @staticmethod
    def from_yaml(path: str) -> "NewsIntelConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        sources = []
        for s in data.get("sources", []):
            sources.append(
                SourceConfig(
                    id=s["id"],
                    name=s["name"],
                    region=s["region"],
                    language=s["language"],
                    url=s["url"],
                    enabled=True,
                    topic_tags=s.get("topic_tags", []),
                )
            )

        return NewsIntelConfig(sources=sources)


# ---------------------------------------------------------
# 多源抓取器（RSS）
# ---------------------------------------------------------
class MultiSourceFetcher:
    def __init__(self, sources: List[SourceConfig]) -> None:
        self.sources = [s for s in sources if s.enabled]

    async def fetch(
        self,
        topics: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        max_items: int = 30,
    ) -> List[Article]:
        import feedparser

        articles: List[Article] = []

        for src in self.sources:
            if regions and src.region not in regions:
                continue
            if topics and src.topic_tags:
                if not any(t in src.topic_tags for t in topics):
                    continue

            try:
                feed = feedparser.parse(src.url)
            except Exception:
                continue

            for idx, entry in enumerate(feed.entries):
                if len(articles) >= max_items:
                    break

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                article = Article(
                    id=f"{src.id}-{idx}",
                    url=link,
                    source_id=src.id,
                    source_name=src.name,
                    region=src.region,
                    language=src.language,
                    fetched_at=datetime.utcnow(),
                    title_original=title,
                    content_original=summary,
                )
                articles.append(article)

        return articles


# ---------------------------------------------------------
# NewsIntelService（异步 NarrativeEngine 版本）
# ---------------------------------------------------------
class NewsIntelService:
    """
    Phase 5.5 完整版（异步 NarrativeEngine）：
    - 多源抓取
    - 去噪
    - 翻译
    - 可信度 / 偏见 / 宣传标签
    - 事件聚类
    - 多阵营叙事（LLM 异步）
    """

    def __init__(self, config: NewsIntelConfig) -> None:
        self.config = config
        self.fetcher = MultiSourceFetcher(config.sources)
        self.event_engine = SimpleEventClusteringEngine()
        self.narrative_engine = NarrativeEngine()

    async def gather_intel(
        self,
        topics: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        depth: str = "fast",
    ) -> IntelBundle:

        # 1. 多源抓取
        articles = await self.fetcher.fetch(
            topics=topics,
            regions=regions,
            max_items=30,
        )

        # 2. 去噪
        for a in articles:
            a.content_original = DenoisingEngine.clean(a.content_original)

        # 3. 翻译（并行执行）
        translator = TranslationManager()
        await asyncio.gather(*[translator.process_article(a) for a in articles])

        # 4. 可信度 / 偏见 / 宣传标签
        for a in articles:
            a.credibility = CredibilityScorer.score(a)
            a.bias = BiasScorer.score(a)
            a.propaganda_tags = PropagandaTagger.tag(a)

        # 5. 事件聚类
        events: List[EventCluster] = self.event_engine.cluster(articles)

        # 6. 多阵营叙事（异步并行）
        narrative_tasks = []
        for ev in events:
            ev_articles = [a for a in articles if a.id in ev.article_ids]
            narrative_tasks.append(
                self.narrative_engine.generate_async(ev_articles, ev.id)
            )

        narratives: List[Narrative] = await asyncio.gather(*narrative_tasks)

        # 7. 打包返回
        meta = IntelMeta(
            topics=topics or [],
            regions=regions or [],
            depth=depth,
        )

        return IntelBundle(
            meta=meta,
            articles=articles,
            events=events,
            narratives=narratives,
        )
