"""
fzq_ai/ui/components/risk_block.py — v2.6 Professional Risk Dashboard
"""

from __future__ import annotations
from typing import Any, Dict, List
import streamlit as st
from fzq_ai.ui.theme import COLORS, RISK_COLORS, region_tag, section_header, status_strip


def render_risk_block(risk_data: Any) -> None:
    section_header("Risk Analysis", "⚠️")

    if risk_data is None:
        status_strip("No risk data available", "info")
        return

    data: Dict[str, Any] = {}
    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data"):
        raw = getattr(risk_data, "data", {})
        data = raw if isinstance(raw, dict) else {}

    if not data:
        status_strip("No risk data available", "info")
        return

    # ── Overall Score ──
    overall = float(data.get("overall_risk_score", 0))
    if overall >= 70:
        level, emoji, color = "HIGH", "🔴", COLORS["danger"]
    elif overall >= 40:
        level, emoji, color = "MEDIUM", "🟡", COLORS["warning"]
    else:
        level, emoji, color = "LOW", "🟢", COLORS["success"]

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.metric("Overall Score", f"{overall:.0f}/100")
    with c2:
        st.markdown(
            f'<div style="background:{color}15;border:1px solid {color}30;'
            f'border-radius:10px;padding:14px 20px;text-align:center;">'
            f'<span style="font-size:32px;">{emoji}</span><br>'
            f'<span style="font-weight:700;color:{color};font-size:18px;">'
            f'{level} Risk</span></div>',
            unsafe_allow_html=True,
        )
    with c3:
        cats = len(data.get("category_intensity", {}))
        items = len(data.get("items", []))
        st.metric("Categories", str(cats))
        st.metric("Signals", str(items))

    # ── Category Breakdown ──
    category_intensity: Dict[str, int] = data.get("category_intensity", {})
    if category_intensity:
        st.markdown("#### Risk Category Distribution")
        cols = st.columns(len(category_intensity))
        labels = {
            "political": "🏛 Political", "economic": "💰 Economic",
            "military": "⚔ Military", "social": "👥 Social",
            "technology": "🔧 Tech",
        }
        for idx, (cat, count) in enumerate(category_intensity.items()):
            with cols[idx]:
                color = RISK_COLORS.get(min(count, 5), COLORS["text_secondary"])
                st.markdown(
                    f'<div style="text-align:center;padding:10px 6px;'
                    f'background:{color}10;border-radius:8px;'
                    f'border-top:3px solid {color};">'
                    f'<div style="font-size:22px;font-weight:700;color:{color};">'
                    f'{count}</div>'
                    f'<div style="font-size:11px;color:{COLORS["text_secondary"]};'
                    f'margin-top:4px;">{labels.get(cat, cat)}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── High-risk items ──
    items = data.get("items", [])
    high_risk = [i for i in items if i.get("risk_score", 0) >= 40]
    if high_risk:
        st.markdown("#### ⚡ High-Risk Signals")
        for item in high_risk[:8]:
            title = item.get("title", "Untitled")
            score = item.get("risk_score", 0)
            cats = item.get("risk_categories", [])
            region = item.get("region", "")
            tag_html = " ".join([
                f'<span class="fzq-tag" style="background:{COLORS["danger"]}">Risk {score}</span>'
            ] + [f'<span class="fzq-tag" style="background:{COLORS["primary_light"]}">{c}</span>' for c in cats])
            if region:
                tag_html += region_tag(region)
            st.markdown(
                f'<div class="fzq-card" style="padding:10px 16px;margin:4px 0;">'
                f'<span style="font-weight:500;">{title[:90]}</span>'
                f'<div style="margin-top:6px;">{tag_html}</div></div>',
                unsafe_allow_html=True,
            )
    elif items:
        status_strip(f"Analyzed {len(items)} signals — no elevated risk detected", "success")
