"""
fzq_ai/ui/components/risk_block.py — v2.6 Professional Risk Dashboard
"""

from __future__ import annotations
from typing import Any, Dict, List
import streamlit as st

from fzq_ai.ui.theme import COLORS, RISK_COLORS, region_tag, section_header, status_strip


def render_risk_block(risk_data: Any) -> None:
    """
    Render a professional risk dashboard block.
    Compatible with RiskPipeline output.
    """

    section_header("Risk Analysis", "⚠️")

    # Normalize input
    if risk_data is None:
        st.info("No risk data available.")
        return

    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data"):
        raw = getattr(risk_data, "data", {})
        data = raw if isinstance(raw, dict) else {}
    else:
        st.info("Invalid risk data.")
        return

    if not data:
        st.info("No risk data available.")
        return

    # Extract fields
    overall: float = data.get("overall_risk", 0)
    category_intensity: Dict[str, float] = data.get("category_intensity", {})
    items: List[Dict] = data.get("items", [])

    # ─────────────────────────────────────────────
    # Overall Risk Score
    # ─────────────────────────────────────────────
    st.markdown("#### Overall Risk Score")

    if overall >= 70:
        level = "High"
        color = RISK_COLORS["high"]
    elif overall >= 40:
        level = "Medium"
        color = RISK_COLORS["medium"]
    else:
        level = "Low"
        color = RISK_COLORS["low"]

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        st.metric("Risk Level", level)

    with c2:
        st.metric("Score", f"{overall:.1f}")

    with c3:
        st.markdown(
            f"""
            <div style="
                background:{color};
                padding:10px;
                border-radius:6px;
                color:white;
                font-weight:bold;
                text-align:center;
            ">
                {level} Risk Zone
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ─────────────────────────────────────────────
    # Category Breakdown
    # ─────────────────────────────────────────────
    if category_intensity:
        st.markdown("#### Risk Category Distribution")

        labels = {
            "political": "🏛 Political",
            "economic": "💰 Economic",
            "military": "⚔ Military",
            "social": "👥 Social",
            "technology": "🔧 Tech",
        }

        cols = st.columns(len(category_intensity))

        for idx, (cat, score) in enumerate(category_intensity.items()):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="
                        background:{COLORS['primary_light']};
                        padding:10px;
                        border-radius:6px;
                        margin-bottom:6px;
                    ">
                        <b>{labels.get(cat, cat)}</b><br>
                        <span style="font-size:20px;">{score:.1f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────────
    # High-risk items
    # ─────────────────────────────────────────────
    high_risk = [i for i in items if i.get("risk_score", 0) >= 40]

    if high_risk:
        st.markdown("#### ⚡ High-Risk Signals")

        for item in high_risk[:8]:
            title = item.get("title", "N/A")
            region = item.get("region", "")
            cats = item.get("categories", [])
            score = item.get("risk_score", 0)

            cat_tags = " ".join(
                [
                    f'<span class="fzq-tag" style="background:{COLORS["primary_light"]}">{c}</span>'
                    for c in cats
                ]
            )

            st.markdown(
                f"""
                <div style="
                    border:1px solid #ddd;
                    padding:10px;
                    border-radius:6px;
                    margin-bottom:8px;
                ">
                    <b>{title}</b><br>
                    {region_tag(region)}<br>
                    <span style="color:{RISK_COLORS['high']}; font-weight:bold;">
                        Risk Score: {score}
                    </span><br>
                    {cat_tags}
                </div>
                """,
                unsafe_allow_html=True,
            )

    elif items:
        st.markdown("#### No high-risk items detected.")
