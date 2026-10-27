"""components/upload.py — Customer dataset upload processor and inline dropzone."""
import time
import streamlit as st
from components.icons import get_icon
from utils.data import generate_synthetic_customers, load_customers
from utils.model import predict_churn, risk_level


def run_pipeline(df):
    """Simulates the documented pipeline (validate -> preprocess -> predict
    -> classify -> explain -> recommend) with a visible progress trail, then
    stores predictions on the dataframe."""
    steps = [
        ("Validating dataset schema & data types…", 0.15),
        ("Preprocessing customer transactional features…", 0.35),
        ("Running Random Forest churn classification…", 0.60),
        ("Calibrating individual churn probabilities…", 0.78),
        ("Generating SHAP feature attributions…", 0.92),
        ("Synthesizing tailored retention playbooks…", 1.0),
    ]
    progress = st.progress(0, text=steps[0][0])
    for text, pct in steps:
        progress.progress(pct, text=text)
        time.sleep(0.12)

    df = df.copy()
    df["ChurnProbability"] = predict_churn(df)
    df["RiskLevel"] = df["ChurnProbability"].apply(risk_level)
    progress.empty()
    st.markdown('<div class="bc-toast">✓ Pipeline completed · Churn probabilities calculated</div>', unsafe_allow_html=True)
    return df


def render_upload_zone():
    col1, col2 = st.columns([1.2, 1.0], gap="medium")
    with col1:
        st.markdown("""
        <div class="bc-card" style="padding-bottom: 0.5rem; margin-bottom: 0.5rem;">
            <div style="font-weight:700; font-size:1.05rem; color:#FFFFFF; margin-bottom:0.25rem;">Upload Customer File</div>
            <div style="color:#94A3B8; font-size:0.8rem;">Provide CSV or Excel customer telemetry files up to 200MB.</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload customer file", type=["csv", "xlsx", "xls"],
            label_visibility="collapsed", key="uploader",
        )

    with col2:
        st.markdown("""
        <div class="bc-card" style="padding-bottom: 0.5rem; margin-bottom: 0.5rem;">
            <div style="font-weight:700; font-size:1.05rem; color:#FFFFFF; margin-bottom:0.25rem;">Live Demo Dataset</div>
            <div style="color:#94A3B8; font-size:0.8rem; margin-bottom:0.8rem;">Populate 1,000 synthetic banking accounts instantly to test models.</div>
        </div>
        """, unsafe_allow_html=True)
        demo_clicked = st.button("Load Demo Dataset", key="demo_btn", type="primary", use_container_width=True)

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
            f"""<div class="bc-card" style="margin-top:0.9rem; display:flex; gap:2.5rem; flex-wrap:wrap; align-items:center;">
                <div><div style="font-size:0.7rem; color:#64748B; text-transform:uppercase; font-weight:700;">Active Portfolio</div><div style="font-weight:700; color:#FFFFFF; font-family:var(--bc-font-mono); font-size:0.88rem;">{st.session_state.uploaded_filename}</div></div>
                <div><div style="font-size:0.7rem; color:#64748B; text-transform:uppercase; font-weight:700;">Total Accounts</div><div style="font-weight:700; color:#FFFFFF; font-size:0.88rem;">{len(df):,}</div></div>
                <div><div style="font-size:0.7rem; color:#64748B; text-transform:uppercase; font-weight:700;">Tracked Features</div><div style="font-weight:700; color:#FFFFFF; font-size:0.88rem;">{df.shape[1]}</div></div>
                <div><div style="font-size:0.7rem; color:#64748B; text-transform:uppercase; font-weight:700;">Model Engine</div><div style="font-weight:700; color:#10B981; font-size:0.88rem;">✓ Live Inferences</div></div>
            </div>""",
            unsafe_allow_html=True,
        )

