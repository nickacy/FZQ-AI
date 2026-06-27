"""
⚠️  DEPRECATED — 此文件已被 web_app.py (V15-Final) 取代。
    保留原因：向后兼容。
    请使用：python -m streamlit run src/fzq_ai/ui/web_app.py
    
FZQ-AI Frontend Entry (Streamlit V10 — DEPRECATED)
FZQ-AI 前端入口（Streamlit V10 — 已废弃）
"""

import warnings
warnings.warn(
    "ui_app.py (V10) is deprecated. Use web_app.py (V15-Final) instead.",
    DeprecationWarning,
    stacklevel=2,
)

from fzq_ai.ui.views.metrics_dashboard import render_metrics_page

import streamlit as st

# -------------------------------
# Import UI pages
# 导入各 UI 页面
# -------------------------------
from fzq_ai.ui.views.zh_intel import render_zh_intel_page
# Metrics 页面稍后添加
# from fzq_ai.ui.views.metrics_dashboard import render_metrics_page


# -------------------------------
# Streamlit 页面配置
# -------------------------------
st.set_page_config(
    page_title="FZQ-AI Intelligence System",
    page_icon="🌐",
    layout="wide",
)


# -------------------------------
# Sidebar Navigation / 侧边栏导航
# -------------------------------
page = st.sidebar.selectbox(
    "Select Page / 选择页面",
    [
        "Home / 首页",
        "Chinese Intelligence / 中文情报中心",
        "System Metrics / 系统指标（v8.6）",
    ]
)


# -------------------------------
# Page Routing / 页面路由
# -------------------------------
if page == "Home / 首页":
    st.title("🏠 FZQ-AI Intelligence Dashboard / 情报系统首页")
    st.markdown("""
    Welcome to FZQ-AI.  
    欢迎使用 FZQ-AI。

    Use the sidebar to navigate between modules.  
    使用侧边栏切换不同模块。
    """)

elif page == "Chinese Intelligence / 中文情报中心":
    render_zh_intel_page()

elif page == "System Metrics / 系统指标（v8.6）":
    st.title("📊 System Metrics Dashboard / 系统指标仪表盘")
    st.info("Metrics Dashboard will be added in Step 6. / 指标仪表盘将在第 6 步加入。")
    render_metrics_page()
