# fzq_ai/ui/components/news_card.py

import streamlit as st
from fzq_ai.domain.models import Article


def render_news_card(article: Article):
    st.markdown("---")

    # 标题
    st.subheader(f"📰 {article.title_original or '无标题'}")

    # 来源
    st.write(f"**来源：** {article.source_name} ({article.region})")

    # 内容摘要
    if article.content_original:
        st.write(article.content_original)

    # 链接
    if article.url:
        st.markdown(f"[阅读原文]({article.url})")
