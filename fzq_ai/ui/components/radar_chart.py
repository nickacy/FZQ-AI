"""
fzq_ai/ui/components/radar_chart.py
v2.6 — Risk Radar Chart using Streamlit native charts.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def render_radar_chart(risk_data: Any) -> None:
    """
    Render a radar/spider chart for multi-dimensional risk.

    Args:
        risk_data: dict with category_intensity {category: score}
    """
    st.markdown("### 🎯 风险雷达图")

    data: Dict[str, Any] = {}
    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data"):
        data = getattr(risk_data, "data", {})

    category_intensity: Dict[str, int] = data.get("category_intensity", {})
    if not category_intensity:
        st.info("暂无风险类别数据")
        return

    categories: List[str] = []
    values: List[int] = []
    labels: Dict[str, str] = {
        "political": "政治风险",
        "economic": "经济风险",
        "military": "军事风险",
        "social": "社会风险",
        "technology": "科技风险",
    }

    for cat, val in category_intensity.items():
        categories.append(labels.get(cat, cat))
        values.append(val)

    if HAS_PLOTLY:
        fig = go.Figure(
            data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name="风险强度",
                line_color="#D0021B",
            )
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(values) + 1])),
            showlegend=True,
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback: simple bar chart
        import pandas as pd
        df = pd.DataFrame({"category": categories, "score": values})
        st.bar_chart(df.set_index("category"))
