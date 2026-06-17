# fzq_ai/pipelines/news_fetcher.py
# Clean UTF‑8 safe version

import asyncio
from typing import List


async def fetch_all_news(raw_texts: List[str]) -> List[str]:
    """
    Mock news fetcher used for tests and offline mode.
    Simply returns the input list after a small async delay.
    """
    await asyncio.sleep(0.01)
    return raw_texts
