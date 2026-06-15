"""
fzq_ai/ui/components/timeline.py
v2.6 — Event timeline visualization.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st
from datetime import datetime


def render_timeline(articles: List[Any]) -> None:
    """
    Render articles in a chronological timeline.

    Args:
        articles: List of Article objects or dicts with title, source_name, fetched_at
    """
    st.markdown("### 📅 事件时间线")

    if not articles:
        st.info("暂无事件数据")
        return

    # Sort by time if available
    sorted_articles: List[Any] = []
    for a in articles:
        if hasattr(a, "fetched_at") and a.fetched_at:
            sorted_articles.append(a)
        elif isinstance(a, dict) and a.get("fetched_at"):
            sorted_articles.append(a)

    if not sorted_articles:
        # Just show the first 10 without sorting
        sorted_articles = articles[:10]
    else:
        def _get_time(a: Any) -> datetime:
            if hasattr(a, "fetched_at"):
                return a.fetched_at if isinstance(a.fetched_at, datetime) else datetime.now()
            elif isinstance(a, dict):
                return a.get("fetched_at", datetime.now())
            return datetime.now()

        sorted_articles.sort(key=_get_time, reverse=True)
        sorted_articles = sorted_articles[:20]

    for i, a in enumerate(sorted_articles):
        title = getattr(a, "title_original", "") or a.get("title_original", "") if isinstance(a, dict) else str(a)
        source = getattr(a, "source_name", "") or a.get("source_name", "") if isinstance(a, dict) else ""
        url = getattr(a, "url", "") or a.get("url", "") if isinstance(a, dict) else ""
        region = getattr(a, "region", "") or a.get("region", "") if isinstance(a, dict) else ""

        time_str = ""
        fetched = getattr(a, "fetched_at", None) if hasattr(a, "fetched_at") else None
        if fetched and isinstance(fetched, datetime):
            time_str = fetched.strftime("%m-%d %H:%M")

        st.markdown(
            f"**{i+1}.** {time_str} | {region} | {source}\n\n"
            f"{'[' + title[:100] + '](' + url + ')' if url else title[:100]}\n"
            f"---"
        )
