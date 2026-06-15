"""
fzq_ai/ui/theme.py — v2.6 Unified Design System

Professional color palette, typography, card styles, and CSS injection.
All components import THEME for consistent visual language.
"""

from __future__ import annotations

import streamlit as st

# ── Color Palette ──────────────────────────────────────────────
COLORS = {
    # Primary / brand
    "primary": "#1E3A5F",       # Deep navy
    "primary_light": "#2E5A8F",
    "accent": "#E85D2C",        # Warm orange
    "accent_light": "#F0805A",

    # Semantic
    "success": "#10B981",       # Emerald green
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "info": "#3B82F6",          # Blue

    # Neutrals
    "bg_light": "#F8FAFC",
    "bg_card": "#FFFFFF",
    "text_primary": "#1E293B",
    "text_secondary": "#64748B",
    "border": "#E2E8F0",
    "shadow": "rgba(0,0,0,0.06)",

    # Region colors
    "western": "#4A90E2",
    "china": "#E02424",
    "russia": "#7C3AED",
    "middle_east": "#059669",
    "east_asia": "#D97706",
    "africa": "#65A30D",
    "latin_america": "#0891B2",
    "southeast_asia": "#C2410C",
}

# ── Risk level colors ──────────────────────────────────────────
RISK_COLORS = {
    1: "#10B981", 2: "#84CC16", 3: "#F59E0B", 4: "#F97316", 5: "#EF4444",
}

# ── CSS Injection ──────────────────────────────────────────────

def inject_theme() -> None:
    """Inject global CSS for consistent styling across all components."""
    st.markdown(f"""
    <style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.01em;
    }}

    /* ── Cards ── */
    .fzq-card {{
        background: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 16px 20px;
        margin: 8px 0;
        box-shadow: 0 1px 3px {COLORS["shadow"]};
        transition: box-shadow 0.2s;
    }}
    .fzq-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}

    /* ── Section headers ── */
    .fzq-section {{
        border-left: 2px solid {COLORS["primary"]};
        padding-left: 14px;
        margin: 24px 0 12px 0;
    }}
    .fzq-section h2, .fzq-section h3 {{
        margin: 0;
        color: {COLORS["text_primary"]};
        font-weight: 600;
    }}

    /* ── Metrics badge ── */
    .fzq-badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        color: #fff;
    }}
    .fzq-badge-success {{ background: {COLORS["success"]}; }}
    .fzq-badge-warning {{ background: {COLORS["warning"]}; }}
    .fzq-badge-danger  {{ background: {COLORS["danger"]}; }}
    .fzq-badge-info    {{ background: {COLORS["info"]}; }}

    /* ── Region tags ── */
    .fzq-tag {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
        color: #fff;
        margin: 0 2px;
    }}

    /* ── Status strip ── */
    .fzq-status {{
        padding: 10px 16px;
        border-radius: 8px;
        margin: 8px 0;
        font-weight: 500;
        font-size: 14px;
    }}

    /* ── Divider ── */
    .fzq-divider {{
        height: 1px;
        background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["border"]});
        margin: 20px 0;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS["primary"]} 0%, #0F2640 100%);
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {{
        color: rgba(255,255,255,0.85) !important;
    }}

    /* ── Bloomberg-style nav indicators ── */
.fzq-nav-pill::before {
    content: '';
    display: inline-block;
    width: 7px;
    height: 7px;
    border: 1.5px solid rgba(255,255,255,0.35);
    margin-right: 12px;
    flex-shrink: 0;
}
.fzq-nav-pill.active::before {
    border-color: #E85D2C;
    background: #E85D2C;
    box-shadow: 0 0 8px rgba(232,93,44,0.4);
}

/* ── Buttons ── */
    .stButton > button {{
        background: {COLORS["accent"]} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 24px !important;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        background: {COLORS["accent_light"]} !important;
        box-shadow: 0 4px 12px rgba(232,93,44,0.3);
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input {{
        border-radius: 8px !important;
        border: 2px solid {COLORS["border"]} !important;
        font-size: 15px !important;
        padding: 10px 14px !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {COLORS["primary_light"]} !important;
        box-shadow: 0 0 0 3px rgba(30,58,95,0.1) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ── Helper Functions ───────────────────────────────────────────

def section_header(title: str, icon: str = "") -> None:
    """Render a consistent section header."""
    icon_str = f"{icon} " if icon else ""
    st.markdown(
        f'<div class="fzq-section"><h3>{icon_str}{title}</h3></div>',
        unsafe_allow_html=True,
    )


def metric_row(metrics: dict) -> None:
    """Render a row of key metrics."""
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label=label, value=value)


def status_strip(text: str, level: str = "info") -> None:
    """Render a colored status strip."""
    bg_colors = {
        "info": "#EFF6FF", "success": "#ECFDF5",
        "warning": "#FFFBEB", "danger": "#FEF2F2",
    }
    text_colors = {
        "info": "#1E40AF", "success": "#065F46",
        "warning": "#92400E", "danger": "#991B1B",
    }
    st.markdown(
        f'<div class="fzq-status" style="background:{bg_colors.get(level, bg_colors["info"])};'
        f'color:{text_colors.get(level, text_colors["info"])};">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


def region_tag(region: str) -> str:
    """Return an HTML tag for a region."""
    color = COLORS.get(region, COLORS["text_secondary"])
    labels = {
        "western": "West", "china": "China", "russia": "Russia",
        "middle_east": "Mid East", "east_asia": "E Asia",
        "africa": "Africa", "latin_america": "LatAm",
        "southeast_asia": "SE Asia",
    }
    label = labels.get(region, region.replace("_", " ").title())
    return f'<span class="fzq-tag" style="background:{color}">{label}</span>'


def card(*content: str, title: str = "", **kwargs) -> None:
    """Render a card container."""
    title_html = f'<div style="font-weight:600;margin-bottom:8px;color:{COLORS["text_primary"]}">{title}</div>' if title else ""
    inner = "".join(content)
    st.markdown(
        f'<div class="fzq-card">{title_html}{inner}</div>',
        unsafe_allow_html=True,
    )
