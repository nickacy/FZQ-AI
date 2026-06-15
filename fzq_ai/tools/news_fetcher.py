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
    """

    def __init__(self) -> None:
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "").strip()

        # 多源 RSS 配置
        self.rss_sources = [
                "id": "bbc",
                "name": "BBC World",
                "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
                "region": "western",
                "language": "en",
                "id": "reuters",
                "name": "Reuters World",
                "url": "https://feeds.reuters.com/Reuters/worldNews",
                "region": "western",
                "language": "en",
                "id": "ap",
                "name": "AP World",
                "url": "https://apnews.com/rss/apf-worldnews",
                "region": "western",
                "language": "en",
                "id": "aljazeera",
                "name": "Al Jazeera",
                "url": "https://www.aljazeera.com/xml/rss/all.xml",
                "region": "middle_east",
                "language": "en",
                "id": "nhk",
                "name": "NHK Japan",
                "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
                "region": "east_asia",
                "language": "ja",

    async def fetch_news(self, topic: Optional[str]) -> List[Article]:
        """
        """
        rss_articles = await self._fetch_all_rss()
        api_articles: List[Article] = []

        if self.newsapi_key and topic:
            api_articles = await self._fetch_newsapi(topic)

        # 合并去重（按 url）
        for a in rss_articles + api_articles:
            if a.url not in all_articles:

        return list(all_articles.values())

    async def _fetch_all_rss(self) -> List[Article]:
        tasks = [self._fetch_single_rss(cfg) for cfg in self.rss_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, list):
                articles.extend(r)
        return articles

    async def _fetch_single_rss(self, cfg: Dict[str, Any]) -> List[Article]:
        def _parse() -> List[Article]:
            feed = feedparser.parse(cfg["url"])
            items: List[Article] = []

            for idx, entry in enumerate(feed.entries):
                url = entry.get("link") or ""
                title = entry.get("title") or ""
                summary = entry.get("summary") or ""

                if not url or not title:

            return items

        return await asyncio.to_thread(_parse)

    async def _fetch_newsapi(self, topic: str) -> List[Article]:
        """
        """
            "q": topic,
            "language": "en",
            "pageSize": 50,
            "sortBy": "publishedAt",
            "apiKey": self.newsapi_key,

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        return []
            except Exception:
                return []

        for idx, item in enumerate(data.get("articles", [])):
            src = item.get("source") or {}
            url = item.get("url") or ""
            title = item.get("title") or ""
            desc = item.get("description") or ""

            if not url or not title:

        return articles
