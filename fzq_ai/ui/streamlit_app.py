# fzq_ai/ui/streamlit_app.py — v2.6 Professional UI
from dotenv import load_dotenv
load_dotenv()

import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from dotenv import load_dotenv

from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.ui.theme import inject_theme, section_header, metric_row, status_strip, COLORS
from fzq_ai.ui.components.news_card import render_news_card
from fzq_ai.ui.components.narrative_block import render_narrative_block
from fzq_ai.ui.components.risk_block import render_risk_block
from fzq_ai.ui.components.radar_chart import render_radar_chart
from fzq_ai.ui.components.sentiment_trend import render_sentiment_trend
from fzq_ai.ui.components.narrative_graph import render_narrative_graph
from fzq_ai.ui.components.timeline import render_timeline

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# Page Config & Theme
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FZQ-AI · Intelligence Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

# ═══════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:12px 0;">'
        '<h2 style="color:#fff;margin:0;">🔍 FZQ-AI</h2>'
        '<p style="color:rgba(255,255,255,0.6);font-size:13px;">'
        'Multi-Source Intelligence Platform v2.6</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown(
        '<p style="color:rgba(255,255,255,0.8);font-size:14px;font-weight:500;">'
        '📋 Analysis Mode</p>',
        unsafe_allow_html=True,
    )
    analysis_mode = st.selectbox(
        "Mode",
        ["Full Analysis (All Pipelines)", "News Only", "Risk + Sentiment", "Narrative Deep-Dive"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<p style="color:rgba(255,255,255,0.8);font-size:14px;font-weight:500;'
        'margin-top:12px;">🎯 Query Topic</p>',
        unsafe_allow_html=True,
    )
    query = st.text_input(
        "Topic",
        placeholder="e.g. US election sentiment risk...",
        label_visibility="collapsed",
    )
    run_btn = st.button("▶ Run Analysis", use_container_width=True)

    st.markdown("---")
    st.markdown(
        '<p style="color:rgba(255,255,255,0.5);font-size:12px;">'
        'Sources: 17 RSS · GDELT · NewsAPI<br>'
        'LLM: DeepSeek → OpenAI → Gemini</p>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# Main Area — Header
# ═══════════════════════════════════════════════════════════════
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown(
        f'<h1 style="color:{COLORS["primary"]};margin-bottom:4px;">'
        f'FZQ-AI Intelligence Dashboard</h1>'
        f'<p style="color:{COLORS["text_secondary"]};font-size:15px;">'
        f'Cross-region · Multi-source · AI-powered analysis</p>',
        unsafe_allow_html=True,
    )
with col_status:
    st.markdown(
        f'<div style="background:{COLORS["bg_light"]};border-radius:10px;'
        f'padding:12px;text-align:center;margin-top:10px;">'
        f'<div style="font-size:24px;font-weight:700;color:{COLORS["success"]};">●</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};">System Ready</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

orchestrator = TaskOrchestrator()

# ═══════════════════════════════════════════════════════════════
# Idle State
# ═══════════════════════════════════════════════════════════════
if not run_btn or not query:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            f'<div class="fzq-card"><div style="font-size:28px;">📰</div>'
            f'<h4>Multi-Source News</h4>'
            f'<p style="color:{COLORS["text_secondary"]};">17 RSS feeds across 8 regions</p></div>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f'<div class="fzq-card"><div style="font-size:28px;">🧠</div>'
            f'<h4>AI-Powered Analysis</h4>'
            f'<p style="color:{COLORS["text_secondary"]};">DeepSeek / OpenAI / Gemini</p></div>',
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            f'<div class="fzq-card"><div style="font-size:28px;">🌍</div>'
            f'<h4>Global Balance</h4>'
            f'<p style="color:{COLORS["text_secondary"]};">Cross-region, 30%+ Global South</p></div>',
            unsafe_allow_html=True,
        )
    st.stop()

# ═══════════════════════════════════════════════════════════════
# Execute: News Pipeline
# ═══════════════════════════════════════════════════════════════
section_header("📰 News Intelligence", "")
news_result = orchestrator.run_agent(agent_name="news-intel", task="news", topic=query)

if not news_result["success"]:
    st.error(f"NewsPipeline: {news_result['error']}")
    st.stop()

bundle = news_result["data"]
articles = []
if hasattr(bundle, "articles"):
    articles = bundle.articles
elif isinstance(bundle, dict) and "intel_bundle" in bundle:
    articles = bundle["intel_bundle"].articles
else:
    articles = getattr(bundle, "articles", [])

# ── News metrics ──
regions = list(set(a.region for a in articles if a.region))
metric_row({
    "Articles Found": len(articles),
    "Regions": len(regions),
    "Sources": len(set(a.source_name for a in articles)),
    "Avg Credibility": f"{sum(a.credibility for a in articles)/max(len(articles),1):.1f}",
})

if len(articles) == 0:
    status_strip(f"No articles matched '{query}'. Try a broader keyword.", "warning")
    st.stop()

# ── News cards in grid ──
cols = st.columns(2)
for i, a in enumerate(articles[:20]):
    with cols[i % 2]:
        render_news_card(a)

# ═══════════════════════════════════════════════════════════════
# Analysis Pipelines (conditional on mode)
# ═══════════════════════════════════════════════════════════════
run_all = analysis_mode == "Full Analysis (All Pipelines)"
run_risk = run_all or "Risk" in analysis_mode
run_narrative = run_all or "Narrative" in analysis_mode

if run_narrative:
    st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
    section_header("🧭 Narrative Analysis", "")
    narrative_result = orchestrator.run_agent(agent_name="narrative", task="narrative", articles=articles)
    if narrative_result["success"]:
        tab1, tab2 = st.tabs(["📊 Narrative Blocks", "🕸️ Graph View"])
        with tab1:
            render_narrative_block(narrative_result["data"])
        with tab2:
            render_narrative_graph(narrative_result.get("data", {}))
    else:
        status_strip(f"Narrative: {narrative_result['error']}", "warning")

if run_risk:
    st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
    section_header("⚠️ Risk Analysis", "")
    risk_result = orchestrator.run_agent(agent_name="risk", task="risk", articles=articles)
    if risk_result["success"]:
        col_risk, col_radar = st.columns([1, 1])
        with col_risk:
            render_risk_block(risk_result["data"])
        with col_radar:
            render_radar_chart(risk_result["data"])
    else:
        status_strip(f"Risk: {risk_result['error']}", "warning")

st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
section_header("📊 Sentiment & Timeline", "")

sentiment_result = orchestrator.run_agent(agent_name="sentiment", task="sentiment", articles=articles)
if sentiment_result["success"]:
    render_sentiment_trend(sentiment_result["data"])

st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
section_header("📅 Event Timeline", "")
render_timeline(articles)

# ═══════════════════════════════════════════════════════════════
# Daily Report
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
section_header("📋 Daily Intelligence Report", "")
report_result = orchestrator.run_agent(agent_name="daily-report", task="daily-report", articles=articles)
if report_result["success"]:
    st.markdown(report_result["data"])
