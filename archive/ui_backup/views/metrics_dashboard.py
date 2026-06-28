"""
Metrics Dashboard (Streamlit)
系统指标仪表盘（中英文双语）
----------------------------------------------------
Displays:
- System metrics
- Provider metrics
- Pipeline metrics

展示：
- 系统级指标
- Provider 级指标
- Pipeline 级指标
"""

import streamlit as st
import requests
import time


# -------------------------------
# 后端 API 地址
# -------------------------------
API_BASE = "http://localhost:8000/api"


# -------------------------------
# DeepSeek 风格 Provider Gauge
# -------------------------------
def provider_gauge(provider_name, stats):
    """
    Render a DeepSeek-style provider gauge.
    渲染 DeepSeek 风格的 Provider 仪表盘。
    """
    st.subheader(f"🔌 Provider: {provider_name}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Calls / 总调用次数",
            value=stats["total_calls"]
        )

    with col2:
        st.metric(
            label="Success Rate / 成功率",
            value=f"{stats['success_rate'] * 100:.1f}%"
        )

    with col3:
        st.metric(
            label="Avg Latency / 平均延迟 (ms)",
            value=f"{stats['avg_latency_ms']:.1f}"
        )

    st.caption(f"Last Used / 最近调用: {stats['last_used_at']}")


# -------------------------------
# Pipeline 状态卡片
# -------------------------------
def pipeline_card(name, stats):
    st.markdown(f"### 📌 Pipeline: **{name}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Call Count / 调用次数", stats["call_count"])

    with col2:
        st.metric("Avg Latency / 平均延迟 (ms)", f"{stats['avg_latency_ms']:.1f}")

    with col3:
        st.metric("Error Rate / 错误率", f"{stats['error_rate'] * 100:.1f}%")

    st.caption(f"Last Called / 最近调用: {stats['last_called_at']}")


# -------------------------------
# 主渲染函数
# -------------------------------
def render_metrics_page():
    st.title("📊 System Metrics Dashboard / 系统指标仪表盘")

    # 自动刷新
    st.caption("Auto-refresh every 3 seconds / 每 3 秒自动刷新")
    time.sleep(0.1)

    # -------------------------------
    # 获取系统指标
    # -------------------------------
    try:
        system_metrics = requests.get(f"{API_BASE}/metrics").json()
    except Exception:
        st.error("❌ Unable to connect to backend API / 无法连接后端 API")
        return

    # -------------------------------
    # 系统级指标
    # -------------------------------
    st.header("🖥️ System Metrics / 系统级指标")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Uptime / 运行时间 (s)", f"{system_metrics['uptime_seconds']:.0f}")

    with col2:
        st.metric("Total Requests / 总请求数", system_metrics["total_requests"])

    with col3:
        st.metric("Total Errors / 总错误数", system_metrics["total_errors"])

    with col4:
        st.metric("Avg Latency / 平均延迟 (ms)", f"{system_metrics['avg_latency_ms']:.1f}")

    st.divider()

    # -------------------------------
    # Provider 指标
    # -------------------------------
    st.header("🔌 Provider Metrics / 模型提供商指标")

    provider_stats = system_metrics["provider_stats"]

    if not provider_stats:
        st.info("No provider metrics yet. / 暂无 Provider 指标。")
    else:
        for provider_name, stats in provider_stats.items():
            provider_gauge(provider_name, stats)
            st.divider()

    # -------------------------------
    # Pipeline 指标
    # -------------------------------
    st.header("📦 Pipeline Metrics / Pipeline 指标")

    pipeline_stats = system_metrics["pipeline_stats"]

    if not pipeline_stats:
        st.info("No pipeline metrics yet. / 暂无 Pipeline 指标。")
    else:
        for name, stats in pipeline_stats.items():
            pipeline_card(name, stats)
            st.divider()
