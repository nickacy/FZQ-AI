# ---------------------------------------------------------
#  FZQ-AI UI APP (最新版) — 强制加载 .env + Key Debug 输出
# ---------------------------------------------------------

from dotenv import load_dotenv
load_dotenv(override=True)   # ★★★ 强制覆盖所有已有环境变量 ★★★

import os
import json
import streamlit as st

from fzq_ai.agent_hub import AgentHub
from fzq_ai.task_orchestrator import TaskOrchestrator
from fzq_ai.llm.key_manager import KeyManager


# ---------------------------------------------------------
#  加载配置
# ---------------------------------------------------------
def load_config() -> dict:
    config_path = "config.json"
    if not os.path.exists(config_path):
        raise RuntimeError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()
hub = AgentHub(config)
orchestrator = TaskOrchestrator(hub)
km = KeyManager()


# ---------------------------------------------------------
#  DEBUG：显示程序真正使用的 Key（前 10 位）
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 DEBUG：程序实际使用的 Key（前 10 位）")

def mask(v):
    if not v:
        return "(None)"
    return v[:10] + "..."

st.sidebar.write("DeepSeek =", mask(os.getenv("DEEPSEEK_API_KEY")))
st.sidebar.write("OpenAI   =", mask(os.getenv("OPENAI_API_KEY")))
st.sidebar.write("Gemini   =", mask(os.getenv("GEMINI_API_KEY")))


# ---------------------------------------------------------
#  UI 主界面
# ---------------------------------------------------------
st.set_page_config(page_title="FZQ-AI 智能分析系统", layout="wide")

st.title("📊 FZQ-AI 智能分析系统")
st.markdown(
    "支持：新闻摘要、叙事分析、风险扫描、每日简报生成，"
    "并具备多模型自动路由与 API Key 健康检测。"
)


# ---------------------------------------------------------
#  API Key 健康检查
# ---------------------------------------------------------
st.subheader("🔐 API Key 健康状态")

cols = st.columns(3)
models = ["deepseek", "openai", "gemini"]

for i, model in enumerate(models):
    ok, msg = km.health.get(model, (False, "未检测"))
    with cols[i]:
        st.markdown(
            f"**{model.capitalize()}**：{'🟢 正常' if ok else '🔴 异常'}  \n{msg}"
        )

st.markdown("---")


# ---------------------------------------------------------
#  任务选择
# ---------------------------------------------------------
st.subheader("🧠 任务选择")

task = st.selectbox(
    "选择任务类型：",
    [
        "每日简报（Daily Report）",
        "新闻摘要（News Summary）",
        "叙事分析（Narrative Analysis）",
        "风险扫描（Risk Scan）",
    ],
)


# ---------------------------------------------------------
#  输入新闻
# ---------------------------------------------------------
st.markdown("### 📰 输入新闻列表")
text_input = st.text_area(
    "每行一条新闻，可以是标题或简短描述：",
    height=200,
    placeholder="例如：\n澳洲房地产市场在 2026 年持续升温，悉尼房价同比上涨 8%。\n澳洲生活成本指数本季度上涨 2.1%，食品和能源价格是主要推动因素。",
)


# ---------------------------------------------------------
#  执行任务
# ---------------------------------------------------------
if st.button("🚀 运行任务"):
    if not text_input.strip():
        st.warning("请输入至少一条新闻。")
    else:
        items = [x.strip() for x in text_input.split("\n") if x.strip()]

        try:
            if task.startswith("每日简报"):
                result = orchestrator.run("daily_report", items)
                st.subheader("📅 每日简报")
                st.markdown(result["result"]["report"])

            elif task.startswith("新闻摘要"):
                result = orchestrator.run("news", items)
                st.subheader("📰 新闻摘要")
                st.markdown(result["result"])

            elif task.startswith("叙事分析"):
                result = orchestrator.run("narrative", items)
                st.subheader("📚 叙事分析（结构化结果）")
                st.markdown(result["result"])

            elif task.startswith("风险扫描"):
                result = orchestrator.run("risk", items)
                st.subheader("⚠️ 风险扫描（结构化结果）")
                st.markdown(result["result"])

        except Exception as e:
            st.error(f"❌ 运行失败：{e}")


st.markdown("---")
st.caption("FZQ-AI Agent · 多模型路由 · 自动 Key 检测 · 实验性版本")
