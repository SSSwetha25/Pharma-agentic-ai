import streamlit as st
from master_agent import run_master_agent
from report.report_generator import generate_pdf_report


st.set_page_config(
    page_title="Agentic AI for Pharma Innovation",
    page_icon="🧠",
    layout="wide",
)

# ---------- Basic Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #111827, #020617);
    }
    h1, h2, h3, h4 {
        color: #f9fafb !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.write(
        "Agentic AI that combines **clinical trials**, **patent data**, and **market signals** "
        "to surface promising pharmaceutical opportunities."
    )

    st.markdown("### ⚙️ Analysis Settings")
    # add a key to avoid duplicate element IDs if this sidebar is rendered multiple times
    detail_level = st.radio("Detail level", ["Summary", "Detailed"], index=0, key="detail_level_radio")

    st.markdown("### 💡 Tips")
    st.caption(
        "- Be specific about indication, mechanism, or geography.\n"
        "- Mention constraints like `orphan`, `generic`, or `biologic`."
    )

# ---------- Header ----------
st.title("🧠 Agentic AI for Pharmaceutical Innovation")
st.subheader("Accelerating drug opportunity discovery using intelligent agents")

st.divider()

# ---------- Query Input ----------
st.markdown("### 🔍 Research Question")
user_query = st.text_area(
    "Describe the pharmaceutical strategy or opportunity you want to explore:",
    placeholder=(
        "Example: Identify oncology small-molecule opportunities with low patent risk in the US "
        "and EU over the next 5 years."
    ),
    height=140,
)

cols = st.columns([1, 3])
with cols[0]:
    analyze_btn = st.button("▶️ Run Agentic Analysis", use_container_width=True)
with cols[1]:
    st.caption("The system will orchestrate clinical, patent, and market agents over your query.")

# ---------- Run Analysis & Display Results ----------
if analyze_btn and user_query:
    with st.spinner("Running multi-agent analysis... this may take a few moments."):
        results = run_master_agent(user_query)

    st.success("Analysis complete. Explore the tabs below for detailed insights.")

    # Tabs for each agent + conclusion
    tab_clinical, tab_patent, tab_market, tab_conclusion = st.tabs(
        ["🧪 Clinical", "📄 Patent", "📈 Market", "🧷 Conclusion"]
    )

    with tab_clinical:
        st.subheader("Clinical Trials Insights")
        st.write(results["clinical"]["summary"])
        if "trials" in results["clinical"] and results["clinical"]["trials"] is not None:
            st.markdown("**Representative trials**")
            st.table(results["clinical"]["trials"])

    with tab_patent:
        st.subheader("Patent Landscape")
        st.write(results["patent"]["summary"])
        if "patents" in results["patent"] and results["patent"]["patents"] is not None:
            st.markdown("**Relevant patents**")
            st.table(results["patent"]["patents"])

    with tab_market:
        st.subheader("Market Overview")
        st.write(results["market"]["summary"])
        if "market_data" in results["market"] and results["market"]["market_data"] is not None:
            st.markdown("**Key market data**")
            st.json(results["market"]["market_data"])

    with tab_conclusion:
        st.subheader("Integrated Conclusion")
        st.write(results.get("conclusion", "No combined conclusion was generated."))

    st.divider()

    # ---------- Report Download Section ----------
    st.markdown("### 📊 Downloadable PDF Report")
    st.caption(
        "A concise report capturing your query, agentic insights, and a high-level recommendation."
    )

    pdf_path = generate_pdf_report(results, user_query)
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_file.read(),
            file_name="agentic_pharma_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

import streamlit as st
from master_agent import run_master_agent
from report.report_generator import generate_pdf_report


st.set_page_config(
    page_title="Agentic AI for Pharma Innovation",
    page_icon="🧠",
    layout="wide",
)

# ---------- Basic Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #111827, #020617);
    }
    h1, h2, h3, h4 {
        color: #f9fafb !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.write(
        "Agentic AI that combines **clinical trials**, **patent data**, and **market signals** "
        "to surface promising pharmaceutical opportunities."
    )

    st.markdown("### ⚙️ Analysis Settings")
    detail_level = st.radio("Detail level", ["Summary", "Detailed"], index=0)

    st.markdown("### 💡 Tips")
    st.caption(
        "- Be specific about indication, mechanism, or geography.\n"
        "- Mention constraints like `orphan`, `generic`, or `biologic`."
    )

# ---------- Header ----------
st.title("Agentic AI for Pharmaceutical Innovation")
st.subheader("Accelerating drug opportunity discovery using intelligent agents")

st.divider()

# ---------- Query Input ----------
st.markdown("### 🔍 Research Question")
user_query = st.text_area(
    "Describe the pharmaceutical strategy or opportunity you want to explore:",
    placeholder=(
        "Example: Identify oncology small-molecule opportunities with low patent risk in the US "
        "and EU over the next 5 years."
    ),
    height=140,
)

cols = st.columns([1, 3])
with cols[0]:
    analyze_btn = st.button("▶️ Run Agentic Analysis", use_container_width=True)
with cols[1]:
    st.caption("The system will orchestrate clinical, patent, and market agents over your query.")

# ---------- Run Analysis & Display Results ----------
if analyze_btn and user_query:
    with st.spinner("Running multi-agent analysis... this may take a few moments."):
        results = run_master_agent(user_query)

    st.success("Analysis complete. Explore the tabs below for detailed insights.")

    # Tabs for each agent + conclusion
    tab_clinical, tab_patent, tab_market, tab_conclusion = st.tabs(
        ["🧪 Clinical", "📄 Patent", "📈 Market", "🧷 Conclusion"]
    )

    with tab_clinical:
        st.subheader("Clinical Trials Insights")
        st.write(results["clinical"]["summary"])
        if "trials" in results["clinical"] and results["clinical"]["trials"] is not None:
            st.markdown("**Representative trials**")
            st.table(results["clinical"]["trials"])

    with tab_patent:
        st.subheader("Patent Landscape")
        st.write(results["patent"]["summary"])
        if "patents" in results["patent"] and results["patent"]["patents"] is not None:
            st.markdown("**Relevant patents**")
            st.table(results["patent"]["patents"])

    with tab_market:
        st.subheader("Market Overview")
        st.write(results["market"]["summary"])
        if "market_data" in results["market"] and results["market"]["market_data"] is not None:
            st.markdown("**Key market data**")
            st.json(results["market"]["market_data"])

    with tab_conclusion:
        st.subheader("Integrated Conclusion")
        st.write(results.get("conclusion", "No combined conclusion was generated."))

    st.divider()

    # ---------- Report Download Section ----------
    st.markdown("### 📊 Downloadable PDF Report")
    st.caption(
        "A concise report capturing your query, agentic insights, and a high-level recommendation."
    )

    pdf_path = generate_pdf_report(results, user_query)
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_file.read(),
            file_name="agentic_pharma_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
