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
        return

    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data"):
        raw = getattr(risk_data, "data", {})
        data = raw if isinstance(raw, dict) else {}

    if not data:
        return

    # ── Overall Score ──
    if overall >= 70:
    elif overall >= 40:
    else:

    with c1:
    with c2:
    with c3:

    # ── Category Breakdown ──
    if category_intensity:
        st.markdown("#### Risk Category Distribution")
        cols = st.columns(len(category_intensity))
        labels = {
            "political": "🏛 Political", "economic": "💰 Economic",
            "military": "⚔ Military", "social": "👥 Social",
            "technology": "🔧 Tech",
        for idx, (cat, count) in enumerate(category_intensity.items()):
            with cols[idx]:

    # ── High-risk items ──
    high_risk = [i for i in items if i.get("risk_score", 0) >= 40]
    if high_risk:
        st.markdown("#### ⚡ High-Risk Signals")
        for item in high_risk[:8]:
            ] + [f'<span class="fzq-tag" style="background:{COLORS["primary_light"]}">{c}</span>' for c in cats])
            if region:
    elif items:
