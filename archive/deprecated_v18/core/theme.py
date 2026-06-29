# -*- coding: utf-8 -*-
"""
FZQ-AI Theme System (V15-Final)
Bloomberg Terminal Dark Theme + UI Tokens + FastAPI Static Injection
"""

from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"


# ---------------------------------------------------------
# Bloomberg Terminal Dark Theme — 颜色系统（UI Tokens）
# ---------------------------------------------------------

THEME_TOKENS = {
    "background": "#0C0C0C",
    "panel": "#111111",
    "panel_alt": "#161616",
    "border": "#2A2A2A",
    "text_primary": "#E6E6E6",
    "text_secondary": "#A0A0A0",
    "accent_green": "#00FF41",
    "accent_yellow": "#F2E205",
    "accent_red": "#FF4D4D",
    "accent_blue": "#4DA6FF",
    "accent_orange": "#FF9933",
    "font_family": "Consolas, Menlo, Monaco, 'Courier New', monospace",
}


# ---------------------------------------------------------
# 自动生成 CSS（注入 Bloomberg Terminal 风格）
# ---------------------------------------------------------

def _generate_theme_css() -> str:
    """
    根据 THEME_TOKENS 自动生成全局 CSS。
    """
    t = THEME_TOKENS
    return f"""
    body {{
        background-color: {t['background']};
        color: {t['text_primary']};
        font-family: {t['font_family']};
    }}

    .panel {{
        background-color: {t['panel']};
        border: 1px solid {t['border']};
        padding: 12px;
        border-radius: 6px;
    }}

    .panel-alt {{
        background-color: {t['panel_alt']};
        border: 1px solid {t['border']};
        padding: 12px;
        border-radius: 6px;
    }}

    .accent-green {{ color: {t['accent_green']}; }}
    .accent-yellow {{ color: {t['accent_yellow']}; }}
    .accent-red {{ color: {t['accent_red']}; }}
    .accent-blue {{ color: {t['accent_blue']}; }}
    .accent-orange {{ color: {t['accent_orange']}; }}
    """
    


# ---------------------------------------------------------
# 写入 CSS 到 static/theme.css
# ---------------------------------------------------------

def _write_theme_css():
    STATIC_DIR.mkdir(exist_ok=True)
    css_path = STATIC_DIR / "theme.css"
    css_path.write_text(_generate_theme_css(), encoding="utf-8")


# ---------------------------------------------------------
# inject_theme(app) — 入口端调用
# ---------------------------------------------------------

def inject_theme(app: FastAPI):
    """
    将 Bloomberg Terminal Dark 主题注入 FastAPI：
    1. 写入 theme.css
    2. 挂载 /static
    3. 注入主题 tokens（供前端使用）
    """

    # 1) 写入 CSS 文件
    _write_theme_css()

    # 2) 挂载静态资源
    if not any(isinstance(r.app, StaticFiles) for r in app.router.routes):
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # 3) 注入主题 tokens（可被前端读取）
    app.state.theme = THEME_TOKENS

    print("[Theme] Bloomberg Terminal Dark Theme 已注入 /static/theme.css")
