"""
fzq_ai/ui/components/narrative_graph.py
v2.6 — Narrative relationship graph visualization.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


def render_narrative_graph(narrative_data: Any) -> None:
    """
    Render narrative clusters as a relationship graph.

    Args:
        narrative_data: dict with western, east_asia, middle_east, other blocs
    """
    st.markdown("### 🕸️ 叙事关系图谱")

    data: Dict[str, Any] = {}
    if isinstance(narrative_data, dict):
        data = narrative_data
    elif hasattr(narrative_data, "data"):
        data = getattr(narrative_data, "data", {})

    if not data:
        st.info("暂无叙事数据")
        return

    # Build nodes and edges
    nodes: List[str] = []
    edges: List[tuple] = []
    colors: Dict[str, str] = {
        "western": "#4A90E2",
        "east_asia": "#D0021B",
        "middle_east": "#9013FE",
        "other": "#7ED321",
    }

    for bloc, bloc_data in data.items():
        if not isinstance(bloc_data, dict):
            continue
        themes = bloc_data.get("themes", [])
        articles = bloc_data.get("articles", [])

        bloc_label = f"{bloc} ({len(articles)})"
        nodes.append(bloc_label)

        for theme in themes[:4]:
            theme_node = f"{theme}"
            if theme_node not in nodes:
                nodes.append(theme_node)
            edges.append((bloc_label, theme_node))

    if not nodes:
        st.info("暂无足够数据构建叙事图谱")
        return

    if HAS_NETWORKX:
        G = nx.Graph()
        for node in nodes:
            G.add_node(node)
        for u, v in edges:
            G.add_edge(u, v)

        pos = nx.spring_layout(G, seed=42)

        # Simple ASCII visualization
        st.markdown("### 叙事节点")
        for bloc in ["western", "east_asia", "middle_east", "other"]:
            if bloc not in data:
                continue
            bd = data[bloc]
            themes = bd.get("themes", [])
            articles = bd.get("articles", [])
            color = colors.get(bloc, "#333")

            st.markdown(
                f'<div style="background:{color};color:white;padding:4px 8px;'
                f'border-radius:4px;margin:4px 0;display:inline-block;">'
                f'{bloc}: {len(articles)} articles</div>',
                unsafe_allow_html=True,
            )
            for t in themes[:5]:
                st.markdown(f"- {t}")
            st.markdown("---")
    else:
        # Simple text-based view
        st.markdown("### 阵营叙事节点")
        for bloc in ["western", "east_asia", "middle_east", "other"]:
            if bloc not in data:
                continue
            bd = data[bloc]
            themes = bd.get("themes", [])
            articles = bd.get("articles", [])
            color = colors.get(bloc, "#333")

            with st.expander(f"{bloc} ({len(articles)} articles)"):
                st.markdown(f"**Themes:** {', '.join(themes[:8])}")
                for a in articles[:5]:
                    title = a.get("title", "N/A") if isinstance(a, dict) else str(a)
                    st.markdown(f"- {title[:100]}")
