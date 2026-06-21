"""
Chinese Intelligence Center
中文情报中心（中英文双语）
----------------------------------------------------
This GUI page allows users to run the four zh-intel tasks.
该页面允许用户运行四大中文情报任务。
"""

import streamlit as st
import requests
import json


API_BASE = "http://localhost:8000/api/zh"


def render_zh_intel_page():
    st.title("🌏 Chinese Intelligence Center / 中文情报中心")

    st.markdown("""
    **Run Chinese intelligence tasks with one click.**  
    **一键运行四大中文情报任务。**
    """)

    task = st.selectbox(
        "Select Task / 选择任务",
        [
            "zh_policy_brief",
            "zh_risk_scan",
            "zh_opinion_landscape",
            "zh_multisource_merge",
        ]
    )

    st.divider()

    # -----------------------------
    # Input area
    # -----------------------------
    st.subheader("Input / 输入")

    payload_text = st.text_area(
        "Paste JSON payload here / 在此粘贴 JSON 输入",
        height=300
    )

    if st.button("Run / 运行"):
        try:
            payload = json.loads(payload_text)
        except Exception:
            st.error("❌ Invalid JSON / JSON 格式错误")
            return

        with st.spinner("Running… / 正在运行…"):
            resp = requests.post(f"{API_BASE}/{task.replace('zh_', '')}", json=payload)

        if resp.status_code != 200:
            st.error(f"❌ API Error: {resp.text}")
            return

        result = resp.json()

        st.success("✔ Completed / 完成")

        # -----------------------------
        # Output area
        # -----------------------------
        st.subheader("Output (JSON) / 输出（JSON）")
        st.json(result)

        if "summary" in result:
            st.subheader("Summary / 摘要")
            st.markdown(result["summary"])
