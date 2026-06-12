# fzq_ai/tools/news_fetcher.py

from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import asyncio
from datetime import datetime, timezone

import aiohttp
import feedparser

from fzq_ai.domain.models import Article


class NewsFetcher:
    """
    新闻抓取器：RSS + NewsAPI 混合版
    - 优先使用 RSS 多源抓取
    - 如配置 NEWSAPI_KEY，则额外使用 NewsAPI 扩展英文新闻
    """

    def __init__(self) -> None:
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "").strip()

        # 多源 RSS 配置
        self.rss_sources = [
            {
                "id": "bbc",
                "name": "BBC World",
                "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
                "region": "western",
                "language": "en",
            },
            {
                "id": "reuters",
                "name": "Reuters World",
                "url": "https://feeds.reuters.com/Reuters/worldNews",
                "region": "western",
                "language": "en",
            },
            {
                "id": "ap",
                "name": "AP World",
                "url": "https://apnews.com/rss/apf-worldnews",
                "region": "western",
                "language": "en",
            },
            {
                "id": "aljazeera",
                "name": "Al Jazeera",
                "url": "https://www.aljazeera.com/xml/rss/all.xml",
                "region": "middle_east",
                "language": "en",
            },
            {
                "id": "nhk",
                "name": "NHK Japan",
                "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
                "region": "east_asia",
                "language": "ja",
            },
        ]

    async def fetch_news(self, topic: Optional[str]) -> List[Article]:
        """
        综合抓取：
        - 所有 RSS 源
        - 如有 NEWSAPI_KEY，则额外调用 NewsAPI
        """
        rss_articles = await self._fetch_all_rss()
        api_articles: List[Article] = []

        if self.newsapi_key and topic:
            api_articles = await self._fetch_newsapi(topic)

        # 合并去重（按 url）
        all_articles: Dict[str, Article] = {}
        for a in rss_articles + api_articles:
            if a.url not in all_articles:
                all_articles[a.url] = a

        return list(all_articles.values())

    async def _fetch_all_rss(self) -> List[Article]:
        tasks = [self._fetch_single_rss(cfg) for cfg in self.rss_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles: List[Article] = []
        for r in results:
            if isinstance(r, list):
                articles.extend(r)
        return articles

    async def _fetch_single_rss(self, cfg: Dict[str, Any]) -> List[Article]:
        def _parse() -> List[Article]:
            feed = feedparser.parse(cfg["url"])
            items: List[Article] = []
            now = datetime.now(timezone.utc)

            for idx, entry in enumerate(feed.entries):
                url = entry.get("link") or ""
                title = entry.get("title") or ""
                summary = entry.get("summary") or ""

                if not url or not title:
                    continue

                art = Article(
                    id=f"{cfg['id']}-{idx}",
                    url=url,
                    source_id=cfg["id"],
                    source_name=cfg["name"],
                    region=cfg["region"],
                    language=cfg["language"],
                    fetched_at=now,
                    title_original=title,
                    content_original=summary,
                    content_translated=None,
                    content_snippet_en=None,
                    credibility=0.9,
                    bias=0.1,
                    propaganda_tags=[],
                )
                items.append(art)
            return items

        return await asyncio.to_thread(_parse)

    async def _fetch_newsapi(self, topic: str) -> List[Article]:
        """
        使用 NewsAPI 扩展英文新闻：
        需要环境变量：NEWSAPI_KEY
        """
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "language": "en",
            "pageSize": 50,
            "sortBy": "publishedAt",
            "apiKey": self.newsapi_key,
        }

        articles: List[Article] = []
        now = datetime.now(timezone.utc)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
            except Exception:
                return []

        for idx, item in enumerate(data.get("articles", [])):
            src = item.get("source") or {}
            url = item.get("url") or ""
            title = item.get("title") or ""
            desc = item.get("description") or ""

            if not url or not title:
                continue

            art = Article(
                id=f"newsapi-{idx}",
                url=url,
                source_id=src.get("id") or "newsapi",
                source_name=src.get("name") or "NewsAPI",
                region="western",
                language="en",
                fetched_at=now,
                title_original=title,
                content_original=desc,
                content_translated=None,
                content_snippet_en=None,
                credibility=0.85,
                bias=0.1,
                propaganda_tags=[],
            )
            articles.append(art)

        return articles
