# main.py
# FZQ-AI Intelligence Dashboard (Streamlit)

import streamlit as st
import sys
import os

# 确保项目根目录加入 sys.path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.dashboard.dashboard import render_dashboard

# Streamlit 页面配置
st.set_page_config(
    page_title="FZQ-AI Intelligence Dashboard",
    layout="wide",
)

st.title("🌐 FZQ-AI Intelligence System")
st.markdown("全球新闻 → 去噪 → 翻译 → 聚类 → 可信度 → 偏见 → 事件视图 → 情报输出")

# 用户输入
query = st.text_input(
    "输入你的查询（例如：全球要闻、台海局势、乌克兰局势）",
    "全球要闻"
)

# 运行情报分析
if st.button("运行情报分析"):
    with st.spinner("正在收集与分析全球新闻…"):
        pipeline = NewsPipeline()
        result = pipeline.run_sync(query)
        st.session_state["intel"] = result

# 渲染 Dashboard
if "intel" in st.session_state and st.session_state["intel"]:
    intel = st.session_state["intel"]
    bundle = intel.get("intel_bundle")
    if bundle:
        render_dashboard(bundle)
    elif "error" in intel:
        st.error(intel["error"])
