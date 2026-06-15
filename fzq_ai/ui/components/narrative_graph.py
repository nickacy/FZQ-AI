"""
fzq_ai/ui/components/narrative_graph.py
v2.6 — Narrative relationship graph visualization.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

try:
except ImportError:

def render_narrative_graph(narrative_data: Any) -> None:
    """

        narrative_data: dict with western, east_asia, middle_east, other blocs
    """
    st.markdown("### 🕸️ 叙事关系图谱")

    if isinstance(narrative_data, dict):
        data = narrative_data
    elif hasattr(narrative_data, "data"):
        data = getattr(narrative_data, "data", {})

    if not data:
        return

    # Build nodes and edges
        "western": "#4A90E2",
        "east_asia": "#D0021B",
        "middle_east": "#9013FE",
        "other": "#7ED321",

    for bloc, bloc_data in data.items():
        if not isinstance(bloc_data, dict):
            continue

        for theme in themes[:4]:
            if theme_node not in nodes:

    if not nodes:
        return

    if HAS_NETWORKX:
        for node in nodes:
        for u, v in edges:

        # Simple ASCII visualization
        st.markdown("### 叙事节点")
        for bloc in ["western", "east_asia", "middle_east", "other"]:
            if bloc not in data:
            color = colors.get(bloc, "#333")

            for t in themes[:5]:
    else:
        # Simple text-based view
        st.markdown("### 阵营叙事节点")
        for bloc in ["western", "east_asia", "middle_east", "other"]:
            if bloc not in data:
            color = colors.get(bloc, "#333")

            with st.expander(f"{bloc} ({len(articles)} articles)"):
                st.markdown(f"**Themes:** {', '.join(themes[:8])}")
                for a in articles[:5]:
                    title = a.get("title", "N/A") if isinstance(a, dict) else str(a)
                    st.markdown(f"- {title[:100]}")
