"""
fzq_ai/ui/components/narrative_block.py — v2.6 Professional Narrative View
"""

from __future__ import annotations
from typing import Any, Dict, List
import streamlit as st
from fzq_ai.ui.theme import COLORS, section_header

BLOC_DATA = {
    "western":       {"label": "Western",       "color": COLORS["western"],       "icon": "🌍"},
    "east_asia":     {"label": "East Asia",     "color": COLORS["east_asia"],     "icon": "🌏"},
    "china":         {"label": "China",         "color": COLORS["china"],         "icon": "🇨🇳"},
    "middle_east":   {"label": "Middle East",   "color": COLORS["middle_east"],   "icon": "🕌"},
    "russia":        {"label": "Russia",        "color": COLORS["russia"],        "icon": "🇷🇺"},
    "africa":        {"label": "Africa",        "color": COLORS["africa"],        "icon": "🌍"},
    "latin_america": {"label": "Latin America", "color": COLORS["latin_america"], "icon": "🌎"},
    "other":         {"label": "Other",         "color": COLORS["text_secondary"], "icon": "📡"},
}

def render_narrative_block(narrative_data: Any) -> None:
    section_header("Multi-Blocs Narrative", "🧭")

    if isinstance(narrative_data, dict):
        data = narrative_data
    elif hasattr(narrative_data, "data"):
        raw = getattr(narrative_data, "data", {})
        data = raw if isinstance(raw, dict) else {}

    if not data:
        return

    # Find which blocs have content
    for bloc in ["western", "east_asia", "china", "middle_east", "russia", "africa", "latin_america"]:
        if isinstance(bd, dict) and (bd.get("themes") or bd.get("articles")):
            active_blocs.append(bloc)

    if not active_blocs:
        return

    # ── Cards per bloc ──
    for idx, bloc in enumerate(active_blocs):
        bd = data[bloc]

        with cols[idx % len(cols)]:
            st.markdown(
                f'<div style="background:{meta["color"]}10;border:1px solid {meta["color"]}30;'

    # ── Theme details per bloc ──
    for bloc in active_blocs:

        with st.expander(f"{meta['icon']} {meta['label']} — {len(themes)} themes, {len(articles)} articles"):
            if themes:
                    for t in themes[:8]

            if articles:
                for a in articles[:5]:
                    title = a.get("title", "Untitled") if isinstance(a, dict) else str(a)
                    st.markdown(f"- {title[:120]}")
