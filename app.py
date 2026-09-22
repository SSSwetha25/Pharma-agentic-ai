import html
from datetime import datetime

import pandas as pd
import streamlit as st

import master_agent
from master_agent import run_master_agent
from report.report_generator import generate_pdf_report


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="PharmIntel",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --ink: #172033;
        --muted: #667085;
        --subtle: #98A2B3;
        --line: #E4E7EC;
        --panel: #FFFFFF;
        --canvas: #F7F8FA;
        --navy: #17324D;
        --blue: #2F6FED;
        --teal: #168F87;
        --green: #198754;
        --amber: #B7791F;
        --red: #C24141;
    }

    html, body, [class*="css"] {
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: var(--canvas);
        color: var(--ink);
    }

    .main .block-container {
        max-width: 1440px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        color: var(--ink) !important;
        letter-spacing: -0.02em;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding-bottom: 1.15rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.4rem;
    }

    .brand-mark {
        width: 32px;
        height: 32px;
        border: 1px solid #C8D5E3;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--navy);
        font-size: 20px;
        font-weight: 500;
        background: #F8FAFC;
    }

    .brand-name {
        color: var(--ink);
        font-size: 1.02rem;
        font-weight: 700;
    }

    .brand-sub {
        color: var(--subtle);
        font-size: 0.68rem;
        margin-top: 2px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .sidebar-label {
        color: #475467;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 1.4rem 0 0.55rem;
    }

    .sidebar-copy {
        color: var(--muted);
        font-size: 0.79rem;
        line-height: 1.55;
    }

    .sample {
        padding: 0.65rem 0.75rem;
        border: 1px solid var(--line);
        border-radius: 7px;
        margin-bottom: 0.5rem;
        background: #FCFCFD;
    }

    .sample-title {
        font-size: 0.7rem;
        color: #475467;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }

    .sample-text {
        font-size: 0.74rem;
        color: var(--muted);
        line-height: 1.45;
    }

    .topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 2.1rem;
    }

    .eyebrow {
        color: #667085;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }

    .date-label {
        color: var(--subtle);
        font-size: 0.72rem;
        font-family: "IBM Plex Mono", monospace;
    }

    .hero-title {
        font-size: 2.15rem;
        line-height: 1.15;
        font-weight: 700;
        margin: 0;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 0.94rem;
        line-height: 1.65;
        max-width: 760px;
        margin: 0.65rem 0 1.65rem;
    }

    .query-label {
        color: #344054;
        font-size: 0.73rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    textarea {
        background: #FFFFFF !important;
        color: var(--ink) !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 8px !important;
        font-size: 0.91rem !important;
        line-height: 1.55 !important;
    }

    textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 2px rgba(47, 111, 237, 0.10) !important;
    }

    div.stButton > button[kind="primary"] {
        background: var(--navy) !important;
        border: 1px solid var(--navy) !important;
        color: white !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        min-height: 42px;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #214865 !important;
        border-color: #214865 !important;
    }

    div.stDownloadButton > button {
        background: white !important;
        color: var(--navy) !important;
        border: 1px solid #C8D2DC !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
    }

    .section-title {
        color: #344054;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 1.9rem 0 0.8rem;
        padding-bottom: 0.55rem;
        border-bottom: 1px solid var(--line);
    }


    /* Native Streamlit metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        padding: 0.9rem 1rem !important;
        min-height: 92px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        color: #667085 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: var(--ink) !important;
    }

    [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] div {
        color: #667085 !important;
    }

    /* Light, readable tab labels */
    button[data-baseweb="tab"],
    button[data-baseweb="tab"] p {
        color: #667085 !important;
        font-weight: 500 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: var(--navy) !important;
        font-weight: 650 !important;
    }

    /* Stable light-theme clinical table */
    .trial-table-wrap {
        overflow-x: auto;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #FFFFFF;
        margin: 0.7rem 0 0.9rem;
    }

    .trial-table {
        width: 100%;
        min-width: 980px;
        border-collapse: collapse;
        font-size: 0.78rem;
        color: var(--ink);
    }

    .trial-table th {
        background: #F8FAFC;
        color: #475467;
        font-weight: 650;
        text-align: left;
        padding: 0.7rem 0.65rem;
        border-bottom: 1px solid var(--line);
        white-space: nowrap;
    }

    .trial-table td {
        color: var(--ink);
        background: #FFFFFF;
        padding: 0.72rem 0.65rem;
        border-bottom: 1px solid #EEF1F4;
        vertical-align: top;
        line-height: 1.35;
    }

    .trial-table tr:last-child td {
        border-bottom: none;
    }

    .trial-id {
        color: var(--navy);
        font-family: "IBM Plex Mono", monospace;
        font-weight: 600;
        white-space: nowrap;
    }

    .trial-title {
        min-width: 360px;
    }

    .trial-status {
        color: #176B4D;
        font-weight: 600;
        white-space: nowrap;
    }

    .trial-phase {
        white-space: nowrap;
        font-weight: 600;
    }


    .coverage-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.65rem;
        margin: 0.75rem 0 1.1rem;
    }

    .coverage-card {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
    }

    .coverage-head {
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
        align-items: center;
    }

    .coverage-name {
        color: #344054;
        font-size: 0.76rem;
        font-weight: 650;
    }

    .coverage-detail {
        color: #98A2B3;
        font-size: 0.68rem;
        line-height: 1.4;
        margin-top: 0.28rem;
    }

    .scope-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.6rem 0 1.15rem;
    }

    .scope-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.32rem;
        padding: 0.28rem 0.55rem;
        border: 1px solid #DCE3EA;
        border-radius: 999px;
        background: #FFFFFF;
        color: #475467;
        font-size: 0.69rem;
    }

    .scope-chip strong {
        color: #344054;
        font-weight: 650;
    }

    .assessment-kicker {
        color: #667085;
        font-size: 0.69rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .hero-rule {
        height: 1px;
        background: var(--line);
        margin: 0.1rem 0 1.2rem;
    }

    .query-meta {
        color: #98A2B3;
        font-size: 0.69rem;
        margin-top: 0.45rem;
    }

    .empty-state {
        text-align: center;
        border: 1px dashed #D0D5DD;
        border-radius: 8px;
        padding: 1.25rem;
        background: #FCFCFD;
    }

    .empty-state-title {
        color: #344054;
        font-size: 0.82rem;
        font-weight: 650;
    }

    .empty-state-copy {
        color: #667085;
        font-size: 0.74rem;
        line-height: 1.5;
        margin-top: 0.25rem;
    }

    @media (max-width: 900px) {
        .coverage-grid {
            grid-template-columns: 1fr;
        }
    }

    .status-strip.status-warning {
        background: #FFFAEB;
        border-color: #F3D28A;
        color: #8A5A00;
    }

    .status-dot-warning {
        background: #C58A00 !important;
    }

    .status-strip {
        display: flex;
        gap: 0.55rem;
        align-items: center;
        padding: 0.7rem 0.85rem;
        border: 1px solid #DCE5EE;
        border-radius: 7px;
        background: #F8FAFC;
        color: #475467;
        font-size: 0.78rem;
        margin-bottom: 1.1rem;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        flex-shrink: 0;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0.8rem 0 1.25rem;
    }

    .metric {
        background: white;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem 1.05rem;
        min-height: 98px;
    }

    .metric-label {
        color: #667085;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        color: var(--ink);
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 0.48rem;
        line-height: 1.1;
    }

    .metric-note {
        color: var(--subtle);
        font-size: 0.69rem;
        margin-top: 0.3rem;
    }

    .recommendation {
        background: white;
        border: 1px solid var(--line);
        border-left: 4px solid var(--navy);
        border-radius: 0 8px 8px 0;
        padding: 1.15rem 1.3rem;
        margin-bottom: 1.2rem;
    }

    .recommendation-title {
        color: #344054;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.55rem;
    }

    .recommendation-text {
        color: #475467;
        font-size: 0.9rem;
        line-height: 1.7;
        margin: 0;
    }

    .source-box {
        background: #FCFCFD;
        border: 1px solid var(--line);
        border-radius: 7px;
        padding: 0.75rem 0.9rem;
        margin-top: 0.8rem;
    }

    .source-name {
        color: #344054;
        font-size: 0.76rem;
        font-weight: 600;
    }

    .source-meta {
        color: var(--subtle);
        font-size: 0.68rem;
        margin-top: 0.2rem;
        line-height: 1.5;
    }

    .notice {
        padding: 0.85rem 1rem;
        border: 1px solid #E4E7EC;
        background: #F9FAFB;
        border-radius: 7px;
        color: #667085;
        font-size: 0.8rem;
        line-height: 1.55;
    }

    .notice-warning {
        border-color: #E8D8B8;
        background: #FFFBF2;
        color: #7A5A1A;
    }

    .notice-info {
        border-color: #CFE0F5;
        background: #F6FAFF;
        color: #315B87;
    }

    .evidence-row {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1rem;
        align-items: start;
        border-bottom: 1px solid var(--line);
        padding: 0.8rem 0;
    }

    .evidence-title {
        color: #344054;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .evidence-detail {
        color: #667085;
        font-size: 0.74rem;
        line-height: 1.5;
        margin-top: 0.18rem;
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.48rem;
        border-radius: 999px;
        font-size: 0.64rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }

    .badge-green { background: #ECFDF3; color: #16794C; }
    .badge-amber { background: #FFFAEB; color: #946200; }
    .badge-red { background: #FEF3F2; color: #B42318; }
    .badge-gray { background: #F2F4F7; color: #667085; }
    .badge-blue { background: #EFF6FF; color: #2459A6; }

    .footnote {
        color: #98A2B3;
        font-size: 0.68rem;
        line-height: 1.5;
        margin-top: 0.7rem;
    }

    .trace {
        background: #172033;
        border-radius: 7px;
        padding: 0.8rem 1rem;
        max-height: 280px;
        overflow-y: auto;
    }

    .trace-line {
        color: #D0D5DD;
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.68rem;
        line-height: 1.7;
        padding: 0.08rem 0;
    }

    .footer {
        border-top: 1px solid var(--line);
        margin-top: 2.5rem;
        padding-top: 1rem;
        color: #98A2B3;
        font-size: 0.68rem;
        line-height: 1.5;
    }

    @media (max-width: 900px) {
        .metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .hero-title {
            font-size: 1.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Utility functions
# ============================================================

def esc(value) -> str:
    return html.escape(str(value)) if value is not None else ""


def badge(text: str, kind: str = "gray") -> str:
    return f'<span class="badge badge-{kind}">{esc(text)}</span>'


def risk_badge(risk: str) -> str:
    value = str(risk or "Unknown")
    low = value.lower()

    if "high" in low:
        return badge(value, "red")
    if "moderate" in low or "medium" in low:
        return badge(value, "amber")
    if "low" in low:
        return badge(value, "green")

    return badge(value, "gray")


def status_badge(status: str) -> str:
    value = str(status or "Unknown")
    low = value.lower()

    if "recruiting" in low:
        return badge(value, "green")
    if "active" in low:
        return badge(value, "blue")
    if "completed" in low:
        return badge(value, "gray")
    if "not yet" in low:
        return badge(value, "amber")

    return badge(value, "gray")


def format_phase(phases) -> str:
    if isinstance(phases, list):
        return ", ".join(phases) if phases else "Not reported"
    if phases is None:
        return "Not reported"
    return str(phases)


def render_source(source: dict, label: str = "Source") -> None:
    if not source:
        st.markdown(
            '<div class="source-box"><div class="source-name">'
            f'{esc(label)}: unavailable</div></div>',
            unsafe_allow_html=True,
        )
        return

    if isinstance(source, str):
        name = source
        url = None
        retrieved = None
    else:
        name = source.get("name", "Source")
        url = source.get("url")
        retrieved = source.get("retrieved_at")

    link = ""
    if url:
        link = (
            f'<div class="source-meta">'
            f'<a href="{esc(url)}" target="_blank">Open source</a>'
            f'</div>'
        )

    retrieved_text = ""
    if retrieved:
        retrieved_text = (
            f'<div class="source-meta">Retrieved: {esc(retrieved)}</div>'
        )

    st.markdown(
        f"""
        <div class="source-box">
            <div class="source-name">{esc(label)} · {esc(name)}</div>
            {retrieved_text}
            {link}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "") -> str:
    return f"""
    <div class="metric">
        <div class="metric-label">{esc(label)}</div>
        <div class="metric-value">{esc(value)}</div>
        <div class="metric-note">{esc(note)}</div>
    </div>
    """


def run_analysis_with_retry(user_query: str) -> dict:
    """Run the orchestrator and retry once when ClinicalTrials.gov times out."""
    results = run_master_agent(user_query)
    clinical = results.get("clinical", {})
    error = str(clinical.get("error", ""))

    timeout_markers = (
        "timed out",
        "timeout",
        "request timed out",
    )

    if error and any(marker in error.lower() for marker in timeout_markers):
        retry_results = run_master_agent(user_query)
        retry_clinical = retry_results.get("clinical", {})
        retry_error = str(retry_clinical.get("error", ""))

        if retry_clinical.get("trials") or not retry_error:
            return retry_results

        trace = list(results.get("trace", []))
        trace.append(
            "[Clinical Agent]: Initial registry request timed out; retry also failed."
        )
        results["trace"] = trace

    return results


def get_clinical_summary(clinical: dict) -> str:
    trials = clinical.get("trials", [])

    if clinical.get("error"):
        return clinical["error"]

    parsed = clinical.get("parsed_query", {})
    count = clinical.get("trial_count", len(trials))

    parts = [f"{count} matching clinical trial(s)"]

    if parsed.get("condition"):
        parts.append(f"for {parsed['condition']}")

    if parsed.get("intervention"):
        parts.append(f"involving {parsed['intervention']}")

    if parsed.get("phase"):
        parts.append(parsed["phase"])

    if parsed.get("status"):
        parts.append(parsed["status"].replace("_", " ").lower())

    if parsed.get("location"):
        parts.append(f"in {parsed['location']}")

    return " ".join(parts) + "."


def render_trials_table(trials_df: pd.DataFrame) -> str:
    """Render a predictable light-theme table for registry results."""
    if trials_df.empty:
        return ""

    columns = [
        ("NCT ID", "NCT ID"),
        ("Title", "Trial"),
        ("Status", "Status"),
        ("Phase", "Phase"),
        ("Enrollment", "Enrollment"),
        ("Sponsor", "Sponsor"),
        ("Start", "Start"),
    ]

    header = "".join(f"<th>{esc(label)}</th>" for _, label in columns)
    rows = []

    for _, row in trials_df.iterrows():
        cells = []

        for key, _ in columns:
            value = row.get(key, "—")
            if pd.isna(value) or value in ("", None):
                value = "—"

            value = esc(str(value))

            if key == "NCT ID":
                raw_id = str(row.get("NCT ID", "")).strip()
                if raw_id and raw_id != "—":
                    href = f"https://clinicaltrials.gov/study/{esc(raw_id)}"
                    value = (
                        f'<a class="trial-id" href="{href}" target="_blank">'
                        f'{value}</a>'
                    )
                else:
                    value = f'<span class="trial-id">{value}</span>'
            elif key == "Title":
                value = f'<div class="trial-title">{value}</div>'
            elif key == "Status":
                value = f'<span class="trial-status">{value}</span>'
            elif key == "Phase":
                value = f'<span class="trial-phase">{value}</span>'

            cells.append(f"<td>{value}</td>")

        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        '<div class="trial-table-wrap">'
        '<table class="trial-table">'
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def normalize_trials(trials) -> pd.DataFrame:
    if not trials:
        return pd.DataFrame()

    rows = []

    for trial in trials:
        rows.append(
            {
                "NCT ID": trial.get("nct_id", ""),
                "Title": trial.get("title", ""),
                "Status": trial.get("status", "Not reported"),
                "Phase": format_phase(trial.get("phase")),
                "Enrollment": trial.get("enrollment", "Not reported"),
                "Sponsor": trial.get("sponsor", "Not reported"),
                "Start": trial.get("start_date", "Not reported"),
            }
        )

    return pd.DataFrame(rows)


def normalize_patents(patents) -> pd.DataFrame:
    if patents is None:
        return pd.DataFrame()

    if not isinstance(patents, pd.DataFrame):
        try:
            patents = pd.DataFrame(patents)
        except Exception:
            return pd.DataFrame()

    if patents.empty:
        return patents

    preferred = [
        "Patent ID",
        "Title",
        "Assignee",
        "Status",
        "Relevance Score",
        "Risk Level",
        "Publication Date",
        "Source URL",
    ]

    columns = [
        col for col in preferred
        if col in patents.columns
    ]

    return patents[columns].copy()


# ============================================================
# Header
# ============================================================

now = datetime.now().strftime("%d %b %Y · %H:%M")

nav_left, nav_mid, nav_right = st.columns([2.2, 3.6, 2.2])

with nav_left:
    st.markdown(
        """
        <div style="padding-top:0.15rem;">
            <div style="font-size:1.05rem;font-weight:750;color:#172033;">PharmIntel</div>
            <div style="font-size:0.64rem;color:#98A2B3;letter-spacing:0.06em;text-transform:uppercase;">
                Pharmaceutical intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_mid:
    st.markdown(
        """
        <div style="text-align:center;padding-top:0.35rem;color:#667085;font-size:0.73rem;">
            Research workspace&nbsp;&nbsp; · &nbsp;&nbsp;Evidence-led opportunity analysis
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_right:
    st.markdown(
        f"""
        <div style="text-align:right;padding-top:0.35rem;color:#98A2B3;font-size:0.68rem;">
            {now}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="hero-rule"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">Research workspace</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h1 class="hero-title">Pharmaceutical Opportunity Intelligence</h1>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p class="hero-copy">
        Turn a research question into structured clinical, commercial and
        intellectual-property evidence. Reported facts and derived analysis
        are kept distinguishable throughout the workspace.
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Query
# ============================================================

st.markdown(
    '<div class="query-label">Research question</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Session state initialization
# ------------------------------------------------------------
if "user_query" not in st.session_state:
    st.session_state["user_query"] = (
        "Find recruiting Phase 3 obesity trials involving semaglutide in the US"
    )

if "last_results" not in st.session_state:
    st.session_state["last_results"] = None

if "last_query" not in st.session_state:
    st.session_state["last_query"] = ""

user_query = st.text_area(
    "Research question",
    value=st.session_state["user_query"],
    key="query_input",
    height=96,
    label_visibility="collapsed",
    placeholder=(
        "Example: Find recruiting Phase 3 obesity trials "
        "involving semaglutide in the US"
    ),
)

analyze_col, help_col = st.columns([1.25, 4.75])

with analyze_col:
    analyze_btn = st.button(
        "Run analysis",
        use_container_width=True,
        type="primary",
    )

with help_col:
    st.markdown(
        """
        <div style="color:#667085;font-size:0.77rem;padding-top:0.72rem;">
        The analysis runs the available domain agents and consolidates
        their structured outputs into one research brief.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Analysis
# ============================================================

if analyze_btn:

    st.session_state["user_query"] = user_query

    if not user_query.strip():
        st.warning("Enter a research question first.")
        st.stop()

    with st.spinner("Running analysis..."):
        try:
            results = run_analysis_with_retry(
                user_query.strip()
            )
            st.session_state["last_results"] = results
            st.session_state["last_query"] = user_query.strip()
        
        except Exception as exc:
            st.error(
                "The analysis could not be completed."
            )
            st.exception(exc)
            st.stop()

    clinical = results.get("clinical", {})
    patent = results.get("patent", {})
    market = results.get("market", {})

    clinical_trials = clinical.get("trials", [])
    clinical_count = clinical.get(
        "trial_count",
        len(clinical_trials),
    )

    market_data = market.get(
        "market_data",
        {},
    )

    patent_risk = patent.get(
        "max_risk",
        "Unknown",
    )

    market_status = market.get(
        "status",
        "UNKNOWN",
    )

    # --------------------------------------------------------
    # Run status
    # --------------------------------------------------------

    clinical_error = bool(clinical.get("error"))
    patent_error = bool(patent.get("error"))
    domain_warning = clinical_error or patent_error

    clinical_available = bool(clinical_trials) and not clinical_error
    market_available = market_status != "UNAVAILABLE" and bool(market_data)
    patent_available = bool(normalize_patents(patent.get("patents")).shape[0])

    if domain_warning:
        status_html = """
        <div class="status-strip status-warning">
            <div class="status-dot status-dot-warning"></div>
            Analysis completed with domain warnings. Review source availability below.
        </div>
        """
    else:
        status_html = """
        <div class="status-strip">
            <div class="status-dot"></div>
            Analysis completed. Review the evidence by domain below.
        </div>
        """

    st.markdown(status_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Evidence coverage</div>',
        unsafe_allow_html=True,
    )

    coverage_cols = st.columns(3)

    coverage_data = [
        (
            "Clinical",
            "Available" if clinical_available else "Unavailable",
            "ClinicalTrials.gov",
            clinical_available,
        ),
        (
            "Market",
            "Available" if market_available else "Unavailable",
            "IQVIA / source-backed estimates",
            market_available,
        ),
        (
            "Patent",
            "Available" if patent_available else "Limited",
            "Preliminary IP evidence",
            patent_available,
        ),
    ]

    for col, (name, state, detail, available) in zip(
        coverage_cols,
        coverage_data,
    ):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"**{name}**"
                )
                if available:
                    st.success(state)
                else:
                    st.warning(state)
                st.caption(detail)

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Executive overview</div>',
        unsafe_allow_html=True,
    )

    parsed = clinical.get("parsed_query", {})

    indication = (
        parsed.get("condition")
        or clinical.get("category")
        or "Not specified"
    )

    intervention = (
        parsed.get("intervention")
        or "Not specified"
    )

    market_size = market_data.get(
        "estimated_size",
        "Unavailable",
    )

    cagr = market_data.get(
        "cagr",
        "Unavailable",
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Therapeutic area",
            indication.title()
            if indication != "Not specified"
            else indication,
            help="Parsed from the clinical query.",
        )

    with m2:
        st.metric(
            "Clinical matches",
            str(clinical_count) if not clinical.get("error") else "Unavailable",
            help="Validated ClinicalTrials.gov records. Unavailable means the registry request failed.",
        )

    with m3:
        st.metric(
            "Market size",
            market_size,
            help=f"Source year: {market_data.get('estimated_size_year', 'Not reported')}",
        )

    with m4:
        st.metric(
            "IP evidence status",
            patent_risk,
            help="Evidence availability only; this is not a legal freedom-to-operate opinion.",
        )

    scope_parts = []
    if indication != "Not specified":
        scope_parts.append(f'<span class="scope-chip"><strong>Area</strong> {esc(indication.title())}</span>')
    if intervention != "Not specified":
        scope_parts.append(f'<span class="scope-chip"><strong>Intervention</strong> {esc(intervention)}</span>')
    if parsed.get("phase"):
        scope_parts.append(f'<span class="scope-chip"><strong>Phase</strong> {esc(parsed["phase"])}</span>')
    if parsed.get("status"):
        scope_parts.append(f'<span class="scope-chip"><strong>Status</strong> {esc(parsed["status"])}</span>')
    if parsed.get("location"):
        scope_parts.append(f'<span class="scope-chip"><strong>Region</strong> {esc(parsed["location"])}</span>')

    if scope_parts:
        st.markdown(
            '<div class="query-meta">Parsed research scope</div>'
            '<div class="scope-strip">'
            + "".join(scope_parts)
            + "</div>",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Opportunity score
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Opportunity assessment</div>',
        unsafe_allow_html=True,
    )

    opportunity_score = results.get("opportunity_score", {})
    overall_score = opportunity_score.get("overall_score")
    rating = opportunity_score.get("rating", "Unavailable")
    evidence_confidence = opportunity_score.get("evidence_confidence", {})
    confidence = evidence_confidence.get(
        "level",
        opportunity_score.get("confidence", "Unavailable"),
    )
    dimensions = opportunity_score.get("dimension_scores", {})

    if overall_score is None:
        st.markdown(
            """
            <div class="notice notice-warning">
            Opportunity scoring is currently unavailable because the scoring
            engine did not return a validated score.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        score_cols = st.columns(3)

        with score_cols[0]:
            st.metric(
                "Opportunity score",
                f"{overall_score} / 100",
                help="Normalized score from the available market, clinical, competition and IP evidence.",
            )

        with score_cols[1]:
            st.metric(
                "Assessment",
                str(rating),
                help="Interpretation of the normalized opportunity score.",
            )

        with score_cols[2]:
            st.metric(
                "Evidence confidence",
                str(confidence),
                help="Evidence confidence is separate from the opportunity score.",
            )

        dimension_labels = {
            "market": "Market potential",
            "clinical": "Clinical activity",
            "competition": "Competition",
            "ip": "IP evidence",
        }

        dimension_cols = st.columns(4)

        for col, key in zip(
            dimension_cols,
            ["market", "clinical", "competition", "ip"],
        ):
            dimension = dimensions.get(key, {})
            score = dimension.get("score")
            maximum = dimension.get("maximum")

            with col:
                if score is None:
                    st.metric(dimension_labels[key], "Unknown")
                    st.caption("Excluded from score denominator")
                else:
                    st.metric(
                        dimension_labels[key],
                        f"{score} / {maximum}",
                    )

        st.markdown(
            """
            <div class="footnote">
            The opportunity score is normalized over dimensions for which
            evidence is available. Missing evidence is not treated as zero;
            evidence confidence is reported separately.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Strategic assessment</div>',
        unsafe_allow_html=True,
    )

    recommendation = results.get(
        "conclusion",
        "No strategic conclusion was generated.",
    )

    with st.container(border=True):
        st.caption("CROSS-DOMAIN DECISION SIGNAL")
        st.markdown("### Assessment")
        st.write(recommendation)

        positive_signals = []
        constraints = []

        if clinical_available:
            positive_signals.append(
                f"{clinical_count} matching clinical trial(s)"
            )
        else:
            constraints.append("Clinical registry evidence unavailable")

        if market_available:
            if market_size != "Unavailable":
                positive_signals.append(
                    f"Market estimate: {market_size}"
                )
            if cagr != "Unavailable":
                positive_signals.append(
                    f"Reported growth range: {cagr}"
                )
        else:
            constraints.append("Market intelligence unavailable")

        if patent_available:
            positive_signals.append("Patent evidence retrieved")
        else:
            constraints.append("Patent/FTO evidence currently unavailable")

        signal_col, constraint_col = st.columns(2)

        with signal_col:
            st.markdown("**Positive signals**")
            if positive_signals:
                for item in positive_signals:
                    st.markdown(f"- {item}")
            else:
                st.caption("No positive evidence signals available.")

        with constraint_col:
            st.markdown("**Constraints**")
            if constraints:
                for item in constraints:
                    st.markdown(f"- {item}")
            else:
                st.caption("No domain constraints reported.")


    # --------------------------------------------------------
    # Intelligence tabs
    # --------------------------------------------------------

    tab_clinical, tab_market, tab_patent, tab_trace = st.tabs(
        [
            "Clinical evidence",
            "Market intelligence",
            "Patent landscape",
            "Run details",
        ]
    )

    # ========================================================
    # Clinical tab
    # ========================================================

    with tab_clinical:

        st.markdown(
            '<div class="section-title">Clinical development</div>',
            unsafe_allow_html=True,
        )

        st.write(
            get_clinical_summary(
                clinical
            )
        )

        parsed_items = []

        for label, key in [
            ("Condition", "condition"),
            ("Intervention", "intervention"),
            ("Phase", "phase"),
            ("Recruitment", "status"),
            ("Location", "location"),
        ]:
            value = parsed.get(key)

            if value:
                parsed_items.append(
                    f"**{label}:** {value}"
                )

        if parsed_items:
            st.markdown(
                " · ".join(parsed_items)
            )

        trials_df = normalize_trials(
            clinical_trials
        )

        if trials_df.empty:

            error = clinical.get(
                "error"
            )

            if error:
                st.error(error)
            else:
                st.markdown(
                    """
                    <div class="empty-state">
                        <div class="empty-state-title">No matching clinical trials</div>
                        <div class="empty-state-copy">
                        The registry returned no records matching the parsed
                        clinical constraints. This is distinct from a registry
                        request failure.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                render_trials_table(trials_df),
                unsafe_allow_html=True,
            )


            render_source(
                {
                    "name": "ClinicalTrials.gov",
                    "url": "https://clinicaltrials.gov/",
                    "retrieved_at": clinical.get(
                        "retrieved_at"
                    ),
                },
                "Registry",
            )

            st.markdown(
                """
                <div class="footnote">
                Trial records are retrieved from the ClinicalTrials.gov
                API. Individual NCT records include their own source URL.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ========================================================
    # Market tab
    # ========================================================

    with tab_market:

        st.markdown(
            '<div class="section-title">Commercial market</div>',
            unsafe_allow_html=True,
        )

        market_summary = market.get(
            "summary",
            "No market summary is available.",
        )

        st.write(
            market_summary
        )

        if market_status == "UNAVAILABLE":

            st.markdown(
                """
                <div class="notice notice-warning">
                A reliable source-backed market estimate is not currently
                available for this therapeutic area. No fabricated estimate
                is displayed.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "2026 market",
                    market_data.get(
                        "estimated_size",
                        "Unavailable",
                    ),
                )

            with m2:
                st.metric(
                    "Reported CAGR",
                    market_data.get(
                        "cagr",
                        "Unavailable",
                    ),
                )

            with m3:
                st.metric(
                    "Competition",
                    market_data.get(
                        "competition_level",
                        "Unavailable",
                    ),
                )

            projections = market_data.get(
                "projections",
                [],
            )

            if projections:

                st.markdown(
                    '<div class="section-title">Derived market trajectory</div>',
                    unsafe_allow_html=True,
                )

                proj_df = pd.DataFrame(
                    projections
                )

                if (
                    "Year" in proj_df.columns
                    and "Market Size ($B)" in proj_df.columns
                ):

                    chart_df = (
                        proj_df[
                            ["Year", "Market Size ($B)"]
                        ]
                        .set_index("Year")
                    )

                    st.line_chart(
                        chart_df,
                        height=300,
                    )

                st.markdown(
                    """
                    <div class="footnote">
                    The first value is the source-backed baseline.
                    Subsequent values are derived projections using the
                    configured growth-rate assumption; they are not
                    independently reported market figures.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            drivers = market_data.get(
                "key_drivers",
                [],
            )

            if drivers:

                st.markdown(
                    '<div class="section-title">Commercial drivers</div>',
                    unsafe_allow_html=True,
                )

                for driver in drivers:
                    st.markdown(
                        f"- {driver}"
                    )

        render_source(
            market.get("source"),
            "Primary market source",
        )

        if market.get("secondary_source"):
            render_source(
                market.get("secondary_source"),
                "Secondary context",
            )

    # ========================================================
    # Patent tab
    # ========================================================

    with tab_patent:

        st.markdown(
            '<div class="section-title">Intellectual property</div>',
            unsafe_allow_html=True,
        )

        patent_summary = patent.get(
            "summary",
            "No patent assessment is available.",
        )

        st.write(
            patent_summary
        )

        if patent.get("error"):

            st.markdown(
                f"""
                <div class="notice notice-warning">
                {esc(patent["error"])}
                </div>
                """,
                unsafe_allow_html=True,
            )

        patents_df = normalize_patents(
            patent.get("patents")
        )

        if patents_df.empty:

            st.markdown(
                """
                <div class="notice notice-warning">
                Patent evidence is currently unavailable for this analysis.
                The system does not substitute simulated patents or a
                definitive FTO conclusion when evidence cannot be established.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.dataframe(
                patents_df,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown(
            """
            <div class="footnote">
            Preliminary IP risk is a research signal, not legal advice.
            Freedom-to-Operate requires professional claim-level analysis,
            jurisdiction review and consideration of patent-family and
            prosecution information.
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_source(
            {
                "name": patent.get(
                    "source",
                    "Patent source",
                ),
                "url": patent.get(
                    "source_url"
                ),
                "retrieved_at": patent.get(
                    "retrieved_at"
                ),
            },
            "Patent source",
        )

    # ========================================================
    # Run details tab
    # ========================================================

    with tab_trace:

        st.markdown(
            '<div class="section-title">Agent run</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="notice notice-info">
            Query: <strong>{esc(user_query)}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title">Execution trace</div>',
            unsafe_allow_html=True,
        )

        trace_lines = results.get(
            "trace",
            [],
        )

        trace_html = "".join(
            f'<div class="trace-line">{esc(line)}</div>'
            for line in trace_lines
        )

        st.markdown(
            f'<div class="trace">{trace_html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title">Parsed clinical query</div>',
            unsafe_allow_html=True,
        )

        if parsed:
            st.json(parsed)
        else:
            st.info(
                "No structured clinical query was returned."
            )

        st.markdown(
            '<div class="section-title">API parameters</div>',
            unsafe_allow_html=True,
        )

        api_parameters = clinical.get(
            "api_parameters"
        )

        if api_parameters:
            st.json(api_parameters)
        else:
            st.info(
                "No API parameters were returned."
            )

    # ========================================================
    # PDF export
    # ========================================================

    st.markdown(
        '<div class="section-title">Report</div>',
        unsafe_allow_html=True,
    )

    export_col1, export_col2 = st.columns(
        [4, 1]
    )

    with export_col1:
        st.markdown(
            """
            <div class="notice">
            Generate a PDF brief containing the current clinical,
            patent and market results.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with export_col2:

        try:

            if not clinical.get("summary"):
                clinical["summary"] = get_clinical_summary(clinical)

            pdf_path = generate_pdf_report(
                results,
                user_query,
            )

            with open(
                pdf_path,
                "rb",
            ) as pdf_file:

                pdf_data = pdf_file.read()

            st.download_button(
                "Download PDF",
                data=pdf_data,
                file_name=(
                    "pharmintel_analysis.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as exc:

            st.warning(
                f"PDF generation is currently unavailable: {exc}"
            )


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div class="footer">
    PharmIntel is a research and decision-support prototype.
    It does not provide medical advice, legal advice, definitive
    Freedom-to-Operate opinions, or investment guarantees.
    </div>
    """,
    unsafe_allow_html=True,
)
