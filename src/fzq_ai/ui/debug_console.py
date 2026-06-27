"""
FZQ-AI Web UI (Debug Console)
FZQ-AI 调试控制台（中英文双语）
----------------------------------------------------
Entry point for testing pipelines via Streamlit.
通过 Streamlit 测试各 Pipeline 的调试入口。
"""

import streamlit as st
import asyncio
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.schemas.pipeline_input import PipelineInput


st.set_page_config(
    page_title="FZQ-AI Web UI / 调试控制台",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 FZQ-AI Web UI / 调试控制台")
st.write(
    "Enter any question. FZQ-AI processes it through Router → Pipeline → Self-Healing → Recovery.\n\n"
    "输入任何问题，FZQ-AI 将通过 Router → Pipeline → 自愈 → 恢复 链路输出完整回答。"
)

question = st.text_area(
    "Question / 问题：",
    height=150,
    placeholder="e.g. Who might win the 2026 World Cup? / 例如：2026年世界杯冠军可能是谁？"
)

task_type = st.selectbox(
    "Pipeline type / Pipeline 类型：",
    ["daily_report", "narrative", "risk", "merge",
     "zh_multisource_merge", "zh_opinion_landscape", "zh_policy_brief", "zh_risk_scan"]
)

target_language = st.selectbox(
    "Output language / 输出语言：",
    ["zh", "en"]
)

run_button = st.button("🚀 Run FZQ-AI / 运行")


if run_button and question.strip():
    orchestrator = TaskOrchestrator()

    req = PipelineInput(
        query=question,
        target_language=target_language,
        task_type=task_type,
    )

    with st.spinner("Processing... / 处理中..."):
        try:
            result = asyncio.run(orchestrator.run(req.model_dump()))
        except Exception as e:
            st.error(f"Error / 错误: {e}")
            st.stop()

    st.subheader("📝 Output / 输出")
    output = result.get("output", str(result))
    if isinstance(output, str):
        st.write(output)
    else:
        st.json(output)

    if "model_used" in result:
        st.subheader("🤖 Model Used / 使用模型")
        st.json(result["model_used"])

    if "metadata" in result:
        st.subheader("📦 Metadata / 元数据")
        st.json(result["metadata"])

    if "recovery_trace" in result:
        st.subheader("🛠 Recovery Trace / 恢复链路")
        st.json(result["recovery_trace"])

    if "repair_log" in result:
        st.subheader("🔧 Self-Healing Log / 自愈日志")
        st.json(result["repair_log"])
