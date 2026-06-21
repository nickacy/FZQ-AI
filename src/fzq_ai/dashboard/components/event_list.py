# fzq_ai/dashboard/components/event_list.py

import streamlit as st
from fzq_ai.domain.models import IntelBundle


def render_event_list(bundle: IntelBundle):
    """
    事件列表视图（Phase 5.4）
    - 展示事件 ID、主题、文章数量
    - 点击展开查看文章详情
    """

    st.title("📌 事件视图 Event View")
    st.markdown("按语义聚类展示新闻事件。")

    for ev in bundle.events:
        with st.expander(f"🧩 {ev.id} — {ev.topic}  ({len(ev.article_ids)} 篇文章)"):
            st.markdown("### 相关文章")

            for aid in ev.article_ids:
                article = next((a for a in bundle.articles if a.id == aid), None)
                if not article:
                    continue

                st.markdown(f"#### 📰 {article.title_original}")
                st.write(article.content_translated or article.content_original)

                st.caption(
                    f"来源：{article.source_name} | 区域：{article.region} | "
                    f"可信度：{article.credibility:.2f} | 偏见：{article.bias:.2f}"
                )

                if article.propaganda_tags:
                    st.markdown(f"**宣传标签：** {', '.join(article.propaganda_tags)}")

                st.markdown("---")
