# app.py

import streamlit as st

from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.dashboard.dashboard import render_dashboard


st.set_page_config(page_title="FZQ-AI Intelligence Dashboard", layout="wide")

st.title("🌐 FZQ-AI Intelligence System")

query = st.text_input("输入你的查询（例如：全球要闻、台海局势、乌克兰局势）", "全球要闻")

if st.button("运行情报分析"):
    with st.spinner("正在收集与分析全球新闻…"):
        pipeline = NewsPipeline()
        result = st.session_state["intel"] = pipeline.run_sync(query)

if "intel" in st.session_state:
    render_dashboard(st.session_state["intel"]["intel_bundle"])
