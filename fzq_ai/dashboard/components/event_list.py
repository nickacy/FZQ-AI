# fzq_ai/dashboard/components/event_list.py

import streamlit as st
from fzq_ai.domain.models import IntelBundle

def render_event_list(bundle: IntelBundle):
    """
    """

    for ev in bundle.events:
        with st.expander(f"🧩 {ev.id} — {ev.topic}  ({len(ev.article_ids)} 篇文章)"):
            st.markdown("### 相关文章")

            for aid in ev.article_ids:
                article = next((a for a in bundle.articles if a.id == aid), None)
                if not article:

                st.markdown(f"#### 📰 {article.title_original}")
                st.write(article.content_translated or article.content_original)

                if article.propaganda_tags:

