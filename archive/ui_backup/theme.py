"""
fzq_ai/ui/theme.py — Bloomberg Terminal Dark Design System
Pure dark theme: industrial edges, amber accents, terminal aesthetic.
"""

from __future__ import annotations
import streamlit as st

# ── Bloomberg Terminal Color Palette ───────────────────────────
COLORS = {
    # Core
    "bg":          "#0D0D0D",  # Terminal black
    "bg_panel":    "#141414",  # Slightly lighter panel
    "bg_card":     "#1A1A1A",  # Card background
    "bg_hover":    "#222222",  # Hover state

    # Text
    "text":        "#B0B0B0",  # Dim white (terminal text)
    "text_bright": "#E0E0E0",  # Bright text
    "text_dim":    "#606060",  # Dimmed text

    # Accent (Bloomberg orange)
    "accent":       "#FF6600",
    "accent_dim":   "#CC5500",

    # Semantic (terminal-style)
    "success":      "#00CC66",  # Green
    "warning":      "#FFAA00",  # Amber
    "danger":       "#FF3333",  # Red
    "info":         "#3399FF",  # Blue

    # Borders
    "border":       "#2A2A2A",
    "border_light": "#3A3A3A",

    # Region
    "western":       "#4488CC",
    "china":         "#DD3333",
    "russia":        "#8855DD",
    "middle_east":   "#22AA66",
    "east_asia":     "#CC8833",
    "africa":        "#66AA22",
    "latin_america": "#2288AA",
    "southeast_asia":"#CC5522",
}

RISK_COLORS = {
    1: "#00CC66", 2: "#88CC22", 3: "#FFAA00", 4: "#FF6600", 5: "#FF3333",
}


def inject_theme() -> None:
    """Inject Bloomberg Terminal dark CSS."""
    st.markdown(f"""
    <style>
    /* ── Global Reset ── */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
        background: {COLORS["bg"]};
        color: {COLORS["text"]};
    }}

    /* ── Main content background ── */
    .stApp, .main .block-container {{
        background: {COLORS["bg"]};
    }}

    /* ── Section headers ── */
    .fzq-section {{
        border-left: 2px solid {COLORS["accent"]};
        padding-left: 10px;
        margin: 20px 0 10px 0;
    }}
    .fzq-section h2, .fzq-section h3 {{
        margin: 0; color: {COLORS["text_bright"]};
        font-weight: 500; font-size: 15px;
        text-transform: uppercase; letter-spacing: 1px;
    }}

    /* ── Cards (terminal panels) ── */
    .fzq-card {{
        background: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 0;
        padding: 12px 16px;
        margin: 4px 0;
    }}
    .fzq-card:hover {{
        border-color: {COLORS["border_light"]};
    }}

    /* ── Status strip ── */
    .fzq-status {{
        padding: 8px 14px; margin: 6px 0;
        font-size: 13px; font-weight: 500;
        border-radius: 0; border-left: 3px solid;
    }}

    /* ── Tags ── */
    .fzq-tag {{
        display: inline-block; padding: 1px 8px;
        border-radius: 0; font-size: 10px;
        font-weight: 600; color: {COLORS["bg"]};
        margin: 0 2px; text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .fzq-badge {{
        display: inline-block; padding: 2px 8px;
        border-radius: 0; font-size: 11px; font-weight: 600;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: {COLORS["bg_panel"]};
        border-right: 1px solid {COLORS["border"]};
    }}
    section[data-testid="stSidebar"] * {{
        color: {COLORS["text"]} !important;
        font-family: 'IBM Plex Sans', sans-serif;
    }}

    /* ── Sidebar key status ── */
    .fzq-key-dot {{
        display: inline-block; width: 6px; height: 6px;
        border-radius: 50%; margin-right: 8px;
    }}
    .fzq-key-row {{
        display: flex; align-items: center;
        padding: 2px 0; font-size: 11px;
    }}
    .fzq-key-row .label {{ width: 65px; }}
    .fzq-key-row .status {{ font-weight: 500; }}

    /* ── Nav pills ── */
    .fzq-nav-pill {{
        display: block; padding: 8px 14px; margin: 2px 0;
        font-size: 13px; font-weight: 400; cursor: pointer;
        border: 1px solid transparent; border-radius: 0;
        background: transparent; color: {COLORS["text"]} !important;
        transition: background 0.15s;
    }}
    .fzq-nav-pill:hover {{
        background: {COLORS["bg_card"]}; border-color: {COLORS["border"]};
    }}
    .fzq-nav-pill.active {{
        background: {COLORS["bg_card"]};
        border-color: {COLORS["accent"]};
        color: {COLORS["accent"]} !important;
    }}
    .fzq-nav-pill::before {{
        content: ''; display: inline-block;
        width: 6px; height: 6px; margin-right: 10px;
        border: 1px solid {COLORS["text_dim"]}; flex-shrink: 0;
    }}
    .fzq-nav-pill.active::before {{
        background: {COLORS["accent"]}; border-color: {COLORS["accent"]};
    }}

    /* ── Divider ── */
    .fzq-sidebar-div {{
        height: 1px; background: {COLORS["border"]}; margin: 12px 0;
    }}
    .fzq-divider {{
        height: 1px; background: {COLORS["border"]}; margin: 16px 0;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: {COLORS["accent"]} !important;
        color: {COLORS["bg"]} !important;
        border: none !important; border-radius: 0 !important;
        font-weight: 600 !important; padding: 8px 20px !important;
        font-size: 13px !important; text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .stButton > button:hover {{
        background: {COLORS["accent_dim"]} !important;
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input {{
        border-radius: 0 !important;
        border: 1px solid {COLORS["border"]} !important;
        background: {COLORS["bg_card"]} !important;
        color: {COLORS["text_bright"]} !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {COLORS["accent"]} !important;
        outline: none !important;
    }}

    /* ── Metrics ── */
    [data-testid="stMetricValue"] {{
        color: {COLORS["text_bright"]} !important;
        font-weight: 600 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {COLORS["text_dim"]} !important;
    }}

    /* ── Expanders ── */
    .streamlit-expanderHeader {{
        background: {COLORS["bg_card"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 0 !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {COLORS["text"]} !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom-color: {COLORS["accent"]} !important;
        color: {COLORS["accent"]} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def section_header(title: str, icon: str = "") -> None:
    i = f"{icon} " if icon else ""
    st.markdown(
        f'<div class="fzq-section"><h3>{i}{title}</h3></div>',
        unsafe_allow_html=True)

def status_strip(text: str, level: str = "info") -> None:
    bg_map = {"info": "#1A2A3A", "success": "#1A2A1A",
              "warning": "#2A2A1A", "danger": "#2A1A1A"}
    border_map = {"info": COLORS["info"], "success": COLORS["success"],
                  "warning": COLORS["warning"], "danger": COLORS["danger"]}
    st.markdown(
        f'<div class="fzq-status" style="background:{bg_map.get(level,bg_map["info"])};'
        f'border-left-color:{border_map.get(level,border_map["info"])};">{text}</div>',
        unsafe_allow_html=True)

def region_tag(region: str) -> str:
    c = COLORS.get(region, COLORS["text_dim"])
    lb = {"western":"WEST","china":"CN","russia":"RU","middle_east":"ME",
          "east_asia":"EA","africa":"AF","latin_america":"LA","southeast_asia":"SEA"}
    l = lb.get(region, region[:4].upper())
    return f'<span class="fzq-tag" style="background:{c}">{l}</span>'

def card(*content: str, title: str = "", **kwargs) -> None:
    th = f'<div style="font-weight:500;margin-bottom:6px;color:{COLORS["text_bright"]}">{title}</div>' if title else ""
    st.markdown(f'<div class="fzq-card">{th}{"".join(content)}</div>', unsafe_allow_html=True)
