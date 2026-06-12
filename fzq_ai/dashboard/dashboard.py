# fzq_ai/dashboard/dashboard.py

import streamlit as st

from fzq_ai.dashboard.components.news_cards import render_news_cards
from fzq_ai.dashboard.components.event_list import render_event_list
from fzq_ai.dashboard.components.narrative_view import render_narrative_view


def render_dashboard(intel_bundle):
    """
    Dashboard 主入口
    """

    st.sidebar.title("📊 Dashboard")
    page = st.sidebar.radio(
        "选择视图",
        [
            "新闻列表 News Feed",
            "事件视图 Event View",
            "叙事视图 Narrative View",
        ],
    )

    if page == "新闻列表 News Feed":
        render_news_cards(intel_bundle)

    elif page == "事件视图 Event View":
        render_event_list(intel_bundle)

    elif page == "叙事视图 Narrative View":
        render_narrative_view(intel_bundle)
