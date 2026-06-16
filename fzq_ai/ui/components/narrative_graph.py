"""
fzq_ai/ui/components/narrative_graph.py
v2.6 — Narrative relationship graph visualization.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

# Optional: networkx + pyvis for graph visualization
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


def render_narrative_graph(narrative_data: Any) -> None:
    """
    Render a narrative relationship graph or fallback text view.

    narrative_data: dict with blocs:
        - western
        - east_asia
        - middle_east
        - other
    """

    st.markdown("### 🕸️ 叙事关系图谱")

    # Normalize input
    if isinstance(narrative_data, dict):
        data = narrative_data
    elif hasattr(narrative_data, "data"):
        data = getattr(narrative_data, "data", {})
    else:
        st.info("No narrative data available.")
        return

    if not data:
        st.info("No narrative data available.")
        return

    # Colors for blocs
    colors = {
        "western": "#4A90E2",
        "east_asia": "#D0021B",
        "middle_east": "#9013FE",
        "other": "#7ED321",
    }

    # Collect nodes and edges
    nodes = set()
    edges = []

    for bloc, bloc_data in data.items():
        if not isinstance(bloc_data, dict):
            continue

        themes: List[str] = bloc_data.get("themes", [])
        articles: List[Dict] = bloc_data.get("articles", [])

        # Add bloc node
        nodes.add(bloc)

        # Add theme nodes + edges
        for theme in themes[:6]:  # limit to avoid clutter
            theme_node = f"{bloc}:{theme}"
            nodes.add(theme_node)
            edges.append((bloc, theme_node))

    # If no nodes, nothing to draw
    if not nodes:
        st.info("No narrative nodes to visualize.")
        return

    # -----------------------------
    # Graph visualization (if networkx available)
    # -----------------------------
    if HAS_NETWORKX:
        G = nx.Graph()

        for n in nodes:
            G.add_node(n)

        for u, v in edges:
            G.add_edge(u, v)

        st.markdown("#### Network Graph (NetworkX)")
        st.write("节点数量:", len(nodes))
        st.write("边数量:", len(edges))

        # Simple networkx drawing
        try:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(8, 6))
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, node_size=500, font_size=8)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Graph rendering failed: {e}")

    # -----------------------------
    # Fallback: Text-based view
    # -----------------------------
    st.markdown("### 阵营叙事节点（文本视图）")

    for bloc in ["western", "east_asia", "middle_east", "other"]:
        if bloc not in data:
            continue

        bloc_data = data[bloc]
        themes = bloc_data.get("themes", [])
        articles = bloc_data.get("articles", [])

        color = colors.get(bloc, "#333")

        with st.expander(f"{bloc} — {len(articles)} 篇文章"):
            st.markdown(f"**Themes:** {', '.join(themes[:8])}")

            for a in articles[:5]:
                title = a.get("title", "N/A") if isinstance(a, dict) else str(a)
                st.markdown(f"- {title[:100]}")
