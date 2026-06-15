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

# 多源 RSS 配置 (v2.6: 跨区域平衡 19 sources)
RSS_SOURCES = [
     "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
     "url": "http://rss.cnn.com/rss/edition_world.rss"},
     "url": "https://www.theguardian.com/world/rss"},
     "url": "https://www.aljazeera.com/xml/rss/all.xml"},
     "url": "https://www.arabnews.com/rss.xml"},
     "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
     "url": "https://en.yna.co.kr/RSS/news.xml"},
     "url": "https://www.straitstimes.com/news/asia/rss.xml"},
     "url": "http://www.xinhuanet.com/english/rss/worldrss.xml"},
     "url": "https://www.scmp.com/rss/91/feed"},
     "url": "https://www.globaltimes.cn/rss/world.xml"},
     "url": "https://www.rt.com/rss/news/"},
     "url": "https://tass.com/rss/v2.xml"},
     "url": "https://www.telesurenglish.net/rss/RssNews.xml"},
     "url": "https://en.mercopress.com/rss/index.xml"},
     "url": "https://feeds.news24.com/articles/news24/World/rss"},
     "url": "https://allafrica.com/tools/headlines/rss/latest/headlines.rss"},
]

def _parse_rss_source(cfg: Dict[str, Any]) -> List[Article]:
    """解析单个 RSS 源，返回 Article 列表"""
    try:
        for idx, entry in enumerate(feed.entries):
            url = entry.get("link") or ""
            title = entry.get("title") or ""
            summary = entry.get("summary") or ""
            if not url and not title:
    except Exception:
        pass  # 单个源失败不影响整体
    return articles

def fetch_from_rss(query: str = "") -> List[Article]:
    """同步抓取所有配置的 RSS 源"""
    for cfg in RSS_SOURCES:

    # ── 智能多级匹配 + 同义扩展 + 全量排序 (v2.6 fix) ──
    if query:

        # ── 同义词/近义词扩展 ──
            "iran": ["iranian", "tehran", "persian", "iran's"],
            "war": ["conflict", "military", "troops", "strike", "attack", "battle",
                    "combat", "missile", "drone", "invasion", "ceasefire"],
            "china": ["chinese", "beijing", "xi", "ccp"],
            "russia": ["russian", "moscow", "kremlin", "putin"],
            "us": ["america", "american", "washington", "white house", "u.s.", "usa",
                   "united states", "biden", "trump"],
            "election": ["vote", "voting", "ballot", "candidate", "campaign", "poll"],
            "economy": ["economic", "market", "trade", "gdp", "inflation", "stock"],
            "ai": ["artificial intelligence", "machine learning", "llm", "gpt"],
            "climate": ["environment", "carbon", "emission", "warming", "green"],

        # Expand query with synonyms
        for w in query_words:
            if w_clean in synonym_map:
            # Also add singular/plural variants
            if w_clean.endswith("s"):
                expanded_words.add(w_clean[:-1])
            elif not w_clean.endswith("s"):
                expanded_words.add(w_clean + "s")

                     "for", "and", "or", "by", "it", "be", "as", "we", "us",
                     "its", "has", "had", "was", "are", "were", "will", "can"}
        meaningful = {w for w in expanded_words if len(w) >= 2 and w not in stopwords}

        # 为每篇文章计算相关性分数（全量，不过滤）
        for a in all_articles:
            # 整体短语匹配
            if q_en in text or q_original in text:
            # 逐词匹配
            for w in meaningful:
                if w in text:
            # 可信度加权

        # 按分数降序排列（score=0 的排在末尾）
        all_articles = [a for _, a in scored]

    return all_articles

def fetch_from_newsapi(query: str) -> List[Article]:
    """通过 NewsAPI 搜索新闻"""
    if not NEWSAPI_KEY:
        return []

    try:
            "q": q_en,
            "language": "en",
            "pageSize": 50,
            "sortBy": "publishedAt",
            "apiKey": NEWSAPI_KEY,
            "https://newsapi.org/v2/everything", params=params, timeout=30
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    for item in data.get("articles", []):
        src = item.get("source") or {}
        url = item.get("url") or ""
        title = item.get("title") or ""
        desc = item.get("description") or ""
        if not url and not title:
    return articles

def fetch_from_gdelt_doc(query: str) -> List[Article]:
    """通过 GDELT DOC API 搜索文档"""
    try:
            "query": q_en,
            "mode": "ArtList",
            "maxrecords": 50,
            "format": "json",
            "https://api.gdeltproject.org/api/v2/doc/doc", params=params, timeout=30
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    for item in data.get("articles", []):
        articles.append(
            Article(
                id=f"gdelt-doc-{item.get('url', '')[:50]}",
                url=item.get("url") or "",
                source_name=item.get("source") or "GDELT",
                source_id="gdelt",
    return articles

def fetch_from_gdelt_event(query: str) -> List[Article]:
    """通过 GDELT Event API 搜索事件"""
    try:
            "query": q_en,
            "mode": "EventList",
            "format": "json",
            "maxrecords": 50,
            "https://api.gdeltproject.org/api/v2/events/events",
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    for idx, item in enumerate(data.get("events", [])):
        title = f"{item.get('Actor1Name', '')} - {item.get('EventRootCode', '')}"
        articles.append(
            Article(
                id=f"gdelt-ev-{idx}",
    return articles

def fetch_all_news(query: str, min_results: int = 50) -> List[Article]:
    """
    """

    # 去重
    for a in all_articles:
        if key in seen:

    # ── v2.7: Persist to IntelStore ──
    try:
    except Exception:

    # v2.6: 区域平衡重排
    unique = rebalance_articles(unique, min_count=min_results)

    # v2.6: 非英语内容 → 英文翻译预览
    for a in unique:
        if a.language not in ("zh", "en", "") and a.content_original:
            a.content_snippet_en = translate_snippet(
                a.content_original[:1000], target_lang="en"

    return unique

def rebalance_articles(articles: List[Article], min_count: int = 50) -> List[Article]:
    """

    """
    if len(articles) <= min_count:
        return articles

                  "latin_america", "east_asia", "southeast_asia"}

    for a in articles:

    result: List[Article] = []
    idx: Dict[str, int] = {r: 0 for r in region_order}

    if len(region_order) == 1:
        return articles[:max(len(articles), min_count)]

    # Round-robin interleave
    while len(result) < min_count and len(result) < len(articles):
        region = region_order[round_idx % len(region_order)]
        if idx[region] < len(buckets[region]):
            result.append(buckets[region][idx[region]])
            idx[region] += 1
        if all(idx[r] >= len(buckets[r]) for r in region_order):
            break

    # Enforce Global South >=30%
    gs_articles = [a for a in result if a.region in GS_REGIONS]
    target_gs = max(int(len(result) * 0.3), 10)

    if len(gs_articles) < target_gs:
        extra_gs = []
        for region in region_order:
            if region in GS_REGIONS:
                while idx[region] < len(buckets[region]):
                    extra_gs.append(buckets[region][idx[region]])
                    idx[region] += 1
        insert_every = max(2, len(result) // (target_gs - len(gs_articles) + 1))
        inserted = 0
        for i, gs_a in enumerate(extra_gs):
            if len(gs_articles) + inserted >= target_gs:
                break
            if pos < len(result):
                result.insert(pos, gs_a)
                inserted += 1

    # Append remaining
    for region in region_order:
        while idx[region] < len(buckets[region]) and len(result) < len(articles):
            result.append(buckets[region][idx[region]])
            idx[region] += 1

    return result

def translate_snippet(text: str, target_lang: str = "en") -> str:
    """
    """
    if not text:
        return ""
    try:
        if not DEEPSEEK_API_KEY:
            return text[:200]
        sys_msg = ("Translate to Chinese. Only return translation."
                   if target_lang == "zh"
                   else "Translate to English. Only return translation.")
            "model": DEEPSEEK_MODEL,
            "messages": [
            "temperature": 0.2,
                   "Content-Type": "application/json"}
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return text[:200]

def fetch_all_news_async(query: str) -> List[Article]:
    """
    """

    async def _run():
        fetcher = AsyncNewsFetcher()
        return await fetcher.fetch_news(topic=query)

    try:
        return asyncio.run(_run())
    except RuntimeError:
        return fetch_all_news(query)

# ============================================================
# v2.6: Balance Scoring
# ============================================================

def calculate_balance_score(articles: List[Article]) -> Dict[str, Any]:
    """
    Calculate source balance score for a set of articles.

    """
    if not articles:
        return {
            "source_region_distribution": {},
            "source_type_distribution": {},
            "balance_score": 0,
            "assessment": "no_data",
    for a in articles:
    if balance_score >= 70:
    elif balance_score >= 40:
    else:
    return {
        "source_region_distribution": region_dist,
        "source_type_distribution": {},
        "balance_score": balance_score,
        "assessment": assessment,
