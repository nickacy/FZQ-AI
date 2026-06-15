"""
fzq_ai/ui/components/news_card.py — v2.6 Professional News Card
"""

from __future__ import annotations
from typing import Any, List
import streamlit as st
from fzq_ai.domain.models import Article
from fzq_ai.ui.theme import COLORS, region_tag


def render_news_card(article: Any) -> None:
    title = source = region = url = summary = language = ""
    credibility = 0.0

    if isinstance(article, Article):
        title = article.title_original or "Untitled"
        source = article.source_name or ""
        region = article.region or ""
        url = article.url or ""
        summary = article.content_original or ""
        credibility = article.credibility or 0.0
        language = article.language or ""
    elif isinstance(article, dict):
        title = article.get("title_original") or article.get("title", "Untitled")
        source = article.get("source_name") or article.get("source", "")
        region = article.get("region", "")
        url = article.get("url", "")
        summary = article.get("content_original") or article.get("summary", "")
        credibility = article.get("credibility", 0.0)
        language = article.get("language", "")
    else:
        st.write(str(article))
        return

    # ── Meta tags ──
    tags_html = ""
    if region:
        tags_html += region_tag(region)
    if language and language not in ("en", ""):
        tags_html += f' <span class="fzq-tag" style="background:{COLORS["primary_light"]}">{language.upper()}</span>'
    if credibility:
        cred_color = COLORS["success"] if credibility >= 0.8 else COLORS["warning"]
        tags_html += f' <span class="fzq-tag" style="background:{cred_color}">Cred {credibility:.1f}</span>'

    # ── Title with link ──
    title_display = f'<a href="{url}" target="_blank" style="text-decoration:none;color:{COLORS["text_primary"]};">{title[:120]}</a>' if url else title[:120]

    # ── Card ──
    snippet_html = ""
    if summary:
        snippet_html = (
            f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
            f'margin:8px 0;line-height:1.5;">{summary[:250]}</div>'
        )

    st.markdown(
        f'<div class="fzq-card">'
        f'<div style="font-weight:600;font-size:15px;margin-bottom:6px;">'
        f'{title_display}</div>'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
        f'<span style="font-size:12px;color:{COLORS["text_secondary"]};">'
        f'📰 {source}</span>'
        f'{tags_html}'
        f'</div>'
        f'{snippet_html}'
        f'</div>',
        unsafe_allow_html=True,
    )
