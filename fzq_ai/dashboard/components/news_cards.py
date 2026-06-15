# fzq_ai/dashboard/components/news_cards.py

import streamlit as st

def render_news_cards(bundle):
    """
    """

    for article in bundle.articles:

        if article.propaganda_tags:

        st.markdown("### 📘 中文内容")
        st.write(article.content_translated or article.content_original)

        if article.language not in ["zh", "en"] and article.content_snippet_en:
            st.markdown("### 🌐 English snippet")
            st.code(article.content_snippet_en)

        with st.expander("查看原文"):
            st.write(article.content_original)
