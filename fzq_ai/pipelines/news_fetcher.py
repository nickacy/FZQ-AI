# fzq_ai/pipelines/news_fetcher.py
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

from fzq_ai.tools.translator import translate_to_english
from fzq_ai.domain.models import Article

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# 你可以自己扩展这个列表到 50+ 源
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.theguardian.com/world/rss",
    # ...
]

def fetch_from_rss(query: str) -> List[Article]:
    # 这里先给你一个占位，具体你可以用 feedparser 等库实现
    articles: List[Article] = []
    # TODO: 遍历 RSS_FEEDS，抓取后按标题/内容简单匹配 query
    return articles

def fetch_from_newsapi(query: str) -> List[Article]:
    if not NEWSAPI_KEY:
        return []

    q_en = translate_to_english(query)
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q_en,
        "language": "en",
        "pageSize": 50,  # 拉多一点
        "sortBy": "publishedAt",
        "apiKey": NEWSAPI_KEY,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    articles: List[Article] = []
    for item in data.get("articles", []):
        articles.append(
            Article(
                title_original=item.get("title"),
                source=item.get("source", {}).get("name"),
                url=item.get("url"),
                published_at=datetime.fromisoformat(item.get("publishedAt").replace("Z", "+00:00")),
            )
        )
    return articles

def fetch_from_gdelt_doc(query: str) -> List[Article]:
    q_en = translate_to_english(query)
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": q_en,
        "mode": "ArtList",
        "maxrecords": 50,
        "format": "json",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    articles: List[Article] = []
    for item in data.get("articles", []):
        articles.append(
            Article(
                title_original=item.get("title"),
                source=item.get("source"),
                url=item.get("url"),
                published_at=datetime.fromisoformat(item.get("seendate")),
            )
        )
    return articles

def fetch_from_gdelt_event(query: str) -> List[Article]:
    q_en = translate_to_english(query)
    url = "https://api.gdeltproject.org/api/v2/events/events"
    params = {
        "query": q_en,
        "mode": "EventList",
        "format": "json",
        "maxrecords": 50,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    articles: List[Article] = []
    for item in data.get("events", []):
        title = f"{item.get('Actor1Name', '')} - {item.get('EventRootCode', '')}"
        url_evt = item.get("SOURCEURL")
        articles.append(
            Article(
                title_original=title or "GDELT 事件",
                source=item.get("SOURCE"),
                url=url_evt,
                # GDELT 事件时间字段你可以按实际解析
            )
        )
    return articles

def fetch_all_news(query: str) -> List[Article]:
    """
    核心融合函数：RSS + NewsAPI + GDELT DOC + GDELT Event
    """
    rss_articles = fetch_from_rss(query)
    newsapi_articles = fetch_from_newsapi(query)
    gdelt_doc_articles = fetch_from_gdelt_doc(query)
    gdelt_event_articles = fetch_from_gdelt_event(query)

    all_articles = rss_articles + newsapi_articles + gdelt_doc_articles + gdelt_event_articles

    # 去重（按 url 或 title）
    seen = set()
    unique_articles: List[Article] = []
    for a in all_articles:
        key = (a.url or "", a.title_original or "")
        if key in seen:
            continue
        seen.add(key)
        unique_articles.append(a)

    return unique_articles
