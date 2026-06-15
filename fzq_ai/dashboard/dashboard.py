# fzq_ai/dashboard/dashboard.py

import streamlit as st

from fzq_ai.dashboard.components.news_cards import render_news_cards
from fzq_ai.dashboard.components.event_list import render_event_list
from fzq_ai.dashboard.components.narrative_view import render_narrative_view

def render_dashboard(intel_bundle):
    """
    """

        "选择视图",
            "新闻列表 News Feed",
            "事件视图 Event View",
            "叙事视图 Narrative View",

    if page == "新闻列表 News Feed":

    elif page == "事件视图 Event View":

    elif page == "叙事视图 Narrative View":
