"""views/upload_view.py — Dedicated Upload Customer File view."""
import textwrap
import streamlit as st
from components.icons import get_icon
from components.upload import run_pipeline
from utils.data import load_customers, generate_synthetic_customers


def render():
    st.markdown("""
    <div style="margin-bottom: 0.8rem;">
        <h2 style="font-size: 1.45rem; font-weight: 700; color: #FFFFFF; margin: 0; letter-spacing: -0.02em;">Upload Customer</h2>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload Box Card ──
    st.markdown("""
    <div class="bc-card" style="padding-bottom: 0.5rem; margin-bottom: 0.5rem;">
        <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">File Import Zone</div>
        <div style="color: #94A3B8; font-size: 0.8rem;">Provide CSV or Excel customer telemetry files up to 200MB.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload file", type=["csv", "xlsx", "xls"], label_visibility="collapsed", key="dedicated_uploader"
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── File Requirements ──
    req_columns = [
        "InactivityMonths",
        "TransactionFrequency",
        "NumProducts",
        "Tenure",
        "SupportTickets",
        "MonthlyCharges",
    ]

    cols_html = "".join([
        f"""<div style="background:var(--bc-surface-raised); border:1px solid var(--bc-border-subtle); padding:10px 12px; border-radius:8px; color:#F8FAFC; display:flex; align-items:center; gap:8px;">
            <span style="color:#10B981;">{get_icon("check-circle", size=15, color="#10B981")}</span>
            <span style="font-family:var(--bc-font-mono); font-size:0.8rem;">{col}</span>
        </div>"""
        for col in req_columns
    ])

    st.markdown(textwrap.dedent(f"""
    <div class="bc-card">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
            <div style="color:#3B82F6;">{get_icon("info", size=18, color="#3B82F6")}</div>
            <span style="font-weight:700; font-size:0.95rem; color:#FFFFFF;">Schema Validation Requirements</span>
        </div>
        <div style="color:#94A3B8; font-size:0.82rem; margin-bottom:14px;">
            The model accepts files containing the following banking telemetry features (standard aliases auto-mapped):
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; font-size: 0.82rem;">
            {cols_html}
        </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Upload & Predict Churn", key="upload_predict_btn", type="primary", use_container_width=True):
            if uploaded is not None:
                raw = load_customers(uploaded)
                st.session_state.uploaded_filename = uploaded.name
                st.session_state.customers = run_pipeline(raw)
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.warning("Please choose a file or click 'Load Demo Dataset' below.")
    with c2:
        if st.button("Load Demo Dataset (1,000 Accounts)", key="upload_demo_btn", use_container_width=True):
            raw = generate_synthetic_customers(1000)
            st.session_state.uploaded_filename = "demo_customers.csv"
            st.session_state.customers = run_pipeline(raw)
            st.session_state.page = "Dashboard"
            st.rerun()
