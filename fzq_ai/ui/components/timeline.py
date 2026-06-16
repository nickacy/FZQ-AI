"""
fzq_ai/ui/components/timeline.py — v2.6 Professional Timeline
"""

from __future__ import annotations
from typing import Any, List
from datetime import datetime
import streamlit as st
from fzq_ai.ui.theme import COLORS, region_tag, section_header


def render_timeline(articles: List[Any]) -> None:
    """
    Render a chronological event timeline.
    Compatible with Article model from FZQ-AI.
    """

    section_header("Event Timeline", "📅")

    if not articles:
        st.info("No timeline data available.")
        return

    # ─────────────────────────────────────────────
    # Sort articles by fetched_at (newest first)
    # ─────────────────────────────────────────────
    sorted_articles = []

    for a in articles:
        t = getattr(a, "fetched_at", None)
        if isinstance(t, str):
            try:
                t = datetime.fromisoformat(t)
            except Exception:
                t = None
        sorted_articles.append((t or datetime.now(), a))

    sorted_articles.sort(key=lambda x: x[0], reverse=True)

    # ─────────────────────────────────────────────
    # Render timeline entries
    # ─────────────────────────────────────────────
    for time_obj, a in sorted_articles[:20]:
        title = getattr(a, "title_original", "") or ""
        source = getattr(a, "source_name", "") or ""
        region = getattr(a, "region", "") or ""
        url = getattr(a, "url", "") or ""
        lang = getattr(a, "language", "") or ""
        snippet = getattr(a, "content_snippet_en", "") or ""

        time_str = time_obj.strftime("%m-%d %H:%M") if isinstance(time_obj, datetime) else ""

        # Tags
        tag_html = ""
        if region:
            tag_html += region_tag(region)
        if lang and lang not in ("en", ""):
            tag_html += f' <span class="fzq-tag" style="background:{COLORS["primary_light"]}">{lang}</span>'

        # Title with link
        title_display = f"[{title[:100]}]({url})" if url else title[:100]

        # Snippet
        snippet_html = (
            f'<div style="color:#666; font-size:13px; margin-top:4px; font-style:italic;">'
            f'EN: {snippet[:120]}'
            f'</div>'
            if snippet
            else ""
        )

        # Render block
        st.markdown(
            f"""
            <div style="
                border-left:4px solid {COLORS['primary']};
                padding:10px 12px;
                margin-bottom:12px;
                background:#fafafa;
                border-radius:6px;
            ">
                <div style="font-size:13px; color:#999;">{time_str}</div>
                <div style="font-size:16px; font-weight:bold; margin:4px 0;">
                    {title_display}
                </div>
                <div style="font-size:13px; color:#555;">
                    {source} {tag_html}
                </div>
                {snippet_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
