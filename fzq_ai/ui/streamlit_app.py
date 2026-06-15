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

# ── Inject extra sidebar & nav styling ──
st.markdown(f"""
<style>
/* ── Sidebar badge glow ── */
.fzq-key-dot {{
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 6px var(--dot-color);
}}
.fzq-key-row {{
    display: flex;
    align-items: center;
    padding: 3px 0;
    font-size: 12px;
    color: rgba(255,255,255,0.75);
}}
.fzq-key-row .label {{ width: 70px; }}
.fzq-key-row .status {{ font-weight: 500; }}

/* ── Nav pills ── */
.fzq-nav-pill {{
    display: block;
    padding: 10px 16px;
    margin: 4px 0;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    color: rgba(255,255,255,0.8) !important;
    text-decoration: none !important;
    cursor: pointer;
    transition: all 0.15s;
    border: 1px solid transparent;
}}
.fzq-nav-pill:hover {{
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15);
}}
.fzq-nav-pill.active {{
    background: rgba(255,255,255,0.12) !important;
    border-color: {COLORS["accent"]} !important;
    color: #fff !important;
    box-shadow: 0 0 8px rgba(232,93,44,0.2);
}}
.fzq-nav-pill .icon {{ font-size: 16px; margin-right: 8px; }}

/* ── Compact divider ── */
.fzq-sidebar-div {{
    height: 1px;
    background: rgba(255,255,255,0.1);
    margin: 14px 0;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# Sidebar — Key Status + Function Navigation
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Brand Logo ──
    st.markdown(
        '<div style="text-align:center;padding:16px 4px 8px 4px;">'
        '<svg width="220" height="72" viewBox="0 0 220 72" xmlns="http://www.w3.org/2000/svg">'
        '<defs>'
        '<linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#4FC3F7"/>'
        f'<stop offset="100%" stop-color="#E85D2C"/>'
        '</linearGradient>'
        '<linearGradient id="logoBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#fff" stop-opacity="0.12"/>'
        '<stop offset="100%" stop-color="#fff" stop-opacity="0.04"/>'
        '</linearGradient>'
        '</defs>'
        '<circle cx="36" cy="36" r="28" fill="url(#logoBg)" stroke="url(#logoGrad)" stroke-width="1.2" opacity="0.9"/>'
        '<polygon points="36,15 52,23 52,49 36,57 20,49 20,23" fill="none" stroke="url(#logoGrad)" stroke-width="0.8" opacity="0.3"/>'
        '<circle cx="36" cy="15" r="2.5" fill="#4FC3F7" opacity="0.8"/>'
        '<circle cx="52" cy="36" r="2.5" fill="#E85D2C" opacity="0.8"/>'
        '<circle cx="20" cy="36" r="2.5" fill="#E85D2C" opacity="0.8"/>'
        '<polygon points="36,22 42,36 36,50 30,36" fill="url(#logoGrad)" opacity="0.6"/>'
        '<polygon points="36,26 40,36 36,46 32,36" fill="#fff" opacity="0.85"/>'
        '<rect x="54" y="44" width="2" height="4" rx="1" fill="#E85D2C" opacity="0.5"/>'
        '<rect x="57" y="40" width="2" height="8" rx="1" fill="#E85D2C" opacity="0.7"/>'
        '<rect x="60" y="36" width="2" height="12" rx="1" fill="#E85D2C" opacity="0.8"/>'
        '<rect x="63" y="32" width="2" height="16" rx="1" fill="#E85D2C" opacity="0.9"/>'
        '<text x="78" y="34" font-family="Inter,system-ui,sans-serif" font-size="26" font-weight="700" fill="#fff" letter-spacing="3">FZQ</text>'
        f'<text x="144" y="34" font-family="Inter,system-ui,sans-serif" font-size="26" font-weight="700" fill="#E85D2C">AI</text>'
        '<text x="80" y="52" font-family="Inter,system-ui,sans-serif" font-size="9.5" fill="rgba(255,255,255,0.3)" letter-spacing="3">INTELLIGENCE PLATFORM</text>'
        '<line x1="6" y1="6" x2="14" y2="6" stroke="#E85D2C" stroke-width="0.5" opacity="0.3"/>'
        '<line x1="6" y1="6" x2="6" y2="14" stroke="#E85D2C" stroke-width="0.5" opacity="0.3"/>'
        '<line x1="214" y1="6" x2="206" y2="6" stroke="#E85D2C" stroke-width="0.5" opacity="0.3"/>'
        '<line x1="214" y1="6" x2="214" y2="14" stroke="#E85D2C" stroke-width="0.5" opacity="0.3"/>'
        '</svg></div>',
        unsafe_allow_html=True,
    )

    # ── Key Status ──
    st.markdown(
        '<div style="font-size:10px;letter-spacing:2px;color:rgba(255,255,255,0.35);'
        'text-transform:uppercase;margin-bottom:6px;">Key Status</div>',
        unsafe_allow_html=True,
    )

    # Read actual API key status
    dsk_key = os.getenv("DEEPSEEK_API_KEY", "")
    oai_key = os.getenv("OPENAI_API_KEY", "")
    gem_key = os.getenv("GEMINI_API_KEY", "")

    for name, key, color in [
        ("DeepSeek", dsk_key, COLORS["success"]),
        ("OpenAI",   oai_key, COLORS["info"]),
        ("Gemini",   gem_key, COLORS["warning"]),
    ]:
        has_key = bool(key and len(key) > 5 and not key.startswith("your-") and not key.startswith("sk-your-"))
        dot_color = COLORS["success"] if has_key else COLORS["danger"]
        status_text = "Configured" if has_key else "Missing"
        status_color = COLORS["success"] if has_key else COLORS["danger"]

        st.markdown(
            f'<div class="fzq-key-row">'
            f'<span class="fzq-key-dot" style="background:{dot_color};'
            f'box-shadow:0 0 6px {dot_color}80;"></span>'
            f'<span class="label">{name}</span>'
            f'<span class="status" style="color:{status_color};">{status_text}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="fzq-sidebar-div"></div>', unsafe_allow_html=True)

    # ── Function Navigation ──
    st.markdown(
        '<div style="font-size:10px;letter-spacing:2px;color:rgba(255,255,255,0.35);'
        'text-transform:uppercase;margin-bottom:8px;">Function Navigation</div>',
        unsafe_allow_html=True,
    )

    # Session state for active nav
    if "active_nav" not in st.session_state:
        st.session_state.active_nav = "full"

    nav_items = [
        ("full",    "🔍", "Full Intelligence"),
        ("news",    "📰", "News Intel Analysis"),
        ("narr",    "🧭", "Narrative Analysis"),
        ("risk",    "⚠️", "Risk Scanner"),
        ("report",  "📋", "Daily Report"),
    ]

    for key, icon, label in nav_items:
        active_cls = "active" if st.session_state.active_nav == key else ""
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
        ):
            st.session_state.active_nav = key

    st.markdown('<div class="fzq-sidebar-div"></div>', unsafe_allow_html=True)

    # ── Query Input ──
    st.markdown(
        '<div style="font-size:10px;letter-spacing:2px;color:rgba(255,255,255,0.35);'
        'text-transform:uppercase;margin-bottom:6px;">Query</div>',
        unsafe_allow_html=True,
    )
    query = st.text_input(
        "Topic",
        placeholder="e.g. US election, Taiwan strait...",
        label_visibility="collapsed",
    )
    run_btn = st.button("▶  Execute Analysis", use_container_width=True)

    st.markdown('<div class="fzq-sidebar-div"></div>', unsafe_allow_html=True)

    # ── Footer ──
    st.markdown(
        '<div style="font-size:10px;color:rgba(255,255,255,0.3);text-align:center;'
        'line-height:1.6;">'
        '17 RSS · GDELT · NewsAPI<br>'
        'LLM: DeepSeek → OpenAI → Gemini<br>'
        'Global South ≥30% guaranteed'
        '</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# Main — Header
# ═══════════════════════════════════════════════════════════════
active_label = {
    "full": "Full Intelligence Suite",
    "news": "News Intel Analysis",
    "narr": "Narrative Deep-Dive",
    "risk": "Risk Scanner",
    "report": "Daily Report Generator",
}.get(st.session_state.active_nav, "Dashboard")

active_desc = {
    "full": "All pipelines · news → narrative → risk → sentiment → report",
    "news": "Multi-source RSS + GDELT news aggregation with relevance ranking",
    "narr": "Cross-blocs narrative comparison with theme extraction",
    "risk": "Multi-dimensional risk scoring with category breakdown",
    "report": "Structured Markdown intelligence brief with key events",
}.get(st.session_state.active_nav, "")

st.markdown(
    f'<div style="display:flex;align-items:baseline;gap:12px;margin-bottom:2px;">'
    f'<h1 style="color:{COLORS["primary"]};font-weight:700;margin:0;'
    f'font-size:26px;">FZQ-AI Intelligence Dashboard</h1>'
    f'<span style="font-size:13px;color:{COLORS["accent"]};font-weight:500;'
    f'background:{COLORS["accent"]}15;padding:2px 10px;border-radius:10px;">'
    f'{active_label}</span></div>'
    f'<p style="color:{COLORS["text_secondary"]};font-size:14px;margin-top:4px;">'
    f'{active_desc}</p>',
    unsafe_allow_html=True,
)

orchestrator = TaskOrchestrator()

# ═══════════════════════════════════════════════════════════════
# Idle State
# ═══════════════════════════════════════════════════════════════
if not run_btn or not query:
    features = [
        ("📰", "Multi-Source", "17 RSS feeds · 8 regions · GDELT · NewsAPI"),
        ("🧠", "AI Engines", "DeepSeek · OpenAI · Gemini · Auto-failover"),
        ("🌍", "Global Balance", "30%+ Global South · Cross-region rebalancing"),
        ("📊", "Visual Analytics", "Radar · Sentiment · Timeline · Narrative graph"),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f'<div class="fzq-card" style="text-align:center;padding:20px 12px;">'
                f'<div style="font-size:30px;margin-bottom:8px;">{icon}</div>'
                f'<div style="font-weight:600;font-size:14px;color:{COLORS["text_primary"]};">'
                f'{title}</div>'
                f'<div style="font-size:11px;color:{COLORS["text_secondary"]};'
                f'margin-top:4px;line-height:1.5;">{desc}</div></div>',
                unsafe_allow_html=True,
            )
    st.stop()

# ═══════════════════════════════════════════════════════════════
# Execute: News Pipeline (always runs first)
# ═══════════════════════════════════════════════════════════════
nav = st.session_state.active_nav
section_header("📰 News Intelligence", "")
news_result = orchestrator.run_agent(agent_name="news-intel", task="news", topic=query)

if not news_result["success"]:
    status_strip(f"NewsPipeline error: {news_result['error']}", "danger")
    st.stop()

bundle = news_result["data"]
articles = []
if hasattr(bundle, "articles"):
    articles = bundle.articles
elif isinstance(bundle, dict) and "intel_bundle" in bundle:
    articles = bundle["intel_bundle"].articles
else:
    articles = getattr(bundle, "articles", [])

regions = list(set(a.region for a in articles if a.region))
metric_row({
    "Articles": len(articles),
    "Regions": len(regions),
    "Sources": len(set(a.source_name for a in articles)),
    "Credibility": f"{sum(a.credibility for a in articles)/max(len(articles),1):.1f}",
})

if len(articles) == 0:
    status_strip(f"No articles matched '{query}'. Broaden your search.", "warning")
    st.stop()

# ── News cards ──
if nav in ("full", "news"):
    cols = st.columns(2)
    for i, a in enumerate(articles[:20]):
        with cols[i % 2]:
            render_news_card(a)
    if len(articles) > 20:
        st.caption(f"Showing 20 of {len(articles)} articles")

# ═══════════════════════════════════════════════════════════════
# Narrative (nav: full, narr)
# ═══════════════════════════════════════════════════════════════
if nav in ("full", "narr"):
    st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
    section_header("🧭 Narrative Analysis", "")
    narr_result = orchestrator.run_agent(agent_name="narrative", task="narrative", articles=articles)
    if narr_result["success"]:
        t1, t2 = st.tabs(["📊 Blocs View", "🕸️ Graph View"])
        with t1: render_narrative_block(narr_result["data"])
        with t2: render_narrative_graph(narr_result.get("data", {}))
    else:
        status_strip(f"Narrative: {narr_result['error']}", "warning")

# ═══════════════════════════════════════════════════════════════
# Risk (nav: full, risk)
# ═══════════════════════════════════════════════════════════════
if nav in ("full", "risk"):
    st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
    section_header("⚠️ Risk Analysis", "")
    risk_result = orchestrator.run_agent(agent_name="risk", task="risk", articles=articles)
    if risk_result["success"]:
        c1, c2 = st.columns([1, 1])
        with c1: render_risk_block(risk_result["data"])
        with c2: render_radar_chart(risk_result["data"])
    else:
        status_strip(f"Risk: {risk_result['error']}", "warning")

# ═══════════════════════════════════════════════════════════════
# Sentiment + Timeline (always shown)
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
section_header("📊 Sentiment & Timeline", "")
sent_result = orchestrator.run_agent(agent_name="sentiment", task="sentiment", articles=articles)
if sent_result["success"]:
    render_sentiment_trend(sent_result["data"])
st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
section_header("📅 Event Timeline", "")
render_timeline(articles)

# ═══════════════════════════════════════════════════════════════
# Daily Report (nav: full, report)
# ═══════════════════════════════════════════════════════════════
if nav in ("full", "report"):
    st.markdown('<div class="fzq-divider"></div>', unsafe_allow_html=True)
    section_header("📋 Daily Intelligence Report", "")
    rep_result = orchestrator.run_agent(agent_name="daily-report", task="daily-report", articles=articles)
    if rep_result["success"]:
        st.markdown(rep_result["data"])
