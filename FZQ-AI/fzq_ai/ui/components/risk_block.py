# fzq_ai/ui/components/risk_block.py

import streamlit as st


def render_risk_block():
    """
    当前为占位版本，后续接入 RiskPipeline 的真实风险评分。
    """
    st.markdown("## ⚠️ 风险提示（占位）")
    st.info("风险分析将在下一阶段接入 RiskPipeline 的真实数据。")
