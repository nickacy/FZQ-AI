"""
fzq_ai/ui/components/sentiment_trend.py — v2.6 Professional Sentiment View
"""

from __future__ import annotations
from typing import Any, Dict
import streamlit as st
from fzq_ai.ui.theme import COLORS, section_header, status_strip


def render_sentiment_trend(sentiment_data: Any) -> None:
    section_header("Sentiment Analysis", "📊")

    data: Dict[str, Any] = {}
    if isinstance(sentiment_data, dict):
        data = sentiment_data
    elif hasattr(sentiment_data, "data"):
        raw = getattr(sentiment_data, "data", {})
        data = raw if isinstance(raw, dict) else {}

    dist = data.get("distribution", {})
    if not dist:
        status_strip("No sentiment data available", "info")
        return

    pos = dist.get("positive", 0)
    neu = dist.get("neutral", 0)
    neg = dist.get("negative", 0)
    total = max(pos + neu + neg, 1)

    # ── Big Metric Row ──
    c1, c2, c3 = st.columns(3)
    for col, val, label, color, emoji in [
        (c1, pos, "Positive", COLORS["success"], "😊"),
        (c2, neu, "Neutral", COLORS["warning"], "😐"),
        (c3, neg, "Negative", COLORS["danger"], "😟"),
    ]:
        pct = round(val / total * 100, 1)
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:16px 8px;'
                f'background:{color}10;border-radius:12px;'
                f'border:1px solid {color}30;">'
                f'<div style="font-size:36px;">{emoji}</div>'
                f'<div style="font-size:28px;font-weight:700;color:{color};">{val}</div>'
                f'<div style="font-size:13px;color:{COLORS["text_secondary"]};">'
                f'{label} ({pct}%)</div></div>',
                unsafe_allow_html=True,
            )

    # ── Bar Visualization ──
    st.markdown("#### Distribution")
    total_width = 100
    p_pos = pos / total * total_width
    p_neu = neu / total * total_width
    p_neg = neg / total * total_width

    st.markdown(
        f'<div style="height:28px;border-radius:14px;overflow:hidden;display:flex;margin:8px 0;">'
        f'<div style="width:{p_pos}%;background:{COLORS["success"]};"></div>'
        f'<div style="width:{p_neu}%;background:{COLORS["warning"]};"></div>'
        f'<div style="width:{p_neg}%;background:{COLORS["danger"]};"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Legend ──
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;font-size:13px;">'
            f'<div style="width:12px;height:12px;border-radius:3px;background:{COLORS["success"]};"></div>'
            f'Positive ({p_pos:.0f}%)</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;font-size:13px;">'
            f'<div style="width:12px;height:12px;border-radius:3px;background:{COLORS["warning"]};"></div>'
            f'Neutral ({p_neu:.0f}%)</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;font-size:13px;">'
            f'<div style="width:12px;height:12px;border-radius:3px;background:{COLORS["danger"]};"></div>'
            f'Negative ({p_neg:.0f}%)</div>', unsafe_allow_html=True)

    # ── Overall verdict ──
    overall = data.get("overall_sentiment", "")
    if "正面" in overall or "positive" in str(overall).lower():
        status_strip(f"Overall: {overall} — positive outlook", "success")
    elif "负面" in overall or "negative" in str(overall).lower():
        status_strip(f"Overall: {overall} — negative outlook", "danger")
    else:
        status_strip(f"Overall: {overall} — balanced", "info")
