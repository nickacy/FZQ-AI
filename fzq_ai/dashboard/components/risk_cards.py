import streamlit as st

# 风险等级颜色
RISK_COLORS = {
    "高": "#D32F2F",  # 红
    "中": "#F57C00",  # 橙
    "低": "#FBC02D",  # 黄
    "极低": "#388E3C",  # 绿
}

def render_risk_card(risk: dict, index: int):
    """渲染单个风险卡片（左侧彩色条 + 折叠面板）"""

    color = RISK_COLORS.get(severity, "#F57C00")  # 默认橙色

    with st.container():
        # 左侧彩色条 + 标题
            <div style="display:flex; border:1px solid #444; border-radius:6px; overflow:hidden; margin-bottom:10px;">
            """,

        # 折叠面板
        with st.expander("📌 风险详情"):
            st.markdown("### 🔥 触发因素")
            if triggers:
                for t in triggers:
            else:

            st.markdown("### 🎯 影响范围")
            st.write(impact)

            st.markdown("### 🛠 建议措施")
            if suggestions:
                for s in suggestions:
            else:

            st.markdown("### 🔗 后续操作（未来 Intelligence Hub 会启用）")
            st.button("➡️ 送去叙事分析", key=f"narrative_{index}")
            st.button("➡️ 送去地缘政治分析", key=f"geo_{index}")
            st.button("➡️ 加入每日简报", key=f"daily_{index}")
