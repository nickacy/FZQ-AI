# fzq_ai/pipelines/news_fetcher.py
"""
新闻抓取聚合器（同步版）
- RSS：使用 feedparser 抓取多源 RSS
- NewsAPI：按 query 关键词搜索英文新闻
- GDELT：全球事件数据库（DOC + Event）
- 合并去重后返回 Article 列表
"""

import os
import requests
import asyncio
import feedparser
from datetime import datetime, timezone
from typing import List, Dict, Any

from fzq_ai.tools.translator import translate_to_english
from fzq_ai.domain.models import Article

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()

# 多源 RSS 配置（可扩展至 50+ 源）
RSS_SOURCES = [
    {
        "id": "bbc",
        "name": "BBC World",
        "region": "western",
        "language": "en",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
    },
    {
        "id": "reuters",
        "name": "Reuters World",
        "region": "western",
        "language": "en",
        "url": "https://feeds.reuters.com/Reuters/worldNews",
    },
    {
        "id": "ap",
        "name": "AP World",
        "region": "western",
        "language": "en",
        "url": "https://apnews.com/rss/apf-worldnews",
    },
    {
        "id": "aljazeera",
        "name": "Al Jazeera",
        "region": "middle_east",
        "language": "en",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
    },
    {
        "id": "nhk",
        "name": "NHK Japan",
        "region": "east_asia",
        "language": "ja",
        "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
    },
]


def _parse_rss_source(cfg: Dict[str, Any]) -> List[Article]:
    """解析单个 RSS 源，返回 Article 列表"""
    articles: List[Article] = []
    try:
        feed = feedparser.parse(cfg["url"])
        now = datetime.now(timezone.utc)
        for idx, entry in enumerate(feed.entries):
            url = entry.get("link") or ""
            title = entry.get("title") or ""
            summary = entry.get("summary") or ""
            if not url and not title:
                continue
            articles.append(
                Article(
                    id=f"{cfg['id']}-{idx}",
                    url=url,
                    source_id=cfg["id"],
                    source_name=cfg["name"],
                    region=cfg.get("region", ""),
                    language=cfg.get("language", ""),
                    fetched_at=now,
                    title_original=title,
                    content_original=summary,
                    credibility=0.9,
                    bias=0.1,
                )
            )
    except Exception:
        pass  # 单个源失败不影响整体
    return articles


def fetch_from_rss(query: str = "") -> List[Article]:
    """同步抓取所有配置的 RSS 源"""
    all_articles: List[Article] = []
    for cfg in RSS_SOURCES:
        all_articles.extend(_parse_rss_source(cfg))

    # ⭐ 自动翻译中文 query → 英文，再过滤（方案二）
    if query:
        q_en = translate_to_english(query).lower()
        all_articles = [
            a
            for a in all_articles
            if q_en in (a.title_original or "").lower()
            or q_en in (a.content_original or "").lower()
        ]
    return all_articles


def fetch_from_newsapi(query: str) -> List[Article]:
    """通过 NewsAPI 搜索新闻"""
    if not NEWSAPI_KEY:
        return []

    try:
        q_en = translate_to_english(query)
        params = {
            "q": q_en,
            "language": "en",
            "pageSize": 50,
            "sortBy": "publishedAt",
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get(
            "https://newsapi.org/v2/everything", params=params, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    articles: List[Article] = []
    for item in data.get("articles", []):
        src = item.get("source") or {}
        url = item.get("url") or ""
        title = item.get("title") or ""
        desc = item.get("description") or ""
        if not url and not title:
            continue
        articles.append(
            Article(
                id=f"newsapi-{hash(url) % 100000}",
                url=url,
                source_id=src.get("id") or "newsapi",
                source_name=src.get("name") or "NewsAPI",
                region="western",
                language="en",
                fetched_at=datetime.now(timezone.utc),
                title_original=title,
                content_original=desc,
                credibility=0.85,
                bias=0.1,
            )
        )
    return articles


def fetch_from_gdelt_doc(query: str) -> List[Article]:
    """通过 GDELT DOC API 搜索文档"""
    try:
        q_en = translate_to_english(query)
        params = {
            "query": q_en,
            "mode": "ArtList",
            "maxrecords": 50,
            "format": "json",
        }
        resp = requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc", params=params, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    articles: List[Article] = []
    for item in data.get("articles", []):
        articles.append(
            Article(
                id=f"gdelt-doc-{item.get('url', '')[:50]}",
                url=item.get("url") or "",
                source_name=item.get("source") or "GDELT",
                source_id="gdelt",
                region="global",
                language="en",
                fetched_at=datetime.now(timezone.utc),
                title_original=item.get("title") or "",
                credibility=0.7,
                bias=0.1,
            )
        )
    return articles


def fetch_from_gdelt_event(query: str) -> List[Article]:
    """通过 GDELT Event API 搜索事件"""
    try:
        q_en = translate_to_english(query)
        params = {
            "query": q_en,
            "mode": "EventList",
            "format": "json",
            "maxrecords": 50,
        }
        resp = requests.get(
            "https://api.gdeltproject.org/api/v2/events/events",
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    articles: List[Article] = []
    for idx, item in enumerate(data.get("events", [])):
        title = f"{item.get('Actor1Name', '')} - {item.get('EventRootCode', '')}"
        articles.append(
            Article(
                id=f"gdelt-ev-{idx}",
                url=item.get("SOURCEURL") or "",
                source_name=item.get("SOURCE") or "GDELT",
                source_id="gdelt",
                region="global",
                language="en",
                fetched_at=datetime.now(timezone.utc),
                title_original=title or "GDELT 事件",
                credibility=0.6,
                bias=0.1,
            )
        )
    return articles


def fetch_all_news(query: str) -> List[Article]:
    """
    核心融合函数：RSS + NewsAPI + GDELT DOC + GDELT Event
    去重返回统一的 Article 列表
    """
    rss_articles = fetch_from_rss(query)
    newsapi_articles = fetch_from_newsapi(query)
    gdelt_doc_articles = fetch_from_gdelt_doc(query)
    gdelt_event_articles = fetch_from_gdelt_event(query)

    all_articles = (
        rss_articles + newsapi_articles + gdelt_doc_articles + gdelt_event_articles
    )

    # 去重（按 url 或 title）
    seen: Dict[str, bool] = {}
    unique: List[Article] = []
    for a in all_articles:
        key = (a.url or "") + "||" + (a.title_original or "")
        if key in seen:
            continue
        seen[key] = True
        unique.append(a)

    return unique


def fetch_all_news_async(query: str) -> List[Article]:
    """
    异步版融合函数：使用 tools/news_fetcher.py 的异步抓取器
    在同步上下文中通过 asyncio.run() 调用
    """
    from fzq_ai.tools.news_fetcher import NewsFetcher as AsyncNewsFetcher

    async def _run():
        fetcher = AsyncNewsFetcher()
        return await fetcher.fetch_news(topic=query)

    try:
        return asyncio.run(_run())
    except RuntimeError:
        # 如果已经在事件循环中，回退到同步版
        return fetch_all_news(query)
