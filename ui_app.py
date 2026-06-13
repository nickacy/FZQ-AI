# ui_app.py
# FZQ-AI Intelligence Dashboard (Streamlit UI)

import os
import sys
from dotenv import load_dotenv

# ============================
#  加载环境变量（强制覆盖）
# ============================
load_dotenv(override=True)

import streamlit as st

# 将项目根目录加入 sys.path（确保 fzq_ai 可被 import）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================
#  导入 FZQ-AI 核心模块
# ============================
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator


# ============================
#  Streamlit 页面配置
# ============================
st.set_page_config(
    page_title="FZQ-AI Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ FZQ-AI Intelligence Dashboard")
st.caption("多模型情报分析系统 · 新闻 · 叙事 · 风险 · 日报")


# ============================
#  DEBUG Key 状态（安全版本）
# ============================
if os.getenv("DEBUG", "").lower() == "true":
    st.sidebar.markdown("### 🔍 DEBUG：Key 状态")

    def mask(v: str | None) -> str:
        return "✅ 已配置" if v else "❌ 未配置"

    st.sidebar.write("DeepSeek =", mask(os.getenv("DEEPSEEK_API_KEY")))
    st.sidebar.write("OpenAI   =", mask(os.getenv("OPENAI_API_KEY")))
    st.sidebar.write("Gemini   =", mask(os.getenv("GEMINI_API_KEY")))


# ============================
#  侧边栏导航
# ============================
st.sidebar.header("📡 功能导航")

page = st.sidebar.radio(
    "选择功能",
    [
        "📰 新闻情报分析",
        "🧠 叙事分析",
        "⚠️ 风险扫描",
        "📅 每日报告生成",
        "🧩 任务编排（Orchestrator）"
    ]
)


# ============================
#  页面逻辑
# ============================

# --- 新闻情报分析 ---
if page == "📰 新闻情报分析":
    st.subheader("📰 新闻情报分析")
    query = st.text_input("输入新闻主题或关键词：", "")
    if st.button("开始分析"):
        with st.spinner("正在分析新闻情报..."):
            pipeline = NewsPipeline()
            result = pipeline.run(query)
        st.success("分析完成")
        st.write(result)


# --- 叙事分析 ---
elif page == "🧠 叙事分析":
    st.subheader("🧠 叙事分析")
    text = st.text_area("输入需要分析的叙事文本：", "")
    if st.button("开始分析"):
        with st.spinner("正在分析叙事结构..."):
            pipeline = NarrativePipeline()
            result = pipeline.run(text)
        st.success("分析完成")
        st.write(result)


# --- 风险扫描 ---
elif page == "⚠️ 风险扫描":
    st.subheader("⚠️ 风险扫描")
    topic = st.text_input("输入风险主题：", "")
    if st.button("开始扫描"):
        with st.spinner("正在执行风险扫描..."):
            pipeline = RiskPipeline()
            result = pipeline.run(topic)
        st.success("扫描完成")
        st.write(result)


# --- 每日报告 ---
elif page == "📅 每日报告生成":
    st.subheader("📅 每日报告生成")
    if st.button("生成今日情报报告"):
        with st.spinner("正在生成每日报告..."):
            pipeline = DailyReportPipeline()
            result = pipeline.run()
        st.success("报告生成完成")
        st.write(result)


# --- Orchestrator ---
elif page == "🧩 任务编排（Orchestrator）":
    st.subheader("🧩 任务编排中心")
    task = st.text_input("输入任务指令：", "")
    if st.button("执行任务"):
        with st.spinner("正在执行任务编排..."):
            orchestrator = TaskOrchestrator()
            result = orchestrator.run(task)
        st.success("任务执行完成")
        st.write(result)
