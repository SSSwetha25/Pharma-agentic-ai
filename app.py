import streamlit as st
import pandas as pd
from master_agent import run_master_agent
from report.report_generator import generate_pdf_report

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="PharmIntel — Strategic Intelligence Platform",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>+</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Global CSS ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* ─── Reset & Base ─────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #07090f;
        color: #d4dae8;
    }

    /* Thin, subtle scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #1e2535; border-radius: 3px; }

    /* ─── Top Nav Bar ───────────────────────────────────────────── */
    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 0rem;
        border-bottom: 1px solid #141926;
        margin-bottom: 2.5rem;
    }
    .topbar-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-mark {
        width: 34px;
        height: 34px;
        background: #1456d4;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .brand-plus {
        font-size: 1.5rem;
        font-weight: 300;
        color: #ffffff;
        line-height: 1;
        margin-top: -1px;
    }
    .brand-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #eef0f5;
        letter-spacing: -0.01em;
    }
    .brand-division {
        font-size: 0.7rem;
        font-weight: 500;
        color: #5a6482;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 1px;
    }
    .topbar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #0c1120;
        border: 1px solid #1b2540;
        border-radius: 6px;
        padding: 6px 14px;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background: #2fcf78;
        border-radius: 50%;
        box-shadow: 0 0 6px #2fcf78;
        animation: pulse 2.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .status-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #2fcf78;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .topbar-meta {
        font-size: 0.75rem;
        color: #3d4a65;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* ─── Page Title Block ─────────────────────────────────────── */
    .page-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #eef0f5;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin: 0;
    }
    .page-subtitle {
        font-size: 0.95rem;
        font-weight: 400;
        color: #5a6482;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        max-width: 680px;
        line-height: 1.6;
    }

    /* ─── Sidebar ───────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #050710;
        border-right: 1px solid #101525;
    }
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 1.25rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid #101525;
    }
    .sidebar-logo-mark {
        width: 28px;
        height: 28px;
        background: #1456d4;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 300;
        color: #fff;
        line-height: 1;
    }
    .sidebar-logo-text {
        font-size: 1rem;
        font-weight: 600;
        color: #c8cfe0;
    }
    .sidebar-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #3d4a65;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.75rem;
        margin-top: 1.5rem;
    }
    .sidebar-desc {
        font-size: 0.82rem;
        color: #5a6482;
        line-height: 1.6;
    }
    .sample-query {
        background: #0c1120;
        border: 1px solid #151e35;
        border-left: 3px solid #1456d4;
        border-radius: 0 6px 6px 0;
        padding: 10px 12px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .sample-query:hover { background: #101828; }
    .sq-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #5882e0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .sq-text {
        font-size: 0.78rem;
        color: #8a94b0;
        line-height: 1.45;
        font-style: italic;
    }

    /* ─── Query Panel ───────────────────────────────────────────── */
    .panel-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #3d4a65;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.6rem;
    }

    /* ─── Execute Button ────────────────────────────────────────── */
    div.stButton > button[kind="primary"] {
        background: #1456d4 !important;
        border: none !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em !important;
        padding: 0.65rem 1.5rem !important;
        transition: background 0.2s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 2px 12px rgba(20, 86, 212, 0.3) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #1a66f5 !important;
        box-shadow: 0 4px 18px rgba(20, 86, 212, 0.45) !important;
    }
    div.stButton > button[kind="primary"]:active {
        background: #1148b8 !important;
    }

    /* ─── Download Button ───────────────────────────────────────── */
    div.stDownloadButton > button {
        background: transparent !important;
        border: 1px solid #1e2d50 !important;
        border-radius: 6px !important;
        color: #8aa8e8 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:hover {
        background: #0e1830 !important;
        border-color: #2a4080 !important;
        color: #afc8f5 !important;
    }

    /* ─── Success / Spinner Overrides ───────────────────────────── */
    div[data-testid="stAlert"] {
        background: #071c12 !important;
        border: 1px solid #0d3320 !important;
        border-radius: 6px !important;
        color: #3ae880 !important;
    }

    /* ─── Pipeline Execution Bar ────────────────────────────────── */
    .pipeline-bar {
        display: flex;
        align-items: center;
        background: #0c1120;
        border: 1px solid #141926;
        border-radius: 8px;
        padding: 1.2rem 1.6rem;
        margin: 1.5rem 0 2rem 0;
        gap: 0;
    }
    .pipe-step {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }
    .pipe-node {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 1.5px solid #1e2d50;
        background: #0a1020;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .pipe-node.done {
        border-color: #1456d4;
        background: #0e1f45;
    }
    .pipe-node svg {
        width: 16px;
        height: 16px;
        stroke: #3d4a65;
        fill: none;
        stroke-width: 1.5;
        stroke-linecap: round;
        stroke-linejoin: round;
    }
    .pipe-node.done svg { stroke: #5882e0; }
    .pipe-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #3d4a65;
        text-align: center;
        white-space: nowrap;
    }
    .pipe-label.done { color: #8aa8e8; }
    .pipe-sub {
        font-size: 0.65rem;
        color: #272f45;
        text-align: center;
    }
    .pipe-sub.done { color: #3d5080; }
    .pipe-connector {
        flex: 0.5;
        height: 1px;
        background: linear-gradient(90deg, #1e2d50 0%, #1456d4 100%);
        margin-bottom: 28px;
    }

    /* ─── Console Log Window ────────────────────────────────────── */
    .console-wrap {
        background: #060912;
        border: 1px solid #141926;
        border-radius: 8px;
        overflow: hidden;
        margin: 1.5rem 0 2rem 0;
    }
    .console-titlebar {
        background: #0a0d18;
        border-bottom: 1px solid #141926;
        padding: 0.55rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .console-titlebar-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .console-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: #3d4a65;
    }
    .console-badge {
        font-size: 0.62rem;
        font-weight: 600;
        color: #2fcf78;
        background: #071c12;
        border: 1px solid #0d3320;
        border-radius: 4px;
        padding: 1px 7px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .console-body {
        padding: 1.1rem 1.3rem;
        max-height: 260px;
        overflow-y: auto;
    }
    .log-line {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        line-height: 1.6;
        margin-bottom: 4px;
    }
    .log-line .log-ts {
        color: #2a3550;
        margin-right: 10px;
        font-size: 0.72rem;
    }

    /* ─── Recommendation Card ───────────────────────────────────── */
    .rec-card {
        background: #0a1020;
        border: 1px solid #141f38;
        border-left: 3px solid #1456d4;
        border-radius: 0 8px 8px 0;
        padding: 1.4rem 1.6rem;
        margin: 1.5rem 0 2rem 0;
    }
    .rec-card-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: #5882e0;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.7rem;
    }
    .rec-card-text {
        font-size: 0.95rem;
        color: #b0bcda;
        line-height: 1.7;
        margin: 0;
    }

    /* ─── Section Heading ───────────────────────────────────────── */
    .section-heading {
        font-size: 0.7rem;
        font-weight: 700;
        color: #3d4a65;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #101525;
        margin-bottom: 1.25rem;
        margin-top: 2rem;
    }

    /* ─── Tabs ──────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid #141926;
        gap: 0;
        padding-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        color: #3d4a65;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 0.65rem 1.25rem;
        transition: color 0.15s ease;
        margin-bottom: -1px;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #8aa8e8; }
    .stTabs [aria-selected="true"] {
        color: #8aa8e8 !important;
        border-bottom: 2px solid #1456d4 !important;
        background: transparent !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ─── Metrics Row ───────────────────────────────────────────── */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1px;
        background: #141926;
        border: 1px solid #141926;
        border-radius: 8px;
        overflow: hidden;
        margin: 1.5rem 0;
    }
    .metric-cell {
        background: #0a0d18;
        padding: 1.2rem 1.4rem;
        transition: background 0.2s;
    }
    .metric-cell:hover { background: #0c1020; }
    .metric-cell-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #3d4a65;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    .metric-cell-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #d4dae8;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .metric-cell-sub {
        font-size: 0.7rem;
        color: #3d4a65;
        margin-top: 4px;
    }

    /* ─── Driver List ───────────────────────────────────────────── */
    .driver-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 0.75rem 0;
        border-bottom: 1px solid #101525;
    }
    .driver-item:last-child { border-bottom: none; }
    .driver-mark {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #1456d4;
        margin-top: 6px;
        flex-shrink: 0;
    }
    .driver-text {
        font-size: 0.84rem;
        color: #7888a8;
        line-height: 1.5;
    }

    /* ─── Document Export Card ──────────────────────────────────── */
    .export-card {
        background: #0a0d18;
        border: 1px solid #141926;
        border-radius: 8px;
        padding: 1.4rem 1.6rem;
        margin-top: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        flex-wrap: wrap;
    }
    .export-card-meta {
        flex: 1;
        min-width: 250px;
    }
    .export-card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #c8cfe0;
        margin-bottom: 0.4rem;
    }
    .export-card-desc {
        font-size: 0.8rem;
        color: #3d4a65;
        line-height: 1.5;
    }
    .export-tags {
        display: flex;
        gap: 8px;
        margin-top: 0.7rem;
        flex-wrap: wrap;
    }
    .export-tag {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #3d5080;
        border: 1px solid #1e2d50;
        border-radius: 4px;
        padding: 2px 8px;
    }
    .export-btn-wrap {
        min-width: 200px;
    }

    /* ─── Dataframe Overrides ───────────────────────────────────── */
    .stDataFrame, [data-testid="stDataFrame"] {
        border: 1px solid #141926 !important;
        border-radius: 8px !important;
        overflow: hidden;
    }

    /* ─── Divider ───────────────────────────────────────────────── */
    hr {
        border: none;
        border-top: 1px solid #101525 !important;
        margin: 2rem 0 !important;
    }

    /* ─── Text area ─────────────────────────────────────────────── */
    textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        background-color: #0a0d18 !important;
        border: 1px solid #1b2540 !important;
        border-radius: 6px !important;
        color: #c8cfe0 !important;
    }
    textarea:focus {
        border-color: #1456d4 !important;
        box-shadow: 0 0 0 2px rgba(20, 86, 212, 0.15) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════
# SVG icons (inline, no emoji)
# ══════════════════════════════════════════════════════════════════
SVG = {
    "orchestrator": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3"/><path d="M6 20v-1a6 6 0 0112 0v1"/><path d="M2 12h4M18 12h4"/></svg>',
    "clinical":     '<svg viewBox="0 0 24 24"><path d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2h-4"/><path d="M9 3a3 3 0 006 0"/><path d="M8 12h8M12 8v8"/></svg>',
    "patent":       '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/></svg>',
    "market":       '<svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "synthesis":    '<svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
    "size":         '<svg viewBox="0 0 24 24"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    "growth":       '<svg viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "competition":  '<svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>',
    "region":       '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>',
}


def pipe_step(icon_key: str, label: str, sub: str) -> str:
    return f"""
    <div class="pipe-step">
        <div class="pipe-node done">{SVG[icon_key]}</div>
        <div class="pipe-label done">{label}</div>
        <div class="pipe-sub done">{sub}</div>
    </div>"""


def pipe_connector() -> str:
    return '<div class="pipe-connector"></div>'


def log_color(line: str) -> str:
    line_lower = line.lower()
    if "master orchestrator" in line_lower:
        return "#5882e0"
    elif "clinical" in line_lower:
        return "#4db8a0"
    elif "patent" in line_lower:
        return "#9b7ce0"
    elif "market" in line_lower:
        return "#d4a443"
    elif "compil" in line_lower or "success" in line_lower or "assembl" in line_lower:
        return "#2fcf78"
    return "#5a6a88"


def format_log_line(idx: int, line: str) -> str:
    ts = f"[{idx:02d}]"
    escaped = line.replace("<", "&lt;").replace(">", "&gt;")
    color = log_color(line)
    return (
        f'<div class="log-line">'
        f'<span class="log-ts">{ts}</span>'
        f'<span style="color:{color};">{escaped}</span>'
        f'</div>'
    )


def metric_cell(label: str, value: str, sub: str, icon_svg: str) -> str:
    return f"""
    <div class="metric-cell">
        <div class="metric-cell-label">{label}</div>
        <div class="metric-cell-value">{value}</div>
        <div class="metric-cell-sub">{sub}</div>
    </div>"""


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-mark">+</div>
            <span class="sidebar-logo-text">PharmIntel</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sidebar-desc">Multi-agent decision support platform for early-stage pharmaceutical '
        'opportunity analysis. Coordinates autonomous agents across clinical, IP, and commercial domains '
        'to deliver synthesized strategic briefs.</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">Analysis Settings</div>', unsafe_allow_html=True)
    st.radio("FTO Detail Level", ["Executive Summary", "Full Patent Claims"], index=0, key="nav_detail")
    st.selectbox("Mode", ["Standard Analysis", "Accelerated"], index=0)

    st.markdown('<div class="sidebar-section-label">Reference Queries</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sample-query">
            <div class="sq-label">Oncology — US</div>
            <div class="sq-text">Identify oncology small-molecule opportunities with low patent risk in the US over the next 5 years.</div>
        </div>
        <div class="sample-query">
            <div class="sq-label">Metabolic — Europe</div>
            <div class="sq-text">Evaluate metabolic diabetes opportunities for novel peptide formulations in EU.</div>
        </div>
        <div class="sample-query">
            <div class="sq-label">Neurology — Japan</div>
            <div class="sq-text">Identify neurology and Alzheimer's compounds with FTO clearance in Japan.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════════════════════════════
from datetime import datetime
_now = datetime.now().strftime("%Y-%m-%d  %H:%M UTC+5:30")

st.markdown(
    f"""
    <div class="topbar">
        <div class="topbar-brand">
            <div class="brand-mark"><span class="brand-plus">+</span></div>
            <div>
                <div class="brand-name">PharmIntel</div>
                <div class="brand-division">Strategic Intelligence Platform</div>
            </div>
        </div>
        <div class="topbar-status">
            <div class="status-dot"></div>
            <span class="status-label">All Systems Operational</span>
        </div>
        <div class="topbar-meta">{_now}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════
# PAGE TITLE
# ══════════════════════════════════════════════════════════════════
st.markdown(
    """
    <h1 class="page-title">Drug Opportunity Intelligence</h1>
    <p class="page-subtitle">
        Submit a research query to initiate coordinated analysis across clinical trial registries,
        patent databases, and commercial market intelligence sources.
    </p>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════
# QUERY INPUT
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="panel-label">Research Query</div>', unsafe_allow_html=True)

user_query = st.text_area(
    label="query_input",
    label_visibility="collapsed",
    value="Identify oncology small-molecule opportunities with low patent risk in the US and EU over the next 5 years.",
    height=100,
    placeholder="Describe the therapeutic area, compound class, target geography, and risk parameters...",
)

col_btn, col_hint = st.columns([2, 5])
with col_btn:
    analyze_btn = st.button("Run Analysis", use_container_width=True, type="primary")
with col_hint:
    st.markdown(
        '<p style="margin-top:10px; font-size:0.8rem; color:#3d4a65;">'
        "The orchestrator will sequentially dispatch the Clinical, Patent, and Market agents, "
        "then compile a synthesized strategic brief."
        "</p>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════
if analyze_btn and user_query:

    with st.spinner("Running coordinated analysis..."):
        results = run_master_agent(user_query)

    st.success("Analysis complete. Strategic brief assembled.")

    # ── Pipeline Execution Bar ──────────────────────────────────
    st.markdown('<div class="section-heading">Execution Pipeline</div>', unsafe_allow_html=True)
    pipeline_html = (
        '<div class="pipeline-bar">'
        + pipe_step("orchestrator", "Orchestrator", "Init")
        + pipe_connector()
        + pipe_step("clinical", "Clinical Agent", "Trial Scoping")
        + pipe_connector()
        + pipe_step("patent", "Patent Agent", "FTO Analysis")
        + pipe_connector()
        + pipe_step("market", "Market Agent", "Growth Forecast")
        + pipe_connector()
        + pipe_step("synthesis", "Synthesis", "Brief Compiled")
        + '</div>'
    )
    st.markdown(pipeline_html, unsafe_allow_html=True)

    # ── Console Trace ───────────────────────────────────────────
    st.markdown('<div class="section-heading">Agent Execution Log</div>', unsafe_allow_html=True)
    log_lines_html = "".join(
        format_log_line(i + 1, line)
        for i, line in enumerate(results.get("trace", []))
    )
    st.markdown(
        f"""
        <div class="console-wrap">
            <div class="console-titlebar">
                <div class="console-titlebar-left">
                    <span class="console-title">orchestrator.log</span>
                    <span class="console-badge">Completed</span>
                </div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#2a3550;">
                    {len(results.get("trace", []))} events
                </span>
            </div>
            <div class="console-body">{log_lines_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Strategic Recommendation ─────────────────────────────────
    st.markdown('<div class="section-heading">Strategic Recommendation</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="rec-card">
            <div class="rec-card-label">Consolidated Analysis</div>
            <p class="rec-card-text">{results["conclusion"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Intelligence Tabs ────────────────────────────────────────
    st.markdown('<div class="section-heading">Segment Intelligence</div>', unsafe_allow_html=True)
    tab_clinical, tab_patent, tab_market = st.tabs(
        ["Clinical Trials", "Patent & IP Landscape", "Market & Commercial Sizing"]
    )

    # — Tab 1: Clinical ——
    with tab_clinical:
        st.markdown('<div class="section-heading">Registry Summary</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.88rem;color:#7888a8;line-height:1.7;">{results["clinical"]["summary"]}</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-heading">Representative Trials</div>', unsafe_allow_html=True)
        trials_df = results["clinical"]["trials"].copy()

        # Clean status indicators using text badges, no emoji
        if "Status" in trials_df.columns:
            trials_df["Status"] = trials_df["Status"].map(
                lambda x: f"[ACTIVE] {x}" if "Recruiting" in x
                else f"[DONE] {x}" if "Completed" in x
                else f"[HOLD] {x}"
            )
        if "Phase" in trials_df.columns:
            trials_df["Phase"] = trials_df["Phase"].map(
                lambda x: f"III — {x.replace('Phase III', '').strip()}" if "Phase III" in x
                else f"II — {x.replace('Phase II','').strip()}" if "Phase II" in x
                else x
            )

        st.dataframe(trials_df, use_container_width=True, hide_index=True)

    # — Tab 2: Patent ——
    with tab_patent:
        st.markdown('<div class="section-heading">IP Assessment</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.88rem;color:#7888a8;line-height:1.7;">{results["patent"]["summary"]}</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-heading">FTO Landscape</div>', unsafe_allow_html=True)
        patents_df = results["patent"]["patents"].copy()

        if "Risk Level" in patents_df.columns:
            patents_df["Risk Level"] = patents_df["Risk Level"].map(
                lambda x: f"HIGH — {x.replace('High','').strip()}" if "High" in x
                else f"MOD — {x.replace('Moderate','').replace('Medium','').strip()}" if "Moderate" in x or "Medium" in x
                else f"LOW — {x.replace('Low','').replace('(Expired)','').strip()}"
            )
        if "Status" in patents_df.columns:
            patents_df["Status"] = patents_df["Status"].map(
                lambda x: "Active" if "Active" in x else "Expired"
            )

        st.dataframe(patents_df, use_container_width=True, hide_index=True)

    # — Tab 3: Market ——
    with tab_market:
        st.markdown('<div class="section-heading">Commercial Overview</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.88rem;color:#7888a8;line-height:1.7;">{results["market"]["summary"]}</p>',
            unsafe_allow_html=True,
        )

        market_data = results["market"]["market_data"]
        geography = results.get("patent", {}).get("geography", "Global")

        # Metrics row
        metrics_html = (
            '<div class="metrics-row">'
            + metric_cell("Estimated Market Size", market_data["estimated_size"], "Current valuation", SVG["size"])
            + metric_cell("Growth Rate (CAGR)", market_data["cagr"], "5-year projection", SVG["growth"])
            + metric_cell("Competition Density", market_data["competition_level"], "Market participants", SVG["competition"])
            + metric_cell("Primary Region", geography, "Analysis scope", SVG["region"])
            + '</div>'
        )
        st.markdown(metrics_html, unsafe_allow_html=True)

        # Chart + Drivers
        p_col1, p_col2 = st.columns([3, 2])
        with p_col1:
            st.markdown(
                '<div class="section-heading">5-Year Revenue Forecast (USD Million)</div>',
                unsafe_allow_html=True,
            )
            proj_df = pd.DataFrame(market_data["projections"]).set_index("Year")
            st.line_chart(proj_df, height=220)

        with p_col2:
            st.markdown(
                '<div class="section-heading">Key Commercial Drivers</div>',
                unsafe_allow_html=True,
            )
            drivers_html = "".join(
                f'<div class="driver-item">'
                f'<div class="driver-mark"></div>'
                f'<span class="driver-text">{d}</span>'
                f'</div>'
                for d in market_data["key_drivers"]
            )
            st.markdown(drivers_html, unsafe_allow_html=True)

    st.divider()

    # ── Export Card ──────────────────────────────────────────────
    pdf_path = generate_pdf_report(results, user_query)
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    st.markdown(
        """
        <div class="export-card">
            <div class="export-card-meta">
                <div class="export-card-title">Executive Strategy Report</div>
                <div class="export-card-desc">
                    A formatted intelligence brief suitable for distribution to executive leadership,
                    strategy committees, or external partners.
                </div>
                <div class="export-tags">
                    <span class="export-tag">PDF</span>
                    <span class="export-tag">A4 Format</span>
                    <span class="export-tag">Confidential</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        label="Download Report (PDF)",
        data=pdf_data,
        file_name="pharmintel_strategy_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
