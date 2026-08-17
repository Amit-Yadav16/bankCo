import time

import streamlit as st

from utils.data import generate_synthetic_customers, load_customers
from utils.model import predict_churn, risk_level


def run_pipeline(df):
    """Simulates the documented pipeline (validate -> preprocess -> predict
    -> classify -> explain -> recommend) with a visible progress trail, then
    stores predictions on the dataframe."""
    steps = [
        ("Validating file…", 0.12),
        ("Preprocessing customer data…", 0.30),
        ("Running churn prediction model…", 0.55),
        ("Calculating churn probability…", 0.72),
        ("Generating explainable AI insights…", 0.9),
        ("Preparing retention recommendations…", 1.0),
    ]
    progress = st.progress(0, text=steps[0][0])
    for text, pct in steps:
        progress.progress(pct, text=text)
        time.sleep(0.18)

    df = df.copy()
    df["ChurnProbability"] = predict_churn(df)
    df["RiskLevel"] = df["ChurnProbability"].apply(risk_level)
    progress.empty()
    st.markdown('<div class="bc-toast">✓ Analysis completed</div>', unsafe_allow_html=True)
    return df


def render_upload_zone():
    st.markdown('<div class="bc-upload-card">', unsafe_allow_html=True)
    st.markdown(
        """<div class="bc-upload-icon">⬆️</div>
        <div style="font-weight:700; margin-bottom:0.15rem;">+ Upload Customer File</div>
        <div class="bc-caption">CSV or Excel — customer attributes, tenure, transactions, support history.</div>""",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Upload customer file", type=["csv", "xlsx", "xls"],
        label_visibility="collapsed", key="uploader",
    )
    demo_col, _ = st.columns([1, 3])
    with demo_col:
        demo_clicked = st.button("Load Demo Dataset", key="demo_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded is not None and st.session_state.uploaded_filename != uploaded.name:
        raw = load_customers(uploaded)
        st.session_state.uploaded_filename = uploaded.name
        with st.spinner(None):
            st.session_state.customers = run_pipeline(raw)
        st.session_state.history.insert(0, {
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "file": uploaded.name,
            "customers": len(raw),
            "high_risk": int((st.session_state.customers["RiskLevel"] == "High").sum()),
            "status": "Completed",
        })
        st.rerun()

    if demo_clicked:
        raw = generate_synthetic_customers(1000)
        st.session_state.uploaded_filename = "demo_customers.csv"
        st.session_state.customers = run_pipeline(raw)
        st.session_state.history.insert(0, {
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "file": "demo_customers.csv (synthetic)",
            "customers": len(raw),
            "high_risk": int((st.session_state.customers["RiskLevel"] == "High").sum()),
            "status": "Completed",
        })
        st.rerun()

    if st.session_state.customers is not None:
        df = st.session_state.customers
        st.markdown(
            f"""<div class="bc-card" style="margin-top:0.9rem; display:flex; gap:2.2rem; flex-wrap:wrap;">
                <div><div class="bc-caption">File name</div><div style="font-weight:700;">{st.session_state.uploaded_filename}</div></div>
                <div><div class="bc-caption">Customers</div><div style="font-weight:700;">{len(df):,}</div></div>
                <div><div class="bc-caption">Features</div><div style="font-weight:700;">{df.shape[1]}</div></div>
                <div><div class="bc-caption">Status</div><div style="font-weight:700; color:#1E9A63;">✓ Ready</div></div>
            </div>""",
            unsafe_allow_html=True,
        )
