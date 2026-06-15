# fzq_ai/ui/streamlit_app.py
from dotenv import load_dotenv

load_dotenv()

# ============================
# 修复 Python 路径（必须放最前）
# ============================
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================
# 依赖
# ============================
import streamlit as st
from dotenv import load_dotenv

from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.ui.components.news_card import render_news_card
from fzq_ai.ui.components.narrative_block import render_narrative_block
from fzq_ai.ui.components.risk_block import render_risk_block
from fzq_ai.ui.components.radar_chart import render_radar_chart
from fzq_ai.ui.components.sentiment_trend import render_sentiment_trend
from fzq_ai.ui.components.narrative_graph import render_narrative_graph
from fzq_ai.ui.components.timeline import render_timeline

# 加载 .env（确保 DEEPSEEK_API_KEY / NEWSAPI_KEY 生效）
load_dotenv()

# ============================
# 页面配置
# ============================
st.set_page_config(page_title="FZQ-AI 多源情报工作台", layout="wide")

st.title("FZQ-AI 多源情报工作台")
st.write("请输入你的情报查询主题（例如：全球要闻 / 科技新闻 / 宏观经济）")

query = st.text_input("查询主题")
run_btn = st.button("开始分析")

orchestrator = TaskOrchestrator()

# ============================
# 主逻辑（全同步，无 asyncio）
# ============================
if run_btn and query:
    # -----------------------------
    # 1. 新闻情报分析
    # -----------------------------
    st.subheader("新闻情报分析")

    news_result = orchestrator.run_agent(
        agent_name="news-intel",
        task="news",
        topic=query,
    )

    if not news_result["success"]:
        st.error(f"NewsPipeline 错误：{news_result['error']}")
        st.stop()

    bundle = news_result["data"]
    # bundle could be dict or IntelBundle
    if hasattr(bundle, "articles"):
        articles = bundle.articles
    elif isinstance(bundle, dict) and "intel_bundle" in bundle:
        articles = bundle["intel_bundle"].articles
    else:
        articles = getattr(bundle, "articles", [])

    st.write("### 新闻摘要")
    st.write(f"共抓取 {len(articles)} 条新闻")

    st.write("### 新闻列表")
    for a in articles:
        render_news_card(a)

    # -----------------------------
    # 2. 叙事分析
    # -----------------------------
    st.subheader("叙事分析")

    narrative_result = orchestrator.run_agent(
        agent_name="narrative",
        task="narrative",
        articles=articles,
    )

    if not narrative_result["success"]:
        st.error(f"NarrativePipeline 错误：{narrative_result['error']}")
    else:
        render_narrative_block(narrative_result["data"])

    # -----------------------------
    # 3. 风险分析
    # -----------------------------
    st.subheader("风险分析")

    risk_result = orchestrator.run_agent(
        agent_name="risk",
        task="risk",
        articles=articles,
    )

    if not risk_result["success"]:
        st.error(f"RiskPipeline error: {risk_result['error']}")
    else:
        render_risk_block(risk_result["data"])
        render_radar_chart(risk_result["data"])

    # -----------------------------
    # 4. 每日报告
    # -----------------------------
    st.subheader("每日报告")

    report_result = orchestrator.run_agent(
        agent_name="daily-report",
        task="daily-report",
        articles=articles,
    )

    if not report_result["success"]:
        st.error(f"DailyReportPipeline error: {report_result['error']}")
    else:
        st.markdown(report_result["data"])

    # -----------------------------
    # 5. Sentiment & Timeline (v2.6)
    # -----------------------------
    st.subheader("Sentiment Analysis")
    sentiment_result = orchestrator.run_agent(
        agent_name="sentiment",
        task="sentiment",
        articles=articles,
    )
    if not sentiment_result["success"]:
        st.warning(f"SentimentPipeline: {sentiment_result['error']}")
    else:
        render_sentiment_trend(sentiment_result["data"])

    st.subheader("Event Timeline")
    render_timeline(articles)

    st.subheader("Narrative Graph")
    render_narrative_graph(narrative_result.get("data", {}))
