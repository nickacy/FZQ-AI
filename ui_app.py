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
    .fzq-card {{
        background: {C["bg_card"]}; border: 1px solid {C["border"]};
        border-radius: 10px; padding: 16px 20px; margin: 8px 0;
        box-shadow: 0 1px 3px {C["shadow"]}; transition: box-shadow 0.2s;
    }}
    .fzq-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    .fzq-tag {{
        display: inline-block; padding: 2px 8px; border-radius: 6px;
        font-size: 11px; font-weight: 500; color: #fff; margin: 0 2px;
    }}
    .fzq-status {{
        padding: 10px 16px; border-radius: 8px; margin: 8px 0;
        font-weight: 500; font-size: 14px;
    }}
    .stButton > button {{
        background: {C["accent"]} !important; color: #fff !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; padding: 8px 24px !important;
    }}
    .stButton > button:hover {{ background: #F0805A !important; }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {C["primary"]} 0%, #0F2640 100%);
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {{
        color: rgba(255,255,255,0.85) !important;
    }}
    .stTextInput > div > div > input {{
        border-radius: 8px !important; border: 2px solid {C["border"]} !important;
        font-size: 15px !important; padding: 10px 14px !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #2E5A8F !important;
        box-shadow: 0 0 0 3px rgba(30,58,95,0.1) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def section_header(title, icon=""):
    ico = f"{icon} " if icon else ""
    st.markdown(
        f'<div style="border-left:4px solid {C["primary"]};padding-left:14px;'
        f'margin:24px 0 12px;"><h3 style="margin:0;color:{C["text_primary"]};'
        f'font-weight:600;">{ico}{title}</h3></div>',
        unsafe_allow_html=True,
    )


def region_tag(region):
    labels = {"western":"West","china":"China","russia":"Russia",
              "middle_east":"Mid East","east_asia":"E Asia",
              "africa":"Africa","latin_america":"LatAm","southeast_asia":"SE Asia"}
    color = C.get(region, C["text_secondary"])
    label = labels.get(region, region.replace("_"," ").title())
    return f'<span class="fzq-tag" style="background:{color}">{label}</span>'


def status_strip(text, level="info"):
    bg = {"info":"#EFF6FF","success":"#ECFDF5","warning":"#FFFBEB","danger":"#FEF2F2"}
    tc = {"info":"#1E40AF","success":"#065F46","warning":"#92400E","danger":"#991B1B"}
    st.markdown(
        f'<div class="fzq-status" style="background:{bg.get(level,bg["info"])};'
        f'color:{tc.get(level,tc["info"])};">{text}</div>',
        unsafe_allow_html=True,
    )


def check_api_keys():
    """Detect available API keys and return status dict."""
    keys = {
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
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ═══════════════════════════════════════════════════════════════
# Sidebar — Key Status + Function Navigation
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    st.markdown(
        '<div style="text-align:center;padding:16px 0 8px;">'
        '<div style="font-size:32px;">🔍</div>'
        '<h2 style="color:#fff;margin:4px 0;font-size:22px;font-weight:700;'
        'letter-spacing:-0.5px;">FZQ-AI</h2>'
        '<p style="color:rgba(255,255,255,0.5);font-size:12px;margin:0;">'
        'Intelligence Dashboard v2.6</p></div>',
        unsafe_allow_html=True,
    )

    # ── Key Status ──
    st.markdown(
        '<p style="color:rgba(255,255,255,0.7);font-size:11px;'
        'text-transform:uppercase;letter-spacing:1px;margin:16px 0 6px;">'
        '🔑 Provider Status</p>',
        unsafe_allow_html=True,
    )
    api_keys = check_api_keys()
    for name, active in api_keys.items():
        dot = "#10B981" if active else "#EF4444"
        label = "Active" if active else "Inactive"
        st.markdown(
            f'<div style="display:flex;align-items:center;padding:5px 8px;'
            f'margin:2px 0;border-radius:6px;'
            f'background:rgba(255,255,255,0.06);">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{dot};margin-right:10px;'
            f'box-shadow:0 0 6px {dot}80;"></span>'
            f'<span style="color:rgba(255,255,255,0.9);font-size:13px;'
            f'flex:1;font-weight:500;">{name}</span>'
            f'<span style="color:{dot};font-size:11px;font-weight:600;">'
            f'{label}</span></div>',
            unsafe_allow_html=True,
        )

    # ── Separator ──
    st.markdown(
        '<div style="height:1px;background:rgba(255,255,255,0.1);'
        'margin:16px 0;"></div>',
        unsafe_allow_html=True,
    )

    # ── Function Navigation ──
    st.markdown(
        '<p style="color:rgba(255,255,255,0.7);font-size:11px;'
        'text-transform:uppercase;letter-spacing:1px;margin:0 0 8px;">'
        '📋 Function Navigation</p>',
        unsafe_allow_html=True,
    )

    functions = [
        ("▤", "News Intelligence", "Multi-source RSS news fetch + AI summary"),
        ("◎", "Narrative Analysis", "Cross-bloc narrative comparison"),
        ("◬", "Risk Scanner", "Multi-dimension risk assessment"),
        ("▥", "Daily Report", "Structured intelligence briefing"),
    ]

    if "active_function" not in st.session_state:
        st.session_state.active_function = 0

    for i, (icon, name, desc) in enumerate(functions):
        active = st.session_state.active_function == i
        bg = "rgba(255,255,255,0.12)" if active else "rgba(255,255,255,0.04)"
        border = "rgba(255,255,255,0.25)" if active else "rgba(255,255,255,0.06)"
        cursor = "pointer"
        st.markdown(
            f'<div onclick="" style="background:{bg};border:1px solid {border};'
            f'border-radius:10px;padding:12px 14px;margin:4px 0;cursor:{cursor};'
            f'transition:all 0.2s;">'
            f'<div style="display:flex;align-items:center;">'
            f'<span style="font-size:22px;margin-right:12px;">{icon}</span>'
            f'<div style="flex:1;">'
            f'<div style="color:#fff;font-size:14px;font-weight:600;">'
            f'{name}</div>'
            f'<div style="color:rgba(255,255,255,0.45);font-size:11px;">'
            f'{desc}</div></div>'
            + (f'<div style="width:6px;height:6px;border-radius:50%;'
               f'background:{C["accent"]};"></div>' if active else "") +
            f'</div></div>',
            unsafe_allow_html=True,
        )
        # Use actual Streamlit buttons for interaction
        if st.button(f"{icon} {name}", key=f"nav_{i}",
                     use_container_width=True,
                     help=desc):
            st.session_state.active_function = i

    # ── Query Input ──
    st.markdown(
        '<div style="height:1px;background:rgba(255,255,255,0.1);'
        'margin:16px 0;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:rgba(255,255,255,0.7);font-size:11px;'
        'text-transform:uppercase;letter-spacing:1px;margin:0 0 6px;">'
        '🎯 Search Query</p>',
        unsafe_allow_html=True,
    )
    query = st.text_input(
        "Topic",
        placeholder="e.g. US election, 台海局势, Gaza ceasefire...",
        label_visibility="collapsed",
    )
    run_btn = st.button("▶ Run Analysis", use_container_width=True)

    # ── Footer ──
    st.markdown(
        '<div style="position:fixed;bottom:16px;left:16px;right:16px;'
        'color:rgba(255,255,255,0.35);font-size:11px;text-align:center;">'
        '17 RSS · GDELT · NewsAPI<br>DeepSeek → OpenAI → Gemini</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# Main Header
# ═══════════════════════════════════════════════════════════════
nav_labels = ["News Intelligence", "Narrative Analysis",
              "Risk Scanner", "Daily Report"]
nav_icons = ["▤", "◎", "◬", "▥"]
active_idx = st.session_state.get("active_function", 0)

col_h, col_b = st.columns([3, 1])
with col_h:
    st.markdown(
        f'<div style="margin-bottom:20px;">'
        f'<h1 style="color:{C["primary"]};font-size:28px;font-weight:700;'
        f'margin:0;letter-spacing:-0.5px;">'
        f'{nav_icons[active_idx]} {nav_labels[active_idx]}</h1>'
        f'<p style="color:{C["text_secondary"]};font-size:14px;'
        f'margin:4px 0 0;">FZQ-AI Intelligence Dashboard — '
        f'Cross-region · Multi-source · AI-powered</p></div>',
        unsafe_allow_html=True,
    )
with col_b:
    ok_count = sum(1 for v in api_keys.values() if v)
    st.markdown(
        f'<div style="background:{C["bg_light"]};border-radius:12px;'
        f'padding:14px;text-align:center;margin-top:8px;">'
        f'<div style="font-size:22px;font-weight:700;color:{C["success"] if ok_count >= 2 else C["warning"]};">'
        f'{ok_count}/3</div>'
        f'<div style="font-size:11px;color:{C["text_secondary"]};">'
        f'Providers Ready</div></div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# Idle State — Function Cards
# ═══════════════════════════════════════════════════════════════
if not run_btn or not query:
    st.markdown(
        f'<p style="color:{C["text_secondary"]};font-size:15px;'
        f'margin:30px 0 16px;">Select a function and enter a topic to begin analysis</p>',
        unsafe_allow_html=True,
    )
    cards = [
        ("▤", "News Intelligence", "17 RSS sources across 8 regions.\nLLM-powered summarization & risk scoring."),
        ("◎", "Narrative Analysis", "Cross-bloc narrative comparison.\nThemes, consensus facts, contested claims."),
        ("◬", "Risk Scanner", "Political / economic / military / social / tech.\nMulti-dimension risk assessment."),
        ("▥", "Daily Report", "Structured intelligence briefing.\nMarkdown format with key events & risk scan."),
    ]
    cols = st.columns(4)
    for idx, (icon, name, desc) in enumerate(cards):
        with cols[idx]:
            active = idx == active_idx
            border_color = C["accent"] if active else C["border"]
            bg_color = f"{C['accent']}08" if active else C["bg_card"]
            st.markdown(
                f'<div class="fzq-card" style="border-color:{border_color};'
                f'background:{bg_color};min-height:160px;cursor:pointer;">'
                f'<div style="font-size:32px;margin-bottom:8px;">{icon}</div>'
                f'<div style="font-weight:600;font-size:15px;color:{C["text_primary"]};'
                f'margin-bottom:6px;">{name}</div>'
                f'<div style="font-size:12px;color:{C["text_secondary"]};'
                f'line-height:1.5;white-space:pre-line;">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Select {name}", key=f"card_{idx}", use_container_width=True):
                st.session_state.active_function = idx
                st.rerun()
    st.stop()


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
    articles = getattr(bundle, "articles", [])

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
        render_news_card(a)

# ═══════════════════════════════════════════════════════════════
# Function-specific analysis
# ═══════════════════════════════════════════════════════════════
fn = st.session_state.get("active_function", 0)

if fn in (1, 0):  # Narrative (or full)
    section_header("Narrative Analysis", "◎")
    nr = orchestrator.run_agent(agent_name="narrative", task="narrative", articles=articles)
    if nr["success"]:
        render_narrative_block(nr["data"])
    else:
        status_strip(f"Narrative: {nr['error']}", "warning")

if fn in (2, 0):  # Risk (or full)
    section_header("Risk Scanner", "◬")
    rr = orchestrator.run_agent(agent_name="risk", task="risk", articles=articles)
    if rr["success"]:
        c1, c2 = st.columns([3, 2])
        with c1:
            render_risk_block(rr["data"])
        with c2:
            render_radar_chart(rr["data"])
    else:
        status_strip(f"Risk: {rr['error']}", "warning")

# Sentiment + Timeline (always)
section_header("Sentiment & Timeline", "▥")
sr = orchestrator.run_agent(agent_name="sentiment", task="sentiment", articles=articles)
if sr["success"]:
    render_sentiment_trend(sr["data"])
render_timeline(articles)

# Daily Report (if selected or full)
if fn in (3, 0):
    section_header("Daily Report", "▦")
    dr = orchestrator.run_agent(agent_name="daily-report", task="daily-report", articles=articles)
    if dr["success"]:
        st.markdown(dr["data"])
    else:
        status_strip(f"Report: {dr['error']}", "warning")
