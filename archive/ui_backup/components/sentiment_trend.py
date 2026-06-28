"""
fzq_ai/ui/components/sentiment_trend.py — v2.6 Professional Sentiment View
"""

from __future__ import annotations
from typing import Any, Dict
import streamlit as st
from fzq_ai.ui.theme import COLORS, section_header, status_strip


def render_sentiment_trend(sentiment_data: Any) -> None:
    """
    Render sentiment distribution + overall verdict.
    Compatible with SentimentPipeline output.
    """

    section_header("Sentiment Analysis", "📊")

    # Normalize input
    if isinstance(sentiment_data, dict):
        data = sentiment_data
    elif hasattr(sentiment_data, "data"):
        raw = getattr(sentiment_data, "data", {})
        data = raw if isinstance(raw, dict) else {}
    else:
        st.info("No sentiment data available.")
        return

    if not data:
        st.info("No sentiment data available.")
        return

    # Extract fields
    dist: Dict[str, int] = data.get("distribution", {})
    overall = data.get("overall_sentiment", "中性")
    total = data.get("total_articles", 0)

    if not dist:
        st.info("No sentiment distribution available.")
        return

    pos = dist.get("positive", 0)
    neu = dist.get("neutral", 0)
    neg = dist.get("negative", 0)

    # ─────────────────────────────────────────────
    # Big Metric Row
    # ─────────────────────────────────────────────
    st.markdown("#### Sentiment Breakdown")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Positive", pos)

    with c2:
        st.metric("Neutral", neu)

    with c3:
        st.metric("Negative", neg)

    # ─────────────────────────────────────────────
    # Bar Visualization
    # ─────────────────────────────────────────────
    st.markdown("#### Distribution")

    total_width = max(pos + neu + neg, 1)

    pos_pct = pos / total_width * 100
    neu_pct = neu / total_width * 100
    neg_pct = neg / total_width * 100

    st.markdown(
        f"""
        <div style="display:flex; width:100%; height:22px; border-radius:6px; overflow:hidden;">
            <div style="width:{pos_pct}%; background:{COLORS['success']};"></div>
            <div style="width:{neu_pct}%; background:{COLORS['warning']};"></div>
            <div style="width:{neg_pct}%; background:{COLORS['danger']};"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Legend
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"<span style='color:{COLORS['success']};'>● Positive</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<span style='color:{COLORS['warning']};'>● Neutral</span>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<span style='color:{COLORS['danger']};'>● Negative</span>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Overall verdict
    # ─────────────────────────────────────────────
    st.markdown("#### Overall Sentiment")

    overall_str = str(overall)

    if "正面" in overall_str or "positive" in overall_str.lower():
        status_strip(f"Overall: {overall_str} — positive outlook", "success")
    elif "负面" in overall_str or "negative" in overall_str.lower():
        status_strip(f"Overall: {overall_str} — negative outlook", "danger")
    else:
        status_strip(f"Overall: {overall_str} — neutral outlook", "warning")
