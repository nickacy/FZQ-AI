import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

API_URL = "http://localhost:8000/api/daily_report"

# -----------------------------
# 页面配置
# -----------------------------
st.set_page_config(
    page_title="FZQ‑AI Intelligence Dashboard",
    layout="wide",
)

st.title("🧠 FZQ‑AI 情报分析系统 v11 Dashboard")


# -----------------------------
# 输入区域（左侧）
# -----------------------------
with st.sidebar:
    st.header("📌 输入参数")

    topic = st.text_input("分析主题（topic）", "")

    news_raw = st.text_area(
        "新闻文本（每条一行）",
        height=300,
        placeholder="在这里粘贴新闻，每条一行…"
    )

    run_btn = st.button("🚀 生成情报日报")


# -----------------------------
# 调用 FastAPI 后端
# -----------------------------
if run_btn:
    if not topic or not news_raw.strip():
        st.error("请输入 topic 和至少一条新闻")
        st.stop()

    news_list = [line.strip() for line in news_raw.split("\n") if line.strip()]

    with st.spinner("正在生成情报日报…"):
        response = requests.post(
            API_URL,
            json={
                "topic": topic,
                "news_raw_texts": news_list
            }
        )

    if response.status_code != 200:
        st.error(f"后端错误：{response.text}")
        st.stop()

    data = response.json()

    # -----------------------------
    # 展示日报（Markdown）
    # -----------------------------
    st.subheader("📄 情报日报（Markdown）")
    st.markdown(data["final_markdown_report"])


    # -----------------------------
    # v11 Dashboard 图表区
    # -----------------------------
    st.subheader("📊 情报指标 Dashboard")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # -----------------------------
    # 1. 风险雷达图
    # -----------------------------
    with col1:
        st.markdown("### ⚠️ 风险雷达图")

        risk_scores = data["risk_scores"]  # dict: {"政治风险": 0.7, ...}

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(risk_scores.values()),
            theta=list(risk_scores.keys()),
            fill="toself",
            name="风险评分"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)


    # -----------------------------
    # 2. 情绪极化图
    # -----------------------------
    with col2:
        st.markdown("### 😠 情绪极化图")

        sentiment = data["sentiment_scores"]  # {"positive":0.3,"neutral":0.4,"negative":0.3}

        fig = go.Figure(data=[
            go.Bar(
                x=list(sentiment.keys()),
                y=list(sentiment.values()),
                marker_color=["green", "gray", "red"]
            )
        ])
        fig.update_layout(yaxis=dict(range=[0, 1]))
        st.plotly_chart(fig, use_container_width=True)


    # -----------------------------
    # 3. 区域覆盖度图
    # -----------------------------
    with col3:
        st.markdown("### 🌍 区域覆盖度图")

        region = data["region_coverage"]  # {"中国":3,"美国":1,"欧洲":2}

        fig = go.Figure(data=[
            go.Pie(
                labels=list(region.keys()),
                values=list(region.values()),
                hole=0.4
            )
        ])
        st.plotly_chart(fig, use_container_width=True)


    # -----------------------------
    # 4. Provider Fallback 监控
    # -----------------------------
    with col4:
        st.markdown("### 🔄 Provider Fallback 监控")

        fallback = data["provider_fallback"]  # {"deepseek":5,"kimi":2,"qwen":1}

        fig = go.Figure(data=[
            go.Bar(
                x=list(fallback.keys()),
                y=list(fallback.values()),
                marker_color="orange"
            )
        ])
        st.plotly_chart(fig, use_container_width=True)


    # -----------------------------
    # 5. 翻译失败率监控
    # -----------------------------
    st.markdown("### ❗ 翻译失败率监控")

    trans = data["translation_failures"]  # {"total":10,"failed":2}

    df = pd.DataFrame({
        "类型": ["成功", "失败"],
        "数量": [trans["total"] - trans["failed"], trans["failed"]]
    })

    fig = go.Figure(data=[
        go.Bar(
            x=df["类型"],
            y=df["数量"],
            marker_color=["green", "red"]
        )
    ])
    st.plotly_chart(fig, use_container_width=True)
