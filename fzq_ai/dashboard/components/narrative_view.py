# fzq_ai/dashboard/components/narrative_view.py

import streamlit as st
from fzq_ai.intel.models import IntelBundle


def render_narrative_view(bundle: IntelBundle):
    st.title("🧭 多阵营叙事视图 Narrative View")

    for narrative in bundle.narratives:
        st.markdown(f"## 🧩 事件 {narrative.event_id}")

        st.markdown("### 🌍 多阵营叙事")
        for bloc, text in narrative.narratives.items():
            st.markdown(f"#### 🏳 {bloc.capitalize()}")
            st.write(text)

        st.markdown("### 📌 共识事实")
        for f in narrative.consensus_facts:
            st.markdown(f"- {f}")

        st.markdown("### ⚠ 争议点")
        for c in narrative.contested_claims:
            st.markdown(f"- {c}")

        st.markdown("### ❓ 缺失视角")
        for m in narrative.missing_perspectives:
            st.markdown(f"- {m}")

        st.markdown("---")
