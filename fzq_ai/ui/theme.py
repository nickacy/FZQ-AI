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
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    """, unsafe_allow_html=True)

def section_header(title: str, icon: str = "") -> None:
    i = f"{icon} " if icon else ""

def status_strip(text: str, level: str = "info") -> None:
    bg_map = {"info": "#1A2A3A", "success": "#1A2A1A",
              "warning": "#2A2A1A", "danger": "#2A1A1A"}
                  "warning": COLORS["warning"], "danger": COLORS["danger"]}

def region_tag(region: str) -> str:
    c = COLORS.get(region, COLORS["text_dim"])
    lb = {"western":"WEST","china":"CN","russia":"RU","middle_east":"ME",
          "east_asia":"EA","africa":"AF","latin_america":"LA","southeast_asia":"SEA"}
    return f'<span class="fzq-tag" style="background:{c}">{l}</span>'

def card(*content: str, title: str = "", **kwargs) -> None:
    th = f'<div style="font-weight:500;margin-bottom:6px;color:{COLORS["text_bright"]}">{title}</div>' if title else ""
