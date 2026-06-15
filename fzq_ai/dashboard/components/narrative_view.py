# fzq_ai/dashboard/components/narrative_view.py

import streamlit as st

def render_narrative_view(bundle):
    """
    """

    # 按区域分组
    for a in articles:

    if not regions:
        return

    for region_name, region_articles in regions.items():
        with st.expander(f"🌍 {region_name.upper()} — {len(region_articles)} 篇"):
            for a in region_articles[:10]:
                st.markdown(f"#### 📰 {a.title_original}")
                st.caption(f"来源: {a.source_name} | 可信度: {a.credibility:.2f}")
                if a.content_original:
                        if len(a.content_original or "") > 300
                        else a.content_original
