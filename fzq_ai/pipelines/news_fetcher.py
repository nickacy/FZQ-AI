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
    {"id": "bbc", "name": "BBC World", "region": "western", "language": "en",
     "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"id": "cnn", "name": "CNN World", "region": "western", "language": "en",
     "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"id": "guardian", "name": "The Guardian", "region": "western", "language": "en",
     "url": "https://www.theguardian.com/world/rss"},
    {"id": "aljazeera", "name": "Al Jazeera", "region": "middle_east", "language": "en",
     "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"id": "arabnews", "name": "Arab News", "region": "middle_east", "language": "en",
     "url": "https://www.arabnews.com/rss.xml"},
    {"id": "nhk", "name": "NHK Japan", "region": "east_asia", "language": "ja",
     "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
    {"id": "yonhap", "name": "Yonhap News", "region": "east_asia", "language": "en",
     "url": "https://en.yna.co.kr/RSS/news.xml"},
    {"id": "straitstimes", "name": "Straits Times", "region": "east_asia", "language": "en",
     "url": "https://www.straitstimes.com/news/asia/rss.xml"},
    {"id": "xinhuanet", "name": "Xinhua English", "region": "china", "language": "en",
     "url": "http://www.xinhuanet.com/english/rss/worldrss.xml"},
    {"id": "scmp", "name": "SCMP", "region": "china", "language": "en",
     "url": "https://www.scmp.com/rss/91/feed"},
    {"id": "globaltimes", "name": "Global Times", "region": "china", "language": "en",
     "url": "https://www.globaltimes.cn/rss/world.xml"},
    {"id": "rt", "name": "RT News", "region": "russia", "language": "en",
     "url": "https://www.rt.com/rss/news/"},
    {"id": "tass", "name": "TASS", "region": "russia", "language": "en",
     "url": "https://tass.com/rss/v2.xml"},
    {"id": "telesur", "name": "Telesur English", "region": "latin_america", "language": "en",
     "url": "https://www.telesurenglish.net/rss/RssNews.xml"},
    {"id": "mercopress", "name": "MercoPress", "region": "latin_america", "language": "en",
     "url": "https://en.mercopress.com/rss/index.xml"},
    {"id": "news24", "name": "News24 Africa", "region": "africa", "language": "en",
     "url": "https://feeds.news24.com/articles/news24/World/rss"},
    {"id": "allafrica", "name": "AllAfrica", "region": "africa", "language": "en",
     "url": "https://allafrica.com/tools/headlines/rss/latest/headlines.rss"},
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

    # ── 智能多级过滤 (v2.6 fix) ──
    if query:
        q_en = translate_to_english(query).lower()
        q_original = query.lower()

        # 拆分为单词（用于单篇匹配）
        query_words = set(q_en.split()) | set(q_original.split())
        # 过滤掉太短的停用词（a, an, the, in, on, of, to, is, ...）
        stopwords = {"a", "an", "the", "in", "on", "of", "to", "is", "at",
                     "for", "and", "or", "by", "it", "be", "as", "we", "us",
                     "its", "has", "had", "was", "are", "were", "will", "can"}

        # 第1级：整体短语匹配（精确）
        matched = [
            a for a in all_articles
            if q_en in (a.title_original or "").lower()
            or q_en in (a.content_original or "").lower()
            or q_original in (a.title_original or "").lower()
        ]

        # 第2级：单词级匹配（任一关键词命中）
        if not matched and len(query_words) > 0:
            meaningful_words = {w for w in query_words
                               if len(w) >= 2 and w not in stopwords}
            if meaningful_words:
                matched = [
                    a for a in all_articles
                    if any(
                        w in (a.title_original or "").lower()
                        or w in (a.content_original or "").lower()
                        for w in meaningful_words
                    )
                ]

        # 第3级：宽泛回退（前30条）
        if not matched:
            matched = all_articles[:30]

        # 第4级：数量不足时补齐至50（v2.6）
        if len(matched) < 50:
            # 添加尚未匹配的文章（按顺序）
            remaining = [a for a in all_articles if a not in matched]
            needed = 50 - len(matched)
            matched.extend(remaining[:needed])

        all_articles = matched

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


def fetch_all_news(query: str, min_results: int = 50) -> List[Article]:
    """
    核心融合函数：RSS + NewsAPI + GDELT DOC + GDELT Event
    去重 -> 平衡重排 -> 翻译预览 -> 返回 Article 列表 (v2.6)
    """
    rss_articles = fetch_from_rss(query)
    newsapi_articles = fetch_from_newsapi(query)
    gdelt_doc_articles = fetch_from_gdelt_doc(query)
    gdelt_event_articles = fetch_from_gdelt_event(query)

    all_articles = (
        rss_articles + newsapi_articles + gdelt_doc_articles + gdelt_event_articles
    )

    # 去重
    seen: Dict[str, bool] = {}
    unique: List[Article] = []
    for a in all_articles:
        key = (a.url or "") + "||" + (a.title_original or "")
        if key in seen:
            continue
        seen[key] = True
        unique.append(a)

    # v2.6: 区域平衡重排
    unique = rebalance_articles(unique, min_count=min_results)

    # v2.6: 非中英内容翻译预览
    for a in unique:
        if a.language not in ("zh", "en", "") and a.content_original:
            a.content_snippet_en = translate_snippet_to_chinese(
                a.content_original[:1000]
            )

    return unique


def rebalance_articles(articles: List[Article], min_count: int = 50) -> List[Article]:
    """
    v2.6: 区域平衡重排 - 从每个地区轮流取一篇，
    确保 Western / Global South / China / Russia / Africa 多样性。
    """
    if len(articles) <= min_count:
        return articles

    buckets: Dict[str, List[Article]] = {}
    for a in articles:
        region = a.region or "other"
        buckets.setdefault(region, []).append(a)

    result: List[Article] = []
    region_order = list(buckets.keys())
    idx: Dict[str, int] = {r: 0 for r in region_order}
    round_idx = 0

    if len(region_order) == 1:
        return articles[:max(len(articles), min_count)]

    while len(result) < min_count and len(result) < len(articles):
        region = region_order[round_idx % len(region_order)]
        if idx[region] < len(buckets[region]):
            result.append(buckets[region][idx[region]])
            idx[region] += 1
        round_idx += 1
        all_done = all(idx[r] >= len(buckets[r]) for r in region_order)
        if all_done:
            break

    # 追加剩余
    for region in region_order:
        while idx[region] < len(buckets[region]) and len(result) < len(articles):
            result.append(buckets[region][idx[region]])
            idx[region] += 1

    return result


def translate_snippet_to_chinese(text: str) -> str:
    """
    v2.6: 将非中英内容翻译为中文预览（前 1000 字符）。
    使用 DeepSeek API，失败时返回原文前 200 字符。
    """
    if not text:
        return ""
    has_cjk = any("\u4e00" <= c <= "\u9fff" for c in text[:50])
    if has_cjk:
        return text[:200]
    try:
        from fzq_ai.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL
        import requests as _r
        if not DEEPSEEK_API_KEY:
            return text[:200]
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "Translate to Chinese. Only return translation, no explanation."},
                {"role": "user", "content": text[:800]},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        resp = _r.post("https://api.deepseek.com/v1/chat/completions", json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return text[:200]


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
        return fetch_all_news(query)


# ============================================================
# v2.6: Balance Scoring
# ============================================================

def calculate_balance_score(articles: List[Article]) -> Dict[str, Any]:
    """
    Calculate source balance score for a set of articles.

    Returns:
        {source_region_distribution, source_type_distribution,
         balance_score (0-100), assessment}
    """
    if not articles:
        return {
            "source_region_distribution": {},
            "source_type_distribution": {},
            "balance_score": 0,
            "assessment": "no_data",
        }
    region_dist: Dict[str, int] = {}
    for a in articles:
        region = a.region or "unknown"
        region_dist[region] = region_dist.get(region, 0) + 1
    num_regions = len(region_dist)
    balance_score = min(num_regions * 20, 100)
    if balance_score >= 70:
        assessment = "balanced"
    elif balance_score >= 40:
        assessment = "moderately balanced"
    else:
        assessment = "unbalanced"
    return {
        "source_region_distribution": region_dist,
        "source_type_distribution": {},
        "balance_score": balance_score,
        "assessment": assessment,
    }
