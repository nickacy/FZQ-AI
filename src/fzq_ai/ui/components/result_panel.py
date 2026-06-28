"""
V15 Result Panel Component.

Unified rendering of RouteResult -> Streamlit display.
Supports JSON / Markdown / structured output modes.
Error fallback UI.
"""

from __future__ import annotations
import json
import streamlit as st
from fzq_ai.ui.i18n import t


class ResultPanel:
    """Unified result renderer for RouteResult objects."""

    def __init__(self, lang: str = "zh"):
        self.lang = lang

    def render(self, result) -> None:
        """Render a RouteResult into Streamlit widgets."""
        if result is None:
            return

        success = getattr(result, "success", False)
        output_data = getattr(result, "output", None)
        error = getattr(result, "error", None)

        if not success:
            self._render_error(error)
            return

        if output_data is None:
            st.info(t("result.no_output", self.lang))
            return

        # Detect output format
        if isinstance(output_data, str):
            self._render_text(output_data)
        elif isinstance(output_data, dict):
            self._render_structured(output_data)
        elif isinstance(output_data, list):
            self._render_list(output_data)
        else:
            st.write(output_data)

        # Metadata footer
        self._render_footer(result)

    def _render_text(self, text: str):
        st.markdown(text)

    def _render_structured(self, data: dict):
        """Try to render structured data with appropriate widgets."""
        # If it has markdown-like keys, render as text
        if any(k in str(data).lower() for k in ["report", "summary", "brief", "analysis"]):
            st.json(data)
        else:
            st.json(data)

    def _render_list(self, data: list):
        st.json(data)

    def _render_error(self, error):
        st.error(f"{t('result.error_prefix', self.lang)}: {error or t('result.unknown_error', self.lang)}")

    def _render_footer(self, result):
        with st.expander(t("result.details", self.lang)):
            st.caption(f"task_type: {getattr(result, 'task_type', '-')}")
            st.caption(f"pipeline: {getattr(result, 'pipeline_used', '-')}")
            st.caption(f"model: {getattr(result, 'model_used', '-')}")
            st.caption(f"agent: {getattr(result, 'agent_used', '-')}")
            st.caption(f"fallback_used: {getattr(result, 'fallback_used', False)}")


def render_result(result, lang: str = "zh") -> None:
    """Convenience function."""
    panel = ResultPanel(lang)
    panel.render(result)
