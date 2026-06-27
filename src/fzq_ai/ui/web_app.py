import streamlit as st
import asyncio
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.schemas.pipeline_input import PipelineInput


st.set_page_config(
    page_title="FZQ-AI Web UI",
    page_icon="\U0001f916",
    layout="centered"
)

st.title("\U0001f916 FZQ-AI Web UI")
st.write("Enter any question. FZQ-AI will process it through Router + Pipeline + Self-Healing + Recovery.")

question = st.text_area(
    "Question:",
    height=150,
    placeholder="e.g. Who might win the 2026 World Cup?"
)

task_type = st.selectbox(
    "Pipeline type:",
    ["daily_report", "narrative", "risk", "merge"]
)

target_language = st.selectbox(
    "Output language:",
    ["zh", "en"]
)

run_button = st.button("\U0001f680 Run FZQ-AI")


if run_button and question.strip():
    orchestrator = TaskOrchestrator()

    # PipelineInput is a Pydantic model; convert to dict for orchestrator
    req = PipelineInput(
        query=question,
        target_language=target_language,
        task_type=task_type,
    )

    with st.spinner("Processing..."):
        result = asyncio.run(orchestrator.run(req.model_dump()))

    st.subheader("Output")
    output = result.get("output", str(result))
    if isinstance(output, str):
        st.write(output)
    else:
        st.json(output)

    if "model_used" in result:
        st.subheader("Model Used")
        st.json(result["model_used"])

    if "metadata" in result:
        st.subheader("Metadata")
        st.json(result["metadata"])

    if "recovery_trace" in result:
        st.subheader("Recovery Trace")
        st.json(result["recovery_trace"])

    if "repair_log" in result:
        st.subheader("Self-Healing Log")
        st.json(result["repair_log"])
