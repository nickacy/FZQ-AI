# fzq_ai/dashboard/components/news_cards.py

import streamlit as st
from fzq_ai.intel.models import Article


def render_news_cards(bundle):
    """
    新闻列表视图（News Feed）
    """

    st.title("📰 新闻列表 News Feed")

    for article in bundle.articles:
        st.markdown("---")
        st.subheader(article.title_original)

        cols = st.columns(4)
        cols[0].markdown(f"**来源：** {article.source_name}")
        cols[1].markdown(f"**区域：** {article.region}")
        cols[2].markdown(f"**可信度：** {article.credibility:.2f}")
        cols[3].markdown(f"**偏见：** {article.bias:.2f}")

        if article.propaganda_tags:
            st.markdown(f"**宣传标签：** {', '.join(article.propaganda_tags)}")

        st.markdown("### 📘 中文内容")
        st.write(article.content_translated or article.content_original)

        if article.language not in ["zh", "en"] and article.content_snippet_en:
            st.markdown("### 🌐 English snippet")
            st.code(article.content_snippet_en)

        with st.expander("查看原文"):
            st.write(article.content_original)
