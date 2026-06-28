# -*- coding: utf-8 -*-
"""
FZQ-AI Web App (V15-Final)
Bilingual Intelligence Workbench (Streamlit)

- Chinese / English bilingual UI
- 4 ZH intelligence task entry points
- Unified error boundary
- State recovery (SessionState)
- Async execution via asyncio.run()
"""

from __future__ import annotations
import asyncio
import streamlit as st

from fzq_ai.ui.i18n import t
from fzq_ai.ui.theme import inject_theme
from fzq_ai.entry.entry_service import EntryService

service = EntryService()


# ── Session State ──────────────────────────────────────────────

def get_state():
    if "fzq_state" not in st.session_state:
        st.session_state["fzq_state"] = {
            "language": "zh",
            "last_task": None,
            "last_input": "",
            "last_result": None,
            "error": None,
        }
    return st.session_state["fzq_state"]


def _run_async(text: str, task_type: str):
    """Sync wrapper: run the async entry service via asyncio.run()."""
    return asyncio.run(service.handle(text, task_type))


# ── Layout ─────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="FZQ-AI Intelligence Workbench",
        page_icon=":robot:",
        layout="wide",
    )
    inject_theme()
    state = get_state()

    # Language toggle
    col_lang, _ = st.columns([1, 3])
    with col_lang:
        lang = st.radio(
            "Language / 语言",
            options=["zh", "en"],
            index=0 if state["language"] == "zh" else 1,
            horizontal=True,
        )
        state["language"] = lang

    # Header
    st.title(t("app.title", lang))
    st.caption(t("app.subtitle", lang))

    # Task selector
    task = st.selectbox(
        t("app.task_selector", lang),
        [
            "zh_policy_brief",
            "zh_risk_scan",
            "zh_opinion_landscape",
            "zh_multisource_merge",
        ],
        format_func=lambda x: t(f"task.{x}", lang),
    )
    state["last_task"] = task

    # Input area
    text = st.text_area(
        t("app.input_label", lang),
        value=state["last_input"],
        height=200,
    )

    # Run button - async execution via EntryService
    if st.button(t("app.run_button", lang)):
        state["last_input"] = text
        try:
            result = _run_async(text, task)
            state["last_result"] = result
            state["error"] = None
        except Exception as e:
            state["error"] = str(e)
            state["last_result"] = None

    # Error boundary
    if state["error"]:
        st.error(t("app.error_prefix", lang) + state["error"])
        return

    # Result display
    if state["last_result"]:
        rr = state["last_result"]
        st.markdown("### " + t("app.result_title", lang))
        st.json(
            {
                "success": getattr(rr, "success", None),
                "task_type": getattr(rr, "task_type", None),
                "pipeline": getattr(rr, "pipeline_used", None),
                "agent": getattr(rr, "agent_used", None),
                "model": getattr(rr, "model_used", None),
                "fallback_used": getattr(rr, "fallback_used", None),
                "output": getattr(rr, "output", None),
                "error": getattr(rr, "error", None),
            }
        )


if __name__ == "__main__":
    main()
