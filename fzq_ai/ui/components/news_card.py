"""
fzq_ai/ui/components/news_card.py
v2.6 — Rich news card with title, summary, source, risk, keywords, and link.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st
from fzq_ai.domain.models import Article


def render_news_card(article: Any) -> None:
    """
    Render a single news article as a rich card.

    Args:
        article: Article object or dict with title, source, summary, url, etc.
    """
    title: str = ""
    source: str = ""
    region: str = ""
    url: str = ""
    summary: str = ""
    published: str = ""
    risk_level: int = 0
    risk_type: str = ""
    credibility: float = 0.0
    language: str = ""

    if isinstance(article, Article):
        title = article.title_original or "Untitled"
        source = article.source_name or ""
        region = article.region or ""
        url = article.url or ""
        summary = article.content_original or ""
        credibility = article.credibility or 0.0
        language = article.language or ""
        published = str(article.fetched_at) if article.fetched_at else ""

    elif isinstance(article, dict):
        title = article.get("title_original") or article.get("title", "Untitled")
        source = article.get("source_name") or article.get("source", "")
        region = article.get("region", "")
        url = article.get("url", "")
        summary = article.get("content_original") or article.get("summary", "")
        credibility = article.get("credibility", 0.0)
        language = article.get("language", "")
        risk_level = article.get("risk_level", 0)
        risk_type = article.get("risk_type", "")
        published = article.get("published_at", "")
    else:
        st.write(str(article))
        return

    # Card container
    with st.container():
        # Title
        st.markdown(f"### 📰 {title[:100]}")

        # Meta row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.caption(f"**Source:** {source}")
        with col2:
            st.caption(f"**Region:** {region}")
        with col3:
            st.caption(f"**Lang:** {language}")
        with col4:
            if published:
                st.caption(f"**Published:** {published[:19]}")

        # Summary
        if summary:
            st.markdown(summary[:300])

        # Keywords / Tags row
        tags: List[str] = []
        if risk_type:
            tags.append(f"Risk: {risk_type}")
        if credibility:
            tags.append(f"Cred: {credibility:.1f}")
        if risk_level:
            level_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🔴"}
            tags.append(f"{level_emoji.get(risk_level, '⚪')} Risk Lv.{risk_level}")

        if tags:
            st.markdown(" · ".join(tags))

        # Link
        if url:
            st.markdown(f"[🔗 Read Original]({url})")

        st.markdown("---")
