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

    if isinstance(article, Article):
        title = article.title_original or "Untitled"
    elif isinstance(article, dict):
        title = article.get("title_original") or article.get("title", "Untitled")
        source = article.get("source_name") or article.get("source", "")
        region = article.get("region", "")
        url = article.get("url", "")
        summary = article.get("content_original") or article.get("summary", "")
        credibility = article.get("credibility", 0.0)
        language = article.get("language", "")
    else:
        return

    # ── Meta tags ──
    if region:
    if language and language not in ("en", ""):
        tags_html += f' <span class="fzq-tag" style="background:{COLORS["primary_light"]}">{language.upper()}</span>'
    if credibility:
        cred_color = COLORS["success"] if credibility >= 0.8 else COLORS["warning"]

    # ── Title with link ──
    title_display = f'<a href="{url}" target="_blank" style="text-decoration:none;color:{COLORS["text_primary"]};">{title[:120]}</a>' if url else title[:120]

    # ── Card ──
    if summary:

