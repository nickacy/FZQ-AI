# fzq_ai/ui/components/narrative_block.py

import streamlit as st
from fzq_ai.intel.models import Narrative

BLOC_COLORS = {
    "western": "#4A90E2",
    "china": "#D0021B",
    "russia": "#9013FE",
    "global_south": "#7ED321",
}


def render_narrative_block(narratives: list[Narrative]):
    st.header("🧭 多阵营叙事对比")

    if not narratives:
        st.info("暂无叙事数据")
        return

    for n in narratives:
        st.markdown(f"## 🧩 事件 {n.event_id}")

        # -----------------------------
        # 四阵营横向卡片布局
        # -----------------------------
        st.markdown("### 🌍 多阵营叙事")

        cols = st.columns(4)

        for idx, (bloc, text) in enumerate(n.narratives.items()):
            with cols[idx]:
                color = BLOC_COLORS.get(bloc, "#333")

                st.markdown(
                    f"""
                    <div style="
                        background-color:{color};
                        padding:8px 12px;
                        border-radius:6px;
                        color:white;
                        font-weight:bold;
                        text-align:center;
                        margin-bottom:8px;">
                        {bloc.replace('_', ' ').title()}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div style="
                        background-color:#F7F7F7;
                        padding:12px;
                        border-radius:6px;
                        min-height:180px;
                        border:1px solid #E0E0E0;
                        font-size:14px;
                        line-height:1.45;">
                        {text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # -----------------------------
        # 共识事实
        # -----------------------------
        st.markdown("### 📌 共识事实")
        if n.consensus_facts:
            for f in n.consensus_facts:
                st.markdown(f"- {f}")
        else:
            st.markdown("（无）")

        # -----------------------------
        # 争议点
        # -----------------------------
        st.markdown("### ⚠ 争议点")
        if n.contested_claims:
            for c in n.contested_claims:
                st.markdown(f"- {c}")
        else:
            st.markdown("（无）")

        # -----------------------------
        # 缺失视角
        # -----------------------------
        st.markdown("### ❓ 缺失视角")
        if n.missing_perspectives:
            for m in n.missing_perspectives:
                st.markdown(f"- {m}")
        else:
            st.markdown("（无）")

        st.markdown("---")
