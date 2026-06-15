"""
fzq_ai/ui/components/timeline.py — v2.6 Professional Timeline
"""

from __future__ import annotations
from typing import Any, List
from datetime import datetime
import streamlit as st
from fzq_ai.ui.theme import COLORS, region_tag, section_header

def render_timeline(articles: List[Any]) -> None:
    section_header("Event Timeline", "📅")

    if not articles:
        return

    # Sort by time
    for a in articles:
        t = getattr(a, "fetched_at", None) if hasattr(a, "fetched_at") else None
        sorted_articles.append((t or datetime.now(), a))
    sorted_articles.sort(key=lambda x: x[0], reverse=True)

    for i, (time_obj, a) in enumerate(sorted_articles[:20]):
        title = getattr(a, "title_original", "") if hasattr(a, "title_original") else str(a)
        source = getattr(a, "source_name", "") if hasattr(a, "source_name") else ""
        region = getattr(a, "region", "") if hasattr(a, "region") else ""
        url = getattr(a, "url", "") if hasattr(a, "url") else ""
        lang = getattr(a, "language", "") if hasattr(a, "language") else ""
        snippet = getattr(a, "content_snippet_en", "") if hasattr(a, "content_snippet_en") else ""

        time_str = time_obj.strftime("%m-%d %H:%M") if isinstance(time_obj, datetime) else ""
        tag_html = ""
        if region:
        if lang and lang not in ("en", ""):
            tag_html += f' <span class="fzq-tag" style="background:{COLORS["primary_light"]}">{lang}</span>'

        title_display = f"[{title[:100]}]({url})" if url else title[:100]

               f'font-style:italic;">EN: {snippet[:120]}</div>' if snippet else "") +
