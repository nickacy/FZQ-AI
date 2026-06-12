# fzq_ai/dashboard/components/narrative_view.py

import streamlit as st


def render_narrative_view(bundle):
    """
    叙事视图（Narrative View）
    按 region 展示各阵营新闻
    """
    st.title("🧭 多阵营叙事视图 Narrative View")

    articles = getattr(bundle, "articles", []) or []

    # 按区域分组
    regions: dict = {}
    for a in articles:
        r = (a.region or "other").lower()
        regions.setdefault(r, []).append(a)

    if not regions:
        st.info("暂无叙事数据")
        return

    for region_name, region_articles in regions.items():
        with st.expander(f"🌍 {region_name.upper()} — {len(region_articles)} 篇"):
            for a in region_articles[:10]:
                st.markdown(f"#### 📰 {a.title_original}")
                st.caption(f"来源: {a.source_name} | 可信度: {a.credibility:.2f}")
                if a.content_original:
                    st.write(a.content_original[:300] + "..." if len(a.content_original or "") > 300 else a.content_original)
                st.markdown("---")
