import streamlit as st
import time
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os
from dotenv import load_dotenv
load_dotenv()

from main import app as agent_graph
from utils.processor import extract_text_from_upload

# ============================================================
# PAGE CONFIG — Must be first Streamlit call
# ============================================================
st.set_page_config(
    page_title="VerifAI · Enterprise AI Orchestrator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# MASTER CSS — Glassmorphism + 2026 Enterprise Theme
# ============================================================
st.markdown("""
<style>
/* ── Google Font Import ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root Tokens ────────────────────────────────────────── */
:root {
    --bg-base:          #080e1a;
    --bg-surface:       rgba(14, 22, 38, 0.85);
    --bg-card:          rgba(255, 255, 255, 0.045);
    --bg-card-hover:    rgba(255, 255, 255, 0.075);
    --border:           rgba(255, 255, 255, 0.08);
    --border-active:    rgba(20, 184, 166, 0.5);
    --teal:             #14b8a6;
    --teal-glow:        rgba(20, 184, 166, 0.35);
    --cyan:             #06b6d4;
    --purple:           #a78bfa;
    --amber:            #f59e0b;
    --rose:             #f43f5e;
    --green:            #10b981;
    --text-primary:     #f1f5f9;
    --text-secondary:   #94a3b8;
    --text-muted:       #475569;
    --radius-sm:        8px;
    --radius-md:        14px;
    --radius-lg:        20px;
    --blur:             blur(20px);
}

/* ── Global reset ───────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: var(--bg-base) !important;
    color: var(--text-primary);
}

/* ── Subtle mesh-gradient background ───────────────────── */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% -10%, rgba(20,184,166,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 110%, rgba(167,139,250,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(6,182,212,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Main content keeps above bg layer ─────────────────── */
.block-container { position: relative; z-index: 1; padding-top: 4.5rem !important; margin-top: 1rem !important; }

/* ── Streamlit native elements override ─────────────────── */
.stApp > header { display: none; }
section[data-testid="stSidebar"] > div:first-child {
    background: rgba(8, 14, 26, 0.92) !important;
    border-right: 1px solid var(--border);
    backdrop-filter: var(--blur);
}

/* ── Glassmorphism base card ─────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    padding: 20px 24px;
    transition: background 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.glass-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-active);
    box-shadow: 0 0 40px var(--teal-glow);
}

/* ── Hero header ─────────────────────────────────────────── */
.verifai-hero {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 28px;
    background: linear-gradient(135deg, rgba(20,184,166,0.12) 0%, rgba(167,139,250,0.08) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    backdrop-filter: var(--blur);
    margin-bottom: 28px;
}
.verifai-logo {
    font-size: 2.6rem;
    line-height: 1;
}
.verifai-name {
    font-size: 2.0rem;
    font-weight: 900;
    background: linear-gradient(90deg, #14b8a6, #06b6d4, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    line-height: 1;
}
.verifai-tagline {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}
.hero-right {
    margin-left: auto;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
}
.live-badge {
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--green);
    letter-spacing: 0.5px;
}
.live-dot {
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    animation: livePulse 1.6s infinite;
    box-shadow: 0 0 0 0 rgba(16,185,129,0.7);
}
@keyframes livePulse {
    0%   { box-shadow: 0 0 0 0   rgba(16,185,129,0.7); }
    70%  { box-shadow: 0 0 0 8px rgba(16,185,129,0.0); }
    100% { box-shadow: 0 0 0 0   rgba(16,185,129,0.0); }
}
.task-id-badge {
    font-size: 0.68rem;
    color: var(--text-muted);
    font-family: 'Courier New', monospace;
}

/* ── Status alert cards ──────────────────────────────────── */
.status-escalated {
    background: linear-gradient(135deg, rgba(244,63,94,0.15) 0%, rgba(244,63,94,0.05) 100%);
    border: 1px solid rgba(244,63,94,0.4);
    border-radius: var(--radius-md);
    padding: 18px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    animation: escalatedPulse 2.5s ease-in-out infinite;
}
@keyframes escalatedPulse {
    0%, 100% { box-shadow: 0 0 0   0 rgba(244,63,94,0.0); }
    50%       { box-shadow: 0 0 30px 4px rgba(244,63,94,0.25); }
}
.status-completed {
    background: linear-gradient(135deg, rgba(16,185,129,0.14) 0%, rgba(16,185,129,0.05) 100%);
    border: 1px solid rgba(16,185,129,0.35);
    border-radius: var(--radius-md);
    padding: 18px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.status-failed {
    background: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(245,158,11,0.05) 100%);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: var(--radius-md);
    padding: 18px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.status-icon { font-size: 2.2rem; }
.status-label {
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: 0.5px;
}
.status-sub {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 3px;
}
.status-escalated .status-label { color: var(--rose); }
.status-completed .status-label { color: var(--green); }
.status-failed    .status-label { color: var(--amber); }

/* ── Workflow badge ──────────────────────────────────────── */
.workflow-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(20,184,166,0.12);
    border: 1px solid rgba(20,184,166,0.3);
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--teal);
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── KPI metric cards ────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border-radius: var(--radius-md) !important;
    padding: 20px 18px !important;
    transition: all 0.25s ease;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3);
}
div[data-testid="metric-container"]:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--border-active) !important;
    box-shadow: 0 4px 30px var(--teal-glow);
    transform: translateY(-3px);
}
div[data-testid="metric-container"] label {
    color: var(--text-secondary) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    color: var(--text-primary) !important;
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
}
div[data-testid="metric-container"] [data-testid="metric-delta"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
}

/* ── Agents progress bar ─────────────────────────────────── */
.agents-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px 18px;
    transition: all 0.25s ease;
}
.agents-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-active);
    box-shadow: 0 4px 30px var(--teal-glow);
    transform: translateY(-3px);
}
.agents-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 8px;
}
.agents-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}
.agents-track {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
}
.agents-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--teal), var(--cyan));
    box-shadow: 0 0 10px rgba(20,184,166,0.5);
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}

/* ── Stacked tab styling ─────────────────────────────────── */
div[data-testid="stTabs"] button {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 18px !important;
    transition: all 0.2s !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--teal) !important;
    border-bottom-color: var(--teal) !important;
    background: rgba(20,184,166,0.06) !important;
    border-radius: 8px 8px 0 0 !important;
}
div[data-testid="stTabs"] button:hover {
    color: var(--text-primary) !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Extracted entity pills ──────────────────────────────── */
.entity-pill {
    display: inline-block;
    background: rgba(20,184,166,0.12);
    border: 1px solid rgba(20,184,166,0.25);
    border-radius: var(--radius-sm);
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--teal);
    margin: 3px 3px;
    letter-spacing: 0.3px;
}
.entity-key {
    color: var(--text-secondary);
    font-size: 0.72rem;
    font-weight: 500;
}
.entity-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: background 0.2s;
}
.entity-row:last-child { border-bottom: none; }
.entity-row:hover { background: rgba(255,255,255,0.03); border-radius: var(--radius-sm); }
.entity-val {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.88rem;
    max-width: 55%;
    text-align: right;
    word-break: break-all;
}

/* ── Section headers ─────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}
.section-icon {
    width: 36px; height: 36px;
    background: rgba(20,184,166,0.12);
    border: 1px solid rgba(20,184,166,0.25);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.section-title {
    font-size: 1.0rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.2px;
}
.section-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
}

/* ── Timeline entry ──────────────────────────────────────── */
.timeline-entry {
    position: relative;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 16px 20px 16px 36px;
    margin-bottom: 12px;
    transition: all 0.2s;
}
.timeline-entry:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-active);
    box-shadow: 0 4px 20px var(--teal-glow);
}
.timeline-dot {
    position: absolute;
    left: -7px; top: 22px;
    width: 14px; height: 14px;
    border-radius: 50%;
    border: 2px solid var(--bg-base);
    box-shadow: 0 0 8px currentColor;
}
.timeline-connector {
    position: absolute;
    left: 0; top: 36px;
    width: 2px;
    bottom: -12px;
    background: var(--border);
}

/* ── Health card ─────────────────────────────────────────── */
.health-ok {
    background: linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(6,182,212,0.06) 100%);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: var(--radius-md);
    padding: 20px 24px;
    display: flex; align-items: center; gap: 16px;
    animation: healthGlow 3s ease-in-out infinite;
}
@keyframes healthGlow {
    0%, 100% { box-shadow: 0 0  0  0 rgba(16,185,129,0.0); }
    50%       { box-shadow: 0 0 24px 0 rgba(16,185,129,0.2); }
}
.health-issue {
    background: linear-gradient(135deg, rgba(245,158,11,0.12) 0%, rgba(245,158,11,0.04) 100%);
    border: 1px solid rgba(245,158,11,0.35);
    border-radius: var(--radius-md);
    padding: 20px 24px;
}

/* ── Error pill ──────────────────────────────────────────── */
.error-pill {
    background: rgba(244,63,94,0.10);
    border: 1px solid rgba(244,63,94,0.25);
    border-radius: var(--radius-sm);
    padding: 8px 14px;
    font-size: 0.80rem;
    color: #fb7185;
    margin-top: 8px;
}

/* ── Sidebar styles ──────────────────────────────────────── */
.sidebar-stat {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    margin-bottom: 10px;
    transition: all 0.2s;
}
.sidebar-stat:hover { background: rgba(255,255,255,0.07); border-color: var(--border-active); }
.sidebar-stat-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--text-muted); }
.sidebar-stat-value { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); margin-top: 2px; }

/* ── LangSmith button ────────────────────────────────────── */
.ls-btn {
    display: block;
    background: linear-gradient(135deg, #1f6feb 0%, #a78bfa 100%);
    padding: 18px 24px;
    border-radius: var(--radius-md);
    text-align: center;
    color: white !important;
    font-weight: 700;
    font-size: 1.05rem;
    text-decoration: none !important;
    box-shadow: 0 4px 20px rgba(167,139,250,0.35);
    transition: all 0.25s ease;
    letter-spacing: 0.3px;
}
.ls-btn:hover {
    box-shadow: 0 8px 30px rgba(167,139,250,0.5);
    transform: translateY(-2px);
    text-decoration: none !important;
    color: white !important;
}
.ls-meta {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 14px;
}
.ls-meta strong { color: var(--text-secondary); }

/* ── File uploader area ──────────────────────────────────── */
div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.025) !important;
    border: 2px dashed rgba(20,184,166,0.25) !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(20,184,166,0.55) !important;
    background: rgba(20,184,166,0.06) !important;
}
div[data-testid="stFileUploader"] label { color: var(--text-secondary) !important; }

/* ── Spinner color ───────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--teal) !important; }

/* ── Expander ────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Divider ─────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 24px 0 !important; }

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(20,184,166,0.3); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(20,184,166,0.6); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER: Build a beautiful Plotly gauge chart
# ============================================================
def make_gauge(value: float, title: str, suffix: str = "%",
               min_val: float = 0, max_val: float = 100) -> go.Figure:
    """
    Returns a dark-themed Plotly Indicator gauge with color-coded fill:
      - < 60  → rose/red
      - 60–85 → amber
      - > 85  → teal/green
    """
    if value > 85:
        bar_color = "#10b981"
        glow = "rgba(16,185,129,0.35)"
    elif value >= 60:
        bar_color = "#f59e0b"
        glow = "rgba(245,158,11,0.35)"
    else:
        bar_color = "#f43f5e"
        glow = "rgba(244,63,94,0.35)"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={
            "suffix": suffix,
            "font": {"color": "#f1f5f9", "size": 32, "family": "Inter"},
        },
        title={
            "text": title,
            "font": {"color": "#94a3b8", "size": 13, "family": "Inter"},
        },
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {
                "range": [min_val, max_val],
                "tickwidth": 1,
                "tickcolor": "#334155",
                "tickfont": {"color": "#475569", "size": 10},
            },
            "bar": {"color": bar_color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [min_val, 60],       "color": "rgba(244,63,94,0.10)"},
                {"range": [60, 85],            "color": "rgba(245,158,11,0.10)"},
                {"range": [85, max_val],       "color": "rgba(16,185,129,0.10)"},
            ],
            "threshold": {
                "line": {"color": bar_color, "width": 3},
                "thickness": 0.8,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=24, t=48, b=16),
        height=220,
        font={"family": "Inter"},
    )
    return fig


# ============================================================
# HELPER: Build the agents-progress circular gauge
# ============================================================
def make_agents_donut(done: int, total: int = 7) -> go.Figure:
    pct = done / total * 100
    remaining = total - done

    fig = go.Figure(go.Pie(
        values=[done, remaining],
        hole=0.72,
        marker_colors=["#14b8a6", "rgba(255,255,255,0.05)"],
        textinfo="none",
        hoverinfo="skip",
        rotation=90,
    ))
    fig.add_annotation(
        text=f"<b style='font-size:22px;color:#f1f5f9'>{done}/{total}</b><br>"
             f"<span style='font-size:11px;color:#94a3b8'>Agents</span>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family="Inter", size=13),
        align="center",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
    )
    return fig


# ============================================================
# HELPER: Render key-value entity rows
# ============================================================
def render_entities(data: dict, depth: int = 0) -> str:
    """Recursively renders a dict into clean HTML entity rows."""
    html = ""
    for k, v in data.items():
        key_label = str(k).replace("_", " ").title()
        if isinstance(v, dict) and v:
            html += f"""
            <div style="padding:10px 16px 2px;">
                <span class="entity-key" style="font-size:0.8rem; font-weight:700; color:#64748b">
                    ▸ {key_label}
                </span>
            </div>"""
            html += render_entities(v, depth + 1)
        elif isinstance(v, list) and v:
            val_str = ", ".join(str(x) for x in v[:5])
            if len(v) > 5:
                val_str += f" +{len(v)-5} more"
            html += f"""
            <div class="entity-row">
                <span class="entity-key">{key_label}</span>
                <span class="entity-val">{val_str}</span>
            </div>"""
        else:
            if v is None or v == "" or v == []:
                continue
            html += f"""
            <div class="entity-row">
                <span class="entity-key">{key_label}</span>
                <span class="entity-val">{v}</span>
            </div>"""
    return html


# ============================================================
# SIDEBAR — System Health + Quick Stats
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
            <span style="font-size:1.5rem;">🛡️</span>
            <div>
                <div style="font-size:1.1rem;font-weight:800;background:linear-gradient(90deg,#14b8a6,#06b6d4);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                    VerifAI
                </div>
                <div style="font-size:0.65rem;color:#475569;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">
                    Enterprise Orchestrator
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:22px;">
            <div class="live-dot"></div>
            <span style="font-size:0.75rem;font-weight:600;color:#10b981;letter-spacing:0.5px;">SYSTEM ONLINE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar stats placeholder (updated post-processing)
    sidebar_status_placeholder = st.empty()
    sidebar_roi_placeholder    = st.empty()
    sidebar_time_placeholder   = st.empty()

    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)

    # Default sidebar state
    with sidebar_status_placeholder.container():
        st.markdown("""
        <div class="sidebar-stat">
            <div class="sidebar-stat-label">Status</div>
            <div class="sidebar-stat-value" style="color:#475569;">IDLE</div>
        </div>""", unsafe_allow_html=True)
    with sidebar_roi_placeholder.container():
        st.markdown("""
        <div class="sidebar-stat">
            <div class="sidebar-stat-label">ROI Improvement</div>
            <div class="sidebar-stat-value" style="color:#475569;">—</div>
        </div>""", unsafe_allow_html=True)
    with sidebar_time_placeholder.container():
        st.markdown("""
        <div class="sidebar-stat">
            <div class="sidebar-stat-label">Processing Time</div>
            <div class="sidebar-stat-value" style="color:#475569;">—</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="position:absolute;bottom:24px;left:20px;right:20px;font-size:0.65rem;
        color:#334155;text-align:center;letter-spacing:0.5px;">
        ET AI Hackathon 2026 · Build v2.0
    </div>""", unsafe_allow_html=True)


# ============================================================
# HERO HEADER
# ============================================================
st.markdown("""
<div class="verifai-hero">
    <div class="verifai-logo">🛡️</div>
    <div>
        <div class="verifai-name">VerifAI</div>
        <div class="verifai-tagline">Flagship Multi-Agent Orchestrator · 2026</div>
    </div>
    <div class="hero-right">
        <div class="live-badge">
            <div class="live-dot"></div>
            LIVE SYSTEM
        </div>
        <div class="task-id-badge">7-Agent · LangGraph · LangSmith</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# FILE UPLOADER
# ============================================================
uploaded_file = st.file_uploader(
    "🗂️  Upload Invoice, HR Document, or Meeting Transcript",
    type=["pdf", "docx", "txt"],
    help="Supports PDF, DOCX, TXT — up to 5 MB",
)


# ============================================================
# MAIN PIPELINE (runs only when a file is uploaded)
# ============================================================
if uploaded_file:
    with st.spinner("⚙️  VerifAI orchestrating 7-agent pipeline…"):
        try:
            raw_text = extract_text_from_upload(uploaded_file)
            if not raw_text or len(raw_text.strip()) < 10:
                st.error("⚠️ Could not extract readable text. Please upload a clearer document.")
                st.stop()

            start_timestamp = time.time()

            initial_state = {
                "task_id":        f"VERIFAI-{int(start_timestamp)}",
                "file_name":      uploaded_file.name,
                "start_time":     start_timestamp,
                "raw_input":      raw_text,
                "workflow_type":  None,
                "extracted_data": {},
                "audit_log":      [],
                "errors":         [],
                "retry_count":    0,
                "correction_flag": False,
                "status":         "initiated",
                "next_step":      "coordinator",
            }

            final_state = agent_graph.invoke(initial_state)

        except Exception as e:
            st.error(f"❌ System crash: {e}")
            st.stop()

    # ── Metric recovery ──────────────────────────────────────
    audit_log   = final_state.get("audit_log", [])
    last_entry  = audit_log[-1] if audit_log else {}
    metrics     = last_entry.get("metrics", {})

    if not metrics and final_state.get("status") == "completed":
        st.warning("⚠️ Monitoring agent did not return performance metrics.")

    autonomy_score  = metrics.get("autonomy_score", 0)
    savings_per_tx  = metrics.get("net_savings_inr", metrics.get("net_savings_usd", 0.0))
    processing_time = metrics.get("processing_time_sec", 0.0)
    wall_time       = round(time.time() - start_timestamp, 2)
    unique_agents   = len(set(e.get("agent", "Unknown") for e in audit_log))

    manual_cost = 2000.00
    ai_cost     = 12.00
    improvement = ((manual_cost - ai_cost) / manual_cost) * 100  # Constant business-value ROI

    conf_raw    = final_state.get("confidence_score", None)
    conf_pct    = round(conf_raw * 100, 1) if conf_raw is not None else 0.0

    status      = final_state.get("status", "failed").upper()
    w_type      = final_state.get("workflow_type", "UNKNOWN").upper()
    task_id     = initial_state["task_id"]

    # ── Workflow + status banner ──────────────────────────────
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    col_wf, col_st = st.columns([1, 3])
    with col_wf:
        st.markdown(f"""
        <div class="workflow-pill">🔀 &nbsp;{w_type}</div>
        """, unsafe_allow_html=True)

    with col_st:
        if status == "COMPLETED":
            st.markdown("""
            <div class="status-completed">
                <span class="status-icon">✅</span>
                <div>
                    <div class="status-label">WORKFLOW COMPLETED</div>
                    <div class="status-sub">All agents executed without human intervention required.</div>
                </div>
            </div>""", unsafe_allow_html=True)
        elif status in ("ESCALATED", "WAITING_FOR_USER"):
            errors_txt = " · ".join(final_state.get("errors", [])) or "Low confidence detected."
            st.markdown(f"""
            <div class="status-escalated">
                <span class="status-icon">✋</span>
                <div>
                    <div class="status-label">HUMAN-IN-THE-LOOP TRIGGERED</div>
                    <div class="status-sub">Clarification gate activated — {errors_txt}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-failed">
                <span class="status-icon">⚠️</span>
                <div>
                    <div class="status-label">WORKFLOW {status}</div>
                    <div class="status-sub">Review the audit trail for failure details.</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────
    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    with kc1:
        delta_msg = "⬆ Self-Healed" if final_state.get("correction_flag") else "✓ Verified"
        st.metric("🎯 Autonomy Score", f"{autonomy_score}%", delta=delta_msg)
    with kc2:
        st.metric("💰 Cost Savings", f"₹{round(savings_per_tx, 2):,}", delta=f"{round(processing_time, 2)}s")
    with kc3:
        st.metric("📈 Annual Impact", f"₹{savings_per_tx * 1000:,.0f}", delta="per 1,000 TX")
    with kc4:
        st.metric("⚡ ROI Improvement", f"{round(improvement, 1)}%", delta="vs Manual")
    with kc5:
        if conf_raw is not None:
            st.metric("🧠 AI Confidence", f"{conf_pct}%", delta="Extraction Quality")
        else:
            st.metric("🧠 AI Confidence", "N/A")

    # Agents progress (custom card — below KPIs)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    prog_pct = min(unique_agents / 7 * 100, 100)
    st.markdown(f"""
    <div class="agents-card">
        <div class="agents-label">🤖 &nbsp;Agents Executed</div>
        <div class="agents-value">{unique_agents} / 7</div>
        <div class="agents-track">
            <div class="agents-fill" style="width:{prog_pct:.1f}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── DATA TABS ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋  Executive Overview",
        "🚦  Live Audit Trail",
        "📈  Metrics Dashboard",
        "🧠  LangSmith Trace",
    ])

    # ── TAB 1: Executive Overview ─────────────────────────────
    with tab1:
        colA, colB = st.columns(2, gap="large")

        # Left: Extracted entities
        with colA:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">📄</div>
                <div>
                    <div class="section-title">Extracted Entities</div>
                    <div class="section-sub">Structured fields parsed from the document</div>
                </div>
            </div>""", unsafe_allow_html=True)

            raw_data = final_state.get("extracted_data", {})
            if raw_data:
                rows_html = render_entities(raw_data)
                st.markdown(f"""
                <div class="glass-card" style="padding:8px 0;">
                    {rows_html}
                </div>""", unsafe_allow_html=True)

                # Copyable raw JSON in expander
                with st.expander("🔍 View Raw JSON"):
                    st.code(json.dumps(raw_data, indent=2), language="json")
            else:
                st.markdown("""
                <div class="glass-card" style="text-align:center;color:#475569;padding:40px;">
                    No entities extracted.
                </div>""", unsafe_allow_html=True)

        # Right: System Health
        with colB:
            st.markdown("""
            <div class="section-header">
                <div class="section-icon">🏥</div>
                <div>
                    <div class="section-title">System Health & Healing</div>
                    <div class="section-sub">Autonomous self-correction activity</div>
                </div>
            </div>""", unsafe_allow_html=True)

            healing_actions = [
                e for e in audit_log
                if e.get("correction_flag") or e.get("recovery_used") or e.get("critic_loops", 0) > 0
            ]

            if healing_actions or final_state.get("correction_flag"):
                st.markdown("""
                <div class="health-issue">
                    <div style="font-weight:700;color:#fbbf24;margin-bottom:10px;">
                        ✨ Autonomous interventions applied
                    </div>
                    <div style="font-size:0.82rem;color:#94a3b8;">
                        Critic / Semantic Vector Matching corrections detected.
                    </div>
                </div>""", unsafe_allow_html=True)
                for action in healing_actions:
                    st.markdown(f"""
                    <div style="margin-top:10px;padding:10px 14px;
                        background:rgba(245,158,11,0.07);border-radius:var(--radius-sm);
                        border-left:3px solid #f59e0b;">
                        <strong style='color:#fbbf24;'>{action.get('agent')}</strong>
                        <div style="font-size:0.80rem;color:#94a3b8;margin-top:4px;">
                            {action.get('details','—')}
                        </div>
                    </div>""", unsafe_allow_html=True)
            elif status in ("ESCALATED", "WAITING_FOR_USER"):
                st.markdown("""
                <div class="health-issue" style="border-left:5px solid #f43f5e; background:rgba(244,63,94,0.06);">
                    <div style="font-weight:700;color:#f43f5e;margin-bottom:10px;">
                        ✋ Human Review Required
                    </div>
                    <div style="font-size:0.82rem;color:#94a3b8;">
                        VerifAI has paused the autonomous pipeline and triggered the <b>Clarification Gate</b>. 
                        This ensures data integrity by preventing hallucinations during low-confidence events.
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="health-ok">
                    <span style="font-size:2.5rem;">✅</span>
                    <div>
                        <div style="font-weight:700;font-size:1.0rem;color:#10b981;">
                            Zero Interventions Required
                        </div>
                        <div style="font-size:0.82rem;color:#94a3b8;margin-top:4px;">
                            VerifAI processed the document autonomously with full confidence.
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            if final_state.get("errors"):
                st.markdown("<div style='margin-top:14px;'>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:0.78rem;font-weight:700;color:#f43f5e;
                    margin-bottom:6px;">⚠️ System Violations / Errors</div>""",
                    unsafe_allow_html=True)
                for err in final_state["errors"]:
                    st.markdown(f'<div class="error-pill">— {err}</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 2: Audit Trail ────────────────────────────────────
    with tab2:
        st.markdown("""
        <div class="section-header" style="margin-bottom:24px;">
            <div class="section-icon">🚦</div>
            <div>
                <div class="section-title">Execution Timeline</div>
                <div class="section-sub">Step-by-step agent activity log</div>
            </div>
        </div>""", unsafe_allow_html=True)

        for i, entry in enumerate(audit_log, 1):
            agent   = entry.get("agent", "System")
            event   = entry.get("event", "Action")
            details = entry.get("details", "No details provided.")
            t_stamp = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"])) \
                      if entry.get("timestamp") else "—"

            # Color-code by agent type
            if "Clarification" in agent or "Failed" in event:
                dot_color, label_color = "#f43f5e", "#fb7185"
                icon = "⚠️"
            elif "Critic" in agent:
                dot_color, label_color = "#a78bfa", "#c4b5fd"
                icon = "🧐"
            elif "Matching" in agent:
                dot_color, label_color = "#06b6d4", "#67e8f9"
                icon = "🏥"
            elif "Monitor" in agent:
                dot_color, label_color = "#10b981", "#6ee7b7"
                icon = "📊"
            else:
                dot_color, label_color = "#14b8a6", "#5eead4"
                icon = "🤖"

            st.markdown(f"""
            <div class="timeline-entry" style="border-left: 2px solid {dot_color}30;">
                <div class="timeline-dot" style="background:{dot_color};color:{dot_color};"></div>
                <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:6px;">
                    <div style="font-weight:700;font-size:0.95rem;color:{label_color};">
                        {icon} &nbsp;Step {i}: {agent}
                    </div>
                    <div style="font-size:0.70rem;color:#475569;font-family:monospace;">⏱ {t_stamp}</div>
                </div>
                <div style="font-size:0.82rem;font-weight:600;color:#94a3b8;margin-bottom:4px;">{event}</div>
                <div style="font-size:0.80rem;color:#64748b;">{details}</div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 3: Metrics Dashboard ──────────────────────────────
    with tab3:
        st.markdown("""
        <div class="section-header" style="margin-bottom:8px;">
            <div class="section-icon">📈</div>
            <div>
                <div class="section-title">Live Processing Metrics</div>
                <div class="section-sub">Plotly gauges — color-coded: green &gt; 85%, amber 60–85%, red &lt; 60%</div>
            </div>
        </div>""", unsafe_allow_html=True)

        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            st.markdown('<div class="glass-card" style="padding:12px;">', unsafe_allow_html=True)
            st.plotly_chart(
                make_gauge(autonomy_score, "Autonomy Score"),
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with gc2:
            st.markdown('<div class="glass-card" style="padding:12px;">', unsafe_allow_html=True)
            st.plotly_chart(
                make_gauge(conf_pct if conf_raw is not None else 0,
                           "AI Confidence"),
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with gc3:
            st.markdown('<div class="glass-card" style="padding:12px;">', unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align:center;font-size:0.75rem;font-weight:600;color:#94a3b8;
                letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                Agents Progress
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(
                make_agents_donut(unique_agents),
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Summary stats row
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.metric("⏱️ Wall-Clock Time",  f"{wall_time}s")
        with sc2:
            st.metric("💸 Manual Cost",       f"₹{manual_cost:,.0f}")
        with sc3:
            st.metric("🤖 AI Cost",           f"₹{ai_cost:,.0f}")
        with sc4:
            st.metric("🔁 Retry Count",       final_state.get("retry_count", 0))

    # ── TAB 4: LangSmith ─────────────────────────────────────
    with tab4:
        st.markdown("""
        <div class="section-header" style="margin-bottom:20px;">
            <div class="section-icon">🧠</div>
            <div>
                <div class="section-title">LangSmith Observability</div>
                <div class="section-sub">Full LLM prompt, context, tool invocations, and nested AI traces</div>
            </div>
        </div>""", unsafe_allow_html=True)

        smith_url = "https://smith.langchain.com/o/default/projects?p=VerifAI-Agent"
        st.markdown(f"""
        <a href="{smith_url}" target="_blank" class="ls-btn">
            🔗 &nbsp;Open Live Trace in LangSmith Dashboard
        </a>
        <div class="ls-meta" style="margin-top:16px;">
            Project: <strong>VerifAI-Agent</strong> &nbsp;·&nbsp;
            Task ID: <strong>{task_id}</strong> &nbsp;·&nbsp;
            Status: <strong>{status}</strong>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:700;font-size:0.95rem;color:#10b981;margin-bottom:10px;">
                ✅ LangSmith Tracing Active
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;line-height:1.6;">
                Every LLM call, tool invocation, and agent hop for this run has been recorded.
                Explore prompt templates, token counts, latency breakdowns, and model outputs
                in the LangSmith dashboard above.
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Update sidebar with live results ─────────────────────
    status_color = (
        "#10b981" if status == "COMPLETED"
        else "#f43f5e" if "ESCALAT" in status
        else "#f59e0b"
    )
    with sidebar_status_placeholder.container():
        st.markdown(f"""
        <div class="sidebar-stat">
            <div class="sidebar-stat-label">Status</div>
            <div class="sidebar-stat-value" style="color:{status_color};">{status}</div>
        </div>""", unsafe_allow_html=True)
    with sidebar_roi_placeholder.container():
        st.markdown(f"""
        <div class="sidebar-stat">
            <div class="sidebar-stat-label">ROI Improvement</div>
            <div class="sidebar-stat-value" style="color:#14b8a6;">{round(improvement,1)}%</div>
        </div>""", unsafe_allow_html=True)
    with sidebar_time_placeholder.container():
        st.markdown(f"""
        <div class="sidebar-stat">
            <div class="sidebar-stat-label">Processing Time</div>
            <div class="sidebar-stat-value" style="color:#94a3b8;">{wall_time}s</div>
        </div>""", unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center;padding:80px 24px;">
        <div style="font-size:4rem;margin-bottom:20px;">🛡️</div>
        <div style="font-size:1.5rem;font-weight:800;color:#f1f5f9;margin-bottom:10px;">
            Ready for Deployment
        </div>
        <div style="font-size:0.95rem;color:#475569;max-width:460px;margin:0 auto;line-height:1.6;">
            Upload an invoice, HR document, or meeting transcript above to activate
            the <strong style="color:#14b8a6;">7-agent autonomous pipeline</strong>.
        </div>
        <div style="margin-top:32px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
            <div style="background:rgba(20,184,166,0.10);border:1px solid rgba(20,184,166,0.25);
                border-radius:12px;padding:16px 22px;min-width:140px;">
                <div style="font-size:1.5rem;margin-bottom:6px;">🤖</div>
                <div style="font-size:0.75rem;font-weight:700;color:#14b8a6;letter-spacing:0.5px;">7 Agents</div>
                <div style="font-size:0.70rem;color:#475569;margin-top:2px;">Autonomous</div>
            </div>
            <div style="background:rgba(6,182,212,0.10);border:1px solid rgba(6,182,212,0.25);
                border-radius:12px;padding:16px 22px;min-width:140px;">
                <div style="font-size:1.5rem;margin-bottom:6px;">🧠</div>
                <div style="font-size:0.75rem;font-weight:700;color:#06b6d4;letter-spacing:0.5px;">LangSmith</div>
                <div style="font-size:0.70rem;color:#475569;margin-top:2px;">Full Tracing</div>
            </div>
            <div style="background:rgba(167,139,250,0.10);border:1px solid rgba(167,139,250,0.25);
                border-radius:12px;padding:16px 22px;min-width:140px;">
                <div style="font-size:1.5rem;margin-bottom:6px;">🏥</div>
                <div style="font-size:0.75rem;font-weight:700;color:#a78bfa;letter-spacing:0.5px;">Self-Healing</div>
                <div style="font-size:0.70rem;color:#475569;margin-top:2px;">Auto-correction</div>
            </div>
            <div style="background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.25);
                border-radius:12px;padding:16px 22px;min-width:140px;">
                <div style="font-size:1.5rem;margin-bottom:6px;">✋</div>
                <div style="font-size:0.75rem;font-weight:700;color:#f59e0b;letter-spacing:0.5px;">HITL Gate</div>
                <div style="font-size:0.70rem;color:#475569;margin-top:2px;">Human-in-Loop</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)