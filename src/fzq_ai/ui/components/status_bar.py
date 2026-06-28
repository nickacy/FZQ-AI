"""
V15 Status Bar Component.

Shows execution status: pipeline, model, tokens, duration.
Color-coded: green=success, red=error, blue=running.
"""

from __future__ import annotations
import streamlit as st
from fzq_ai.ui.i18n import t


class StatusBar:
    """Task execution status bar."""

    def __init__(self, lang: str = "zh"):
        self.lang = lang
        self.reset()

    def reset(self):
        self.status: str = "idle"
        self.pipeline: str = "-"
        self.model: str = "-"
        self.duration_ms: float = 0.0
        self.tokens: int = 0
        self.error: str = ""

    def update_from_result(self, result) -> None:
        """Populate status from a RouteResult."""
        self.status = "success" if getattr(result, "success", False) else "error"
        self.pipeline = getattr(result, "pipeline_used", "-") or "-"
        self.model = getattr(result, "model_used", "-") or "-"
        self.error = getattr(result, "error", "") or ""

    def set_running(self, pipeline: str = "", model: str = ""):
        self.status = "running"
        self.pipeline = pipeline or self.pipeline
        self.model = model or self.model

    def render(self):
        """Render the status strip."""
        color_map = {
            "success": "green",
            "error": "red",
            "running": "blue",
            "idle": "gray",
        }
        color = color_map.get(self.status, "gray")

        cols = st.columns(4)
        with cols[0]:
            st.markdown(f":{color}[ **{t('status.label', self.lang)}**: {self.status} ]")
        with cols[1]:
            st.caption(f"{t('status.pipeline', self.lang)}: {self.pipeline}")
        with cols[2]:
            st.caption(f"{t('status.model', self.lang)}: {self.model}")
        with cols[3]:
            st.caption(f"{t('status.duration', self.lang)}: {self.duration_ms:.0f}ms")

        if self.status == "error" and self.error:
            st.error(self.error)


def render_status_bar(result=None, lang: str = "zh") -> StatusBar:
    """Convenience function. Returns the bar so caller can update it."""
    bar = StatusBar(lang)
    if result is not None:
        bar.update_from_result(result)
    bar.render()
    return bar
