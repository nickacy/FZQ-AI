# -*- coding: utf-8 -*-
"""
FZQ-AI Web App (V15-Final)
双语情报工作台前端入口（Streamlit）

- 中文 / English 双语 UI
- 四大中文情报任务入口
- 统一错误边界
- 状态恢复（SessionState）
"""

from __future__ import annotations
import streamlit as st

from fzq_ai.ui.i18n import t
from fzq_ai.core.intent_engine import classify
from fzq_ai.core.task_router import TaskRouter

router = TaskRouter()


# ---------------- Session State ----------------

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


# ---------------- Layout ----------------

def main():
    st.set_page_config(page_title="FZQ-AI Intelligence Workbench", layout="wide")
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

    if st.button(t("app.run_button", lang)):
        state["last_input"] = text
        try:
            intent = classify(text)
            intent.task_type = task
            result = router.route(intent, text)
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
                "success": rr.success,
                "task_type": rr.task_type,
                "pipeline": rr.pipeline_used,
                "agent": rr.agent_used,
                "model": rr.model_used,
                "fallback_used": rr.fallback_used,
                "output": rr.output,
                "error": rr.error,
            }
        )


if __name__ == "__main__":
    main()
