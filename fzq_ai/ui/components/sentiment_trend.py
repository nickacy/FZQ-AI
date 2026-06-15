"""
fzq_ai/ui/components/sentiment_trend.py
v2.6 — Sentiment trend chart using Streamlit.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st


def render_sentiment_trend(sentiment_data: Any) -> None:
    """
    Render sentiment distribution as a trend visualization.

    Args:
        sentiment_data: dict with distribution {positive, neutral, negative}
    """
    st.markdown("### 📊 舆情趋势图")

    data: Dict[str, Any] = {}
    if isinstance(sentiment_data, dict):
        data = sentiment_data
    elif hasattr(sentiment_data, "data"):
        data = getattr(sentiment_data, "data", {})

    distribution: Dict[str, Any] = data.get("distribution", {})
    if not distribution:
        st.info("暂无情感分布数据")
        return

    import pandas as pd

    categories = ["正面", "中性", "负面"]
    values = [
        distribution.get("positive", 0),
        distribution.get("neutral", 0),
        distribution.get("negative", 0),
    ]
    colors = ["#4CAF50", "#FFC107", "#F44336"]

    df = pd.DataFrame({"Sentiment": categories, "Count": values})

    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df.set_index("Sentiment"))
    with col2:
        total = sum(values) or 1
        for i, (cat, val, color) in enumerate(zip(categories, values, colors)):
            pct = round(val / total * 100, 1)
            st.markdown(
                f'<div style="display:flex;align-items:center;margin:4px 0;">'
                f'<div style="width:16px;height:16px;background:{color};'
                f'border-radius:3px;margin-right:8px;"></div>'
                f'<span>{cat}: {val} ({pct}%)</span></div>',
                unsafe_allow_html=True,
            )

    overall = data.get("overall_sentiment", "未知")
    if overall in ("偏正面", "positive"):
        st.success(f"总体情感倾向: {overall}")
    elif overall in ("偏负面", "negative"):
        st.error(f"总体情感倾向: {overall}")
    else:
        st.info(f"总体情感倾向: {overall}")
