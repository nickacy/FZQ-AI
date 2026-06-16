"""
fzq_ai/ui/components/radar_chart.py
v2.6 — Risk Radar Chart using Streamlit native charts or Plotly.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

# Optional Plotly support
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def render_radar_chart(risk_data: Any) -> None:
    """
    Render a radar/spider chart for multi-dimensional risk.

    risk_data: dict with category_intensity {category: score}
    """

    st.markdown("### 🎯 风险雷达图")

    # Normalize input
    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data"):
        data = getattr(risk_data, "data", {})
    else:
        st.info("No risk data available.")
        return

    category_intensity: Dict[str, float] = data.get("category_intensity", {})

    if not category_intensity:
        st.info("No risk categories found.")
        return

    # Labels for display
    labels = {
        "political": "政治风险",
        "economic": "经济风险",
        "military": "军事风险",
        "social": "社会风险",
        "technology": "科技风险",
    }

    categories: List[str] = []
    values: List[float] = []

    for cat, val in category_intensity.items():
        categories.append(labels.get(cat, cat))
        values.append(val)

    # Close the radar loop
    categories.append(categories[0])
    values.append(values[0])

    # -----------------------------
    # Plotly Radar Chart (if available)
    # -----------------------------
    if HAS_PLOTLY:
        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="Risk Levels",
                line_color="#D0021B",
            )
        )

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(values) * 1.2])
            ),
            showlegend=False,
            height=450,
        )

        st.plotly_chart(fig, use_container_width=True)
        return

    # -----------------------------
    # Fallback: Simple bar chart
    # -----------------------------
    st.warning("Plotly not installed — using fallback bar chart.")

    bar_data = {
        "Category": categories[:-1],
        "Score": values[:-1],
    }

    st.bar_chart(bar_data)
