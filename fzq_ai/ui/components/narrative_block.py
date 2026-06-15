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

    data: Dict[str, Any] = {}
    if isinstance(narrative_data, dict):
        data = narrative_data
    elif hasattr(narrative_data, "data"):
        raw = getattr(narrative_data, "data", {})
        data = raw if isinstance(raw, dict) else {}

    if not data:
        st.info("No narrative data available")
        return

    # Find which blocs have content
    active_blocs = []
    for bloc in ["western", "east_asia", "china", "middle_east", "russia", "africa", "latin_america"]:
        bd = data.get(bloc, {})
        if isinstance(bd, dict) and (bd.get("themes") or bd.get("articles")):
            active_blocs.append(bloc)

    if not active_blocs:
        st.info("No significant narrative blocs detected")
        return

    # ── Cards per bloc ──
    cols = st.columns(min(len(active_blocs), 4))
    for idx, bloc in enumerate(active_blocs):
        bd = data[bloc]
        meta = BLOC_DATA.get(bloc, BLOC_DATA["other"])
        themes = bd.get("themes", [])
        articles = bd.get("articles", [])

        with cols[idx % len(cols)]:
            st.markdown(
                f'<div style="background:{meta["color"]}10;border:1px solid {meta["color"]}30;'
                f'border-radius:10px;padding:14px;margin:4px 0;'
                f'border-top:4px solid {meta["color"]};">'
                f'<div style="font-size:18px;font-weight:700;color:{meta["color"]};'
                f'margin-bottom:8px;">{meta["icon"]} {meta["label"]}</div>'
                f'<div style="font-size:24px;font-weight:700;color:{COLORS["text_primary"]};">'
                f'{len(articles)}</div>'
                f'<div style="font-size:11px;color:{COLORS["text_secondary"]};">articles</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Theme details per bloc ──
    for bloc in active_blocs:
        bd = data[bloc]
        meta = BLOC_DATA.get(bloc, BLOC_DATA["other"])
        themes = bd.get("themes", [])
        articles = bd.get("articles", [])

        with st.expander(f"{meta['icon']} {meta['label']} — {len(themes)} themes, {len(articles)} articles"):
            if themes:
                st.markdown("**Core Themes**")
                theme_html = " ".join([
                    f'<span style="display:inline-block;background:{meta["color"]}20;'
                    f'color:{meta["color"]};padding:3px 10px;border-radius:12px;'
                    f'margin:2px;font-size:12px;font-weight:500;">{t[:40]}</span>'
                    for t in themes[:8]
                ])
                st.markdown(theme_html, unsafe_allow_html=True)

            if articles:
                st.markdown("**Sample Articles**")
                for a in articles[:5]:
                    title = a.get("title", "Untitled") if isinstance(a, dict) else str(a)
                    st.markdown(f"- {title[:120]}")
