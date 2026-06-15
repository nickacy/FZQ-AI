"""
fzq_ai/ui/components/sentiment_trend.py — v2.6 Professional Sentiment View
"""

from __future__ import annotations
from typing import Any, Dict
import streamlit as st
from fzq_ai.ui.theme import COLORS, section_header, status_strip

def render_sentiment_trend(sentiment_data: Any) -> None:
    section_header("Sentiment Analysis", "📊")

    if isinstance(sentiment_data, dict):
        data = sentiment_data
    elif hasattr(sentiment_data, "data"):
        raw = getattr(sentiment_data, "data", {})
        data = raw if isinstance(raw, dict) else {}

    if not dist:
        return

    # ── Big Metric Row ──
    for col, val, label, color, emoji in [
        with col:

    # ── Bar Visualization ──
    st.markdown("#### Distribution")
    total_width = 100

    # ── Legend ──
    with c1:
    with c2:
    with c3:

    # ── Overall verdict ──
    if "正面" in overall or "positive" in str(overall).lower():
        status_strip(f"Overall: {overall} — positive outlook", "success")
    elif "负面" in overall or "negative" in str(overall).lower():
        status_strip(f"Overall: {overall} — negative outlook", "danger")
    else:
