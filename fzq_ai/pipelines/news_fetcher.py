# fzq_ai/pipelines/news_fetcher.py

import aiohttp
import asyncio
from typing import List
from fzq_ai.domain.models import Article


NEWS_SOURCES = [
    # 你可以在这里添加更多源
    "https://newsapi.org/v2/everything?q={query}&apiKey=YOUR_KEY",
    "https://gnews.io/api/v4/search?q={query}&token=YOUR_KEY",
]


async def _fetch_one(session, url) -> List[Article]:
    """
    抓取单个新闻源（async）
    """
    try:
        async with session.get(url, timeout=10) as resp:
            data = await resp.json()

            articles = []
            for item in data.get("articles", []):
                articles.append(
                    Article(
                        title_original=item.get("title", ""),
                        source_name=item.get("source", {}).get("name", ""),
                        url=item.get("url", ""),
                    )
                )
            return articles

    except Exception:
        return []


async def _fetch_all_async(query: str) -> List[Article]:
    """
    并发抓取所有新闻源
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            _fetch_one(session, url.format(query=query))
            for url in NEWS_SOURCES
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 合并结果
    merged = []
    for r in results:
        if isinstance(r, list):
            merged.extend(r)

    return merged


def fetch_all_news(query: str) -> List[Article]:
    """
    同步入口（保持旧行为）
    - NewsPipeline 仍然可以同步调用
    - 内部使用 asyncio.run() 执行 async 并发抓取
    """
    try:
        return asyncio.run(_fetch_all_async(query))
    except RuntimeError:
        # 如果 event loop 已经在运行（如 Streamlit）
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_fetch_all_async(query))
