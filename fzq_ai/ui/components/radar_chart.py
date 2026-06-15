"""
fzq_ai/ui/components/radar_chart.py
v2.6 — Risk Radar Chart using Streamlit native charts.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

try:
except ImportError:

def render_radar_chart(risk_data: Any) -> None:
    """
    Render a radar/spider chart for multi-dimensional risk.

        risk_data: dict with category_intensity {category: score}
    """
    st.markdown("### 🎯 风险雷达图")

    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data"):
        data = getattr(risk_data, "data", {})

    if not category_intensity:
        return

        "political": "政治风险",
        "economic": "经济风险",
        "military": "军事风险",
        "social": "社会风险",
        "technology": "科技风险",

    for cat, val in category_intensity.items():
        categories.append(labels.get(cat, cat))
        values.append(val)

    if HAS_PLOTLY:
                line_color="#D0021B",
    else:
        # Fallback: simple bar chart
