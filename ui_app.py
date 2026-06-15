# ui_app.py
# FZQ-AI Intelligence Dashboard (Streamlit UI) — v2.5
#
# 防御性 UI：所有 Pipeline 结果均通过 ServiceResult 安全解析，
# 成功时展示结构化内容，失败时展示友好错误提示。

import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from fzq_ai.domain.models import ServiceResult
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator

st.set_page_config(
    page_title="FZQ-AI Intelligence Dashboard", page_icon="satellite_antenna", layout="wide"
)

st.title("FZQ-AI Intelligence Dashboard")
st.caption("多模型情报分析系统 · 新闻 · 叙事 · 风险 · 日报")

# ── DEBUG Key 状态 ─────────────────────────────────────────────
if os.getenv("DEBUG", "").lower() == "true":
    st.sidebar.markdown("### DEBUG：Key 状态")

    def mask(v):
        return "已配置" if v else "未配置"

    st.sidebar.write("DeepSeek =", mask(os.getenv("DEEPSEEK_API_KEY")))
    st.sidebar.write("OpenAI   =", mask(os.getenv("OPENAI_API_KEY")))
    st.sidebar.write("Gemini   =", mask(os.getenv("GEMINI_API_KEY")))

# ── 辅助函数 ───────────────────────────────────────────────────


def _safe_unpack(result: ServiceResult):
    """防御性解析 ServiceResult -> (success, data, error_msg)."""
    if hasattr(result, "success"):
        return result.success, result.data, result.error
    if isinstance(result, dict):
        return result.get("success", False), result.get("data"), result.get("error")
    return False, None, str(result)


def _show_empty_topic(topic: str, sources: int = 0):
    st.info(f"未找到与 '{topic}' 匹配的结果（已检查 {sources} 个数据源）" if sources
            else f"未找到与 '{topic}' 匹配的结果")


# ── 侧边栏 ─────────────────────────────────────────────────────
st.sidebar.header("功能导航")

page = st.sidebar.radio(
    "选择功能",
    [
        "新闻情报分析",
        "叙事分析",
        "风险扫描",
        "每日报告生成",
    ],
)

# ── 页面逻辑 ───────────────────────────────────────────────────

if page == "新闻情报分析":
    st.subheader("新闻情报分析")
    query = st.text_input("输入新闻主题或关键词：", "")

    if st.button("开始分析"):
        if not query.strip():
            st.warning("请输入新闻主题或关键词")
        else:
            with st.spinner("正在分析新闻情报..."):
                pipeline = NewsPipeline()
                result = pipeline.run(query)

            success, data, error = _safe_unpack(result)
            if success and data:
                bundle = data.get("intel_bundle", data) if isinstance(data, dict) else data
                articles = getattr(bundle, "articles", [])
                if articles:
                    st.success(f"分析完成，匹配 {len(articles)} 条新闻")
                    for a in articles:
                        title = getattr(a, "title_original", "") or getattr(a, "title", "无标题")
                        source = getattr(a, "source_name", "未知来源")
                        url = getattr(a, "url", "")
                        summary = getattr(a, "content_original", "") or getattr(a, "summary", "")
                        with st.expander(f"{title[:100]}"):
                            st.write(f"**来源:** {source}")
                            if summary:
                                st.write(summary[:500])
                            if url:
                                st.markdown(f"[阅读原文]({url})")
                else:
                    _show_empty_topic(query)
            else:
                st.error(f"分析失败: {error or '未知错误'}")

elif page == "叙事分析":
    st.subheader("叙事分析")
    text = st.text_area("输入需要分析的文本或主题：", "")

    if st.button("开始分析"):
        if not text.strip():
            st.warning("请输入分析文本")
        else:
            with st.spinner("正在分析叙事结构..."):
                pipeline = NarrativePipeline()
                result = pipeline.run(text)

            success, data, error = _safe_unpack(result)
            if success and data:
                if isinstance(data, dict):
                    st.success("叙事分析完成")
                    summary = data.get("global_summary", "")
                    clusters = data.get("clusters", [])
                    tension = data.get("tension_matrix", [])

                    if summary:
                        st.markdown("### 全局摘要")
                        st.write(summary)

                    if clusters:
                        st.markdown("### 叙事聚类")
                        for c in clusters:
                            name = c.get("cluster_name", "未命名")
                            items = c.get("items", [])
                            st.markdown(f"- **{name}** ({len(items)} 条)")
                            for item in items[:5]:
                                st.markdown(f"  - {item}")

                    if tension:
                        st.markdown("### 张力矩阵")
                        for t in tension:
                            a1 = t.get("actor1", "?")
                            a2 = t.get("actor2", "?")
                            desc = t.get("description", "")
                            st.markdown(f"- **{a1} ↔ {a2}**: {desc}")
                else:
                    st.text(str(data))
            else:
                st.error(f"叙事分析失败: {error or '未知错误'}")

elif page == "风险扫描":
    st.subheader("风险扫描")
    topic = st.text_input("输入风险主题：", "")

    if st.button("开始扫描"):
        if not topic.strip():
            st.warning("请输入风险主题")
        else:
            with st.spinner("正在执行风险扫描..."):
                pipeline = RiskPipeline()
                result = pipeline.run(topic)

            success, data, error = _safe_unpack(result)
            if success and data:
                st.success("风险扫描完成")
                st.write(data)
            else:
                st.error(f"风险扫描失败: {error or '未知错误'}")

elif page == "每日报告生成":
    st.subheader("每日报告生成")

    if st.button("生成今日情报报告"):
        with st.spinner("正在生成每日报告..."):
            pipeline = DailyReportPipeline()
            result = pipeline.run()

        success, data, error = _safe_unpack(result)
        if success and data:
            st.success("报告生成完成")
            if isinstance(data, str):
                st.markdown(data)
            else:
                st.write(data)
        else:
            st.error(f"报告生成失败: {error or '未知错误'}")
