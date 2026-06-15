# ui_app.py — FZQ-AI Intelligence Dashboard (Streamlit UI) v2.6 Professional

import os, sys
from pathlib import Path

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env first
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# ═══════════════════════════════════════════════════════════════
# Theme Injection (standalone — no dependency on fzq_ai.ui.theme)
# ═══════════════════════════════════════════════════════════════
C = {
    "primary": "#1E3A5F", "accent": "#E85D2C",
    "success": "#10B981", "warning": "#F59E0B", "danger": "#EF4444",
    "info": "#3B82F6", "bg_light": "#F8FAFC", "bg_card": "#FFFFFF",
    "text_primary": "#1E293B", "text_secondary": "#64748B",
    "border": "#E2E8F0", "shadow": "rgba(0,0,0,0.06)",
    "western": "#4A90E2", "east_asia": "#D97706",
    "china": "#E02424", "russia": "#7C3AED",
    "middle_east": "#059669", "africa": "#65A30D",
}

def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        font-size: 11px; font-weight: 500; color: #fff; margin: 0 2px;
        background: {C["accent"]} !important; color: #fff !important;
    .stButton > button:hover {{ background: #F0805A !important; }}
        background: linear-gradient(180deg, {C["primary"]} 0%, #0F2640 100%);
    }}
        border-color: #2E5A8F !important;
    """, unsafe_allow_html=True)

def section_header(title, icon=""):
    ico = f"{icon} " if icon else ""

def region_tag(region):
    labels = {"western":"West","china":"China","russia":"Russia",
              "middle_east":"Mid East","east_asia":"E Asia",
              "africa":"Africa","latin_america":"LatAm","southeast_asia":"SE Asia"}
    return f'<span class="fzq-tag" style="background:{color}">{label}</span>'

def status_strip(text, level="info"):
    bg = {"info":"#EFF6FF","success":"#ECFDF5","warning":"#FFFBEB","danger":"#FEF2F2"}
    tc = {"info":"#1E40AF","success":"#065F46","warning":"#92400E","danger":"#991B1B"}

def check_api_keys():
    """Detect available API keys and return status dict."""
        "DeepSeek": bool(os.getenv("DEEPSEEK_API_KEY", "")),
        "OpenAI":   bool(os.getenv("OPENAI_API_KEY", "")),
        "Gemini":   bool(os.getenv("GEMINI_API_KEY", "")),
    }
    return keys

# ═══════════════════════════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FZQ-AI · Intelligence Dashboard",
)
inject_css()

# ═══════════════════════════════════════════════════════════════
# Sidebar — Key Status + Function Navigation
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
        '<div style="text-align:center;padding:16px 0 8px;">'
        '<div style="font-size:32px;">🔍</div>'
        '<h2 style="color:#fff;margin:4px 0;font-size:22px;font-weight:700;'
        'letter-spacing:-0.5px;">FZQ-AI</h2>'
        '<p style="color:rgba(255,255,255,0.5);font-size:12px;margin:0;">'
        'Intelligence Dashboard v2.6</p></div>',

    # ── Key Status ──
        '<p style="color:rgba(255,255,255,0.7);font-size:11px;'
        'text-transform:uppercase;letter-spacing:1px;margin:16px 0 6px;">'
        '🔑 Provider Status</p>',
    for name, active in api_keys.items():
        dot = "#10B981" if active else "#EF4444"
        label = "Active" if active else "Inactive"

    # ── Separator ──
        '<div style="height:1px;background:rgba(255,255,255,0.1);'
        'margin:16px 0;"></div>',

    # ── Function Navigation ──
        '<p style="color:rgba(255,255,255,0.7);font-size:11px;'
        'text-transform:uppercase;letter-spacing:1px;margin:0 0 8px;">'
        '📋 Function Navigation</p>',

    if "active_function" not in st.session_state:

    for i, (icon, name, desc) in enumerate(functions):
        active = st.session_state.active_function == i
        bg = "rgba(255,255,255,0.12)" if active else "rgba(255,255,255,0.04)"
        border = "rgba(255,255,255,0.25)" if active else "rgba(255,255,255,0.06)"
        cursor = "pointer"
            f'<div style="color:#fff;font-size:14px;font-weight:600;">'
               f'background:{C["accent"]};"></div>' if active else "") +
        # Use actual Streamlit buttons for interaction
        if st.button(f"{icon} {name}", key=f"nav_{i}",
                     use_container_width=True,

    # ── Query Input ──
        '<div style="height:1px;background:rgba(255,255,255,0.1);'
        'margin:16px 0;"></div>',
        '<p style="color:rgba(255,255,255,0.7);font-size:11px;'
        'text-transform:uppercase;letter-spacing:1px;margin:0 0 6px;">'
        '🎯 Search Query</p>',
        "Topic",

    # ── Footer ──
        '<div style="position:fixed;bottom:16px;left:16px;right:16px;'
        'color:rgba(255,255,255,0.35);font-size:11px;text-align:center;">'
        '17 RSS · GDELT · NewsAPI<br>DeepSeek → OpenAI → Gemini</div>',

# ═══════════════════════════════════════════════════════════════
# Main Header
# ═══════════════════════════════════════════════════════════════
nav_labels = ["News Intelligence", "Narrative Analysis",
              "Risk Scanner", "Daily Report"]
nav_icons = ["▤", "◎", "◬", "▥"]
active_idx = st.session_state.get("active_function", 0)

col_h, col_b = st.columns([3, 1])
with col_h:
with col_b:
    ok_count = sum(1 for v in api_keys.values() if v)
    st.markdown(
        f'<div style="background:{C["bg_light"]};border-radius:12px;'
        f'<div style="font-size:22px;font-weight:700;color:{C["success"] if ok_count >= 2 else C["warning"]};">'

# ═══════════════════════════════════════════════════════════════
# Idle State — Function Cards
# ═══════════════════════════════════════════════════════════════
if not run_btn or not query:
        ("▥", "Daily Report", "Structured intelligence briefing.\nMarkdown format with key events & risk scan."),
    ]
    for idx, (icon, name, desc) in enumerate(cards):
        with cols[idx]:
            border_color = C["accent"] if active else C["border"]
            bg_color = f"{C['accent']}08" if active else C["bg_card"]
            if st.button(f"Select {name}", key=f"card_{idx}", use_container_width=True):
                st.session_state.active_function = idx

# ═══════════════════════════════════════════════════════════════
# Import orchestrator (lazy)
# ═══════════════════════════════════════════════════════════════
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.ui.components.news_card import render_news_card
from fzq_ai.ui.components.narrative_block import render_narrative_block
from fzq_ai.ui.components.risk_block import render_risk_block
from fzq_ai.ui.components.radar_chart import render_radar_chart
from fzq_ai.ui.components.sentiment_trend import render_sentiment_trend
from fzq_ai.ui.components.timeline import render_timeline

orchestrator = TaskOrchestrator()

# ═══════════════════════════════════════════════════════════════
# Execute: News Pipeline (always first)
# ═══════════════════════════════════════════════════════════════
with st.spinner("Fetching news from 17 sources across 8 regions..."):
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

if len(articles) == 0:
    status_strip(f"No articles found for '{query}'. Try a broader keyword.", "warning")
    st.stop()

# ── Metrics bar ──
regions = list(set(a.region for a in articles if a.region))
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Articles", len(articles))
m2.metric("Regions", len(regions))
m3.metric("Sources", len(set(getattr(a, "source_name", "") for a in articles)))
m4.metric("Credibility", f"{sum(getattr(a,'credibility',0) for a in articles)/max(len(articles),1):.2f}")
m5.metric("Global South %", f"{sum(1 for a in articles if a.region in ('china','russia','middle_east','africa','latin_america','east_asia','southeast_asia'))/max(len(articles),1)*100:.0f}%")

# ── News Grid ──
section_header("News Feed", "▤")
cols = st.columns(2)
for i, a in enumerate(articles[:20]):
    with cols[i % 2]:

# ═══════════════════════════════════════════════════════════════
# Function-specific analysis
# ═══════════════════════════════════════════════════════════════
fn = st.session_state.get("active_function", 0)

if fn in (1, 0):  # Narrative (or full)
    section_header("Narrative Analysis", "◎")
    nr = orchestrator.run_agent(agent_name="narrative", task="narrative", articles=articles)
    if nr["success"]:
    else:

if fn in (2, 0):  # Risk (or full)
    section_header("Risk Scanner", "◬")
    rr = orchestrator.run_agent(agent_name="risk", task="risk", articles=articles)
    if rr["success"]:
        with c1:
        with c2:
    else:

# Sentiment + Timeline (always)
section_header("Sentiment & Timeline", "▥")
sr = orchestrator.run_agent(agent_name="sentiment", task="sentiment", articles=articles)
if sr["success"]:
render_timeline(articles)

# Daily Report (if selected or full)
if fn in (3, 0):
    section_header("Daily Report", "▦")
    dr = orchestrator.run_agent(agent_name="daily-report", task="daily-report", articles=articles)
    if dr["success"]:
    else:
