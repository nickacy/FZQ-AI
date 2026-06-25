import streamlit as st
from fzq_ai.llm.orchestrator.orchestrator import TaskOrchestrator
from fzq_ai.schemas.pipeline_input import PipelineInput


st.set_page_config(
    page_title="FZQ-AI Web UI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 FZQ-AI Web UI（调试控制台）")
st.write("输入任何问题，FZQ-AI 将通过 Router → Pipeline → 自愈 → 恢复 → 输出完整回答。")


# 输入框
question = st.text_area(
    "请输入你的问题：",
    height=150,
    placeholder="例如：2026年世界杯冠军可能是谁？中国哪一年可能举办世界杯？"
)

task_type = st.selectbox(
    "选择 Pipeline 类型：",
    ["daily_report", "narrative", "risk", "merge"]
)

target_language = st.selectbox(
    "输出语言：",
    ["zh", "en"]
)

run_button = st.button("🚀 运行 FZQ-AI")


if run_button and question.strip():
    orchestrator = TaskOrchestrator()

    req = PipelineInput(
        query=question,
        target_language=target_language,
        task_type=task_type,
    )

    with st.spinner("FZQ-AI 正在思考中…"):
        result = orchestrator.run(req)

    st.subheader("📝 最终输出")
    st.write(result.output)

    if hasattr(result, "model_used"):
        st.subheader("🤖 使用的模型")
        st.json(result.model_used)

    if hasattr(result, "metadata"):
        st.subheader("📦 元数据")
        st.json(result.metadata)

    if hasattr(result, "recovery_trace"):
        st.subheader("🛠 恢复链路")
        st.json(result.recovery_trace)

    if hasattr(result, "repair_log"):
        st.subheader("🔧 自愈日志")
        st.json(result.repair_log)
