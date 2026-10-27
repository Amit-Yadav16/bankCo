"""views/landing.py — BankCo Home Landing Page.
Features BankCo logo, 2-3 word feature titles in boxes, and rich live telemetry preview.
"""
import streamlit as st
from components.icons import get_icon
from components.logo import render_logo_img
from utils.data import generate_synthetic_customers
from utils.model import predict_churn, risk_level


def clean_html(s: str) -> str:
    """Strips leading and trailing whitespace from every line to ensure zero markdown code blocks."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def render():
    # ── 1. HERO SECTION ───────────────────────────────────────────────────
    hero_left, hero_right = st.columns([1.15, 1.05], gap="large")

    with hero_left:
        st.markdown(clean_html(f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(59,130,246,0.12); border:1px solid rgba(59,130,246,0.28); color:#60A5FA; padding:4px 12px; border-radius:100px; font-size:0.75rem; font-weight:600; margin-bottom:1rem;">
                {render_logo_img(height=18, icon_only=True)}
                <span>Institutional Churn Prevention</span>
            </div>
            <h1 style="font-size: clamp(2.2rem, 3.5vw, 3.2rem); font-weight: 800; line-height: 1.12; color: #FFFFFF; margin: 0 0 1rem 0; letter-spacing: -0.035em;">
                Predict Churn.<br>
                <span style="background: linear-gradient(135deg, #60A5FA 0%, #38BDF8 60%, #10B981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Protect Banking Relationships.
                </span>
            </h1>
            <p style="font-size: 0.98rem; color: #94A3B8; line-height: 1.55; margin: 0 0 1.5rem 0;">
                BankCo analyzes transactional cadence, inactivity patterns, and support telemetry with explainable ML to identify customer churn risk before accounts leave.
            </p>
        </div>
        """), unsafe_allow_html=True)

        # Primary Call-to-Action Buttons
        btn_c1, btn_c2 = st.columns([1.2, 1.3])
        with btn_c1:
            if st.button("Launch Dashboard →", key="landing_dash_btn", type="primary", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
        with btn_c2:
            if st.button("Load Demo Dataset", key="landing_demo_btn", use_container_width=True):
                raw = generate_synthetic_customers(1000)
                st.session_state.uploaded_filename = "demo_customers.csv (synthetic)"
                df = raw.copy()
                df["ChurnProbability"] = predict_churn(df)
                df["RiskLevel"] = df["ChurnProbability"].apply(risk_level)
                st.session_state.customers = df
                st.session_state.page = "Dashboard"
                st.rerun()

        # 4 Core Value Props Grid with 2-3 word titles in boxes
        st.markdown(clean_html(f"""
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:1.8rem;">
            <div style="display:flex; align-items:center; gap:8px; background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); padding:9px 12px; border-radius:8px; font-size:0.82rem; color:#F8FAFC; font-weight:600;">
                <span style="color:#60A5FA;">{get_icon("brain", size=16, color="#60A5FA")}</span>
                <span>Random Forest Scoring</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px; background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); padding:9px 12px; border-radius:8px; font-size:0.82rem; color:#F8FAFC; font-weight:600;">
                <span style="color:#10B981;">{get_icon("lightbulb", size=16, color="#10B981")}</span>
                <span>Explainable SHAP Insights</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px; background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); padding:9px 12px; border-radius:8px; font-size:0.82rem; color:#F8FAFC; font-weight:600;">
                <span style="color:#F59E0B;">{get_icon("target", size=16, color="#F59E0B")}</span>
                <span>Targeted Action Playbooks</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px; background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); padding:9px 12px; border-radius:8px; font-size:0.82rem; color:#F8FAFC; font-weight:600;">
                <span style="color:#38BDF8;">{get_icon("lock", size=16, color="#38BDF8")}</span>
                <span>Local Data Security</span>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with hero_right:
        # Preview Window Card with Live Telemetry (No Code)
        st.markdown(clean_html(f"""
        <div class="bc-card" style="padding:0; overflow:hidden; border-radius:14px; border:1px solid rgba(59,130,246,0.3); box-shadow:0 16px 40px rgba(0,0,0,0.6);">
            <!-- Window Titlebar -->
            <div style="display:flex; align-items:center; gap:6px; padding:9px 14px; background:var(--bc-surface-raised); border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="width:8px; height:8px; border-radius:50%; background:#EF4444;"></span>
                <span style="width:8px; height:8px; border-radius:50%; background:#F59E0B;"></span>
                <span style="width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
                <span style="font-size:0.72rem; color:#94A3B8; font-family:var(--bc-font-mono); margin-left:8px;">bankco-intelligence.internal/dashboard</span>
            </div>
            <!-- Window Body -->
            <div style="padding:14px;">
                <!-- Mini Stats Row -->
                <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; margin-bottom:12px;">
                    <div style="background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:7px; text-align:center;">
                        <div style="font-size:0.95rem; font-weight:800; color:#FFFFFF;">1,248</div>
                        <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">Accounts</div>
                    </div>
                    <div style="background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:7px; text-align:center;">
                        <div style="font-size:0.95rem; font-weight:800; color:#EF4444;">312</div>
                        <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">At Risk</div>
                    </div>
                    <div style="background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:7px; text-align:center;">
                        <div style="font-size:0.95rem; font-weight:800; color:#F59E0B;">12.6%</div>
                        <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">Churn Rate</div>
                    </div>
                    <div style="background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:7px; text-align:center;">
                        <div style="font-size:0.95rem; font-weight:800; color:#10B981;">87.4%</div>
                        <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">Retention</div>
                    </div>
                </div>

                <!-- Live Risk Detection Feed (Real UI, Zero Code) -->
                <div style="background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:10px 12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-size:0.7rem; font-weight:700; color:#F8FAFC; text-transform:uppercase; letter-spacing:0.06em;">Real-Time Risk Detections</div>
                        <span style="font-size:0.65rem; color:#10B981; font-weight:600;">● Active Monitoring</span>
                    </div>

                    <!-- Row 1 -->
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.75rem;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:#EF4444; font-weight:700;">#718293</span>
                            <span style="color:#94A3B8;">Gold Commercial</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:#EF4444; font-weight:700;">94.2% Risk</span>
                            <span style="background:rgba(239,68,68,0.18); color:#EF4444; font-size:0.62rem; font-weight:700; padding:1px 6px; border-radius:4px;">CRITICAL</span>
                        </div>
                    </div>

                    <!-- Row 2 -->
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.75rem;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:#F59E0B; font-weight:700;">#682140</span>
                            <span style="color:#94A3B8;">Platinum Private</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:#F59E0B; font-weight:700;">87.5% Risk</span>
                            <span style="background:rgba(245,158,11,0.18); color:#F59E0B; font-size:0.62rem; font-weight:700; padding:1px 6px; border-radius:4px;">HIGH</span>
                        </div>
                    </div>

                    <!-- Row 3 -->
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; font-size:0.75rem;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:#3B82F6; font-weight:700;">#794122</span>
                            <span style="color:#94A3B8;">Premier Business</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:#F59E0B; font-weight:700;">73.1% Risk</span>
                            <span style="background:rgba(245,158,11,0.18); color:#F59E0B; font-size:0.62rem; font-weight:700; padding:1px 6px; border-radius:4px;">MEDIUM</span>
                        </div>
                    </div>
                </div>

                <!-- Top Risk Drivers Breakdown Bar -->
                <div style="background:var(--bc-surface-raised); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:10px 12px;">
                    <div style="font-size:0.7rem; font-weight:700; color:#F8FAFC; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">Top Behavioral Churn Drivers</div>
                    <div style="display:flex; flex-direction:column; gap:5px; font-size:0.72rem;">
                        <div>
                            <div style="display:flex; justify-content:space-between; color:#94A3B8; margin-bottom:2px;">
                                <span>Transaction Frequency Drop</span>
                                <span style="color:#EF4444; font-weight:600;">+42% impact</span>
                            </div>
                            <div style="height:4px; border-radius:2px; background:rgba(255,255,255,0.08); overflow:hidden;">
                                <div style="width:78%; height:100%; background:#EF4444; border-radius:2px;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; color:#94A3B8; margin-bottom:2px;">
                                <span>Zero Revolving Balance</span>
                                <span style="color:#F59E0B; font-weight:600;">+28% impact</span>
                            </div>
                            <div style="height:4px; border-radius:2px; background:rgba(255,255,255,0.08); overflow:hidden;">
                                <div style="width:56%; height:100%; background:#F59E0B; border-radius:2px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # ── 2. FEATURES SECTION (Boxes with 2-3 word titles) ─────────────────────
    st.markdown(clean_html("""
    <div style="text-align:center; max-width:680px; margin:0 auto 2rem;">
        <h2 style="font-size:1.65rem; font-weight:700; color:#FFFFFF; margin:0 0 0.4rem 0; letter-spacing:-0.03em;">
            Comprehensive Retention Intelligence
        </h2>
        <p style="color:#94A3B8; font-size:0.88rem; margin:0;">
            Turn transactional patterns into early warnings and targeted relationship preservation strategies.
        </p>
    </div>
    """), unsafe_allow_html=True)

    features = [
        ("brain", "#3B82F6", "Machine Learning Scoring",
         "Trained Random Forest algorithm processing 19 behavioral features into calibrated churn probabilities."),
        ("lightbulb", "#10B981", "Explainable SHAP Insights",
         "Feature-level SHAP attributions explaining the specific transactional drivers behind each client's risk score."),
        ("shield-check", "#F59E0B", "Risk Triage Cohorts",
         "Automated cohort segmentation into High (≥60%), Medium (30-59%), and Low (<30%) risk categories."),
        ("target", "#06B6D4", "Tailored Action Playbooks",
         "Personalized retention interventions formulated directly from client account history and tenure."),
        ("activity", "#8B5CF6", "Historical Audit Trails",
         "Historical tracking of past batch predictions and portfolio-wide churn trajectory."),
    ]

    cols = st.columns(len(features))
    for col, (icon_name, fg_col, title, desc) in zip(cols, features):
        with col:
            st.markdown(clean_html(f"""
            <div class="bc-card" style="height:100%; display:flex; flex-direction:column; gap:8px;">
                <div style="width:36px; height:36px; border-radius:8px; background:rgba(255,255,255,0.05); display:flex; align-items:center; justify-content:center; color:{fg_col}; margin-bottom:4px;">
                    {get_icon(icon_name, size=18, color={repr(fg_col)})}
                </div>
                <div style="font-weight:700; font-size:0.88rem; color:#FFFFFF;">{title}</div>
                <div style="font-size:0.75rem; color:#94A3B8; line-height:1.45;">{desc}</div>
            </div>
            """), unsafe_allow_html=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # ── 3. HOW IT WORKS (Boxes with 2-3 word titles) ────────────────────────
    st.markdown(clean_html("""
    <div style="text-align:center; max-width:600px; margin:0 auto 2rem;">
        <h2 style="font-size:1.65rem; font-weight:700; color:#FFFFFF; margin:0; letter-spacing:-0.03em;">
            How It Works
        </h2>
    </div>
    """), unsafe_allow_html=True)

    steps = [
        ("1", "Upload File", "Provide customer accounts in CSV or Excel format containing standard banking fields."),
        ("2", "Model Scoring", "The Random Forest pipeline processes transactional features into calibrated probabilities."),
        ("3", "Inspect Drivers", "Explore individual SHAP waterfall charts revealing exact risk catalysts."),
        ("4", "Execute Retention", "Implement suggested interventions: fee adjustments, product reviews, or proactive outreach."),
    ]

    s_cols = st.columns(4)
    for col, (num, title, desc) in zip(s_cols, steps):
        with col:
            st.markdown(clean_html(f"""
            <div class="bc-card" style="height:100%;">
                <div style="width:30px; height:30px; border-radius:7px; background:linear-gradient(135deg,#3B82F6,#1D4ED8); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:0.85rem; color:#fff; margin-bottom:10px;">
                    {num}
                </div>
                <div style="font-weight:700; font-size:0.92rem; color:#FFFFFF; margin-bottom:4px;">{title}</div>
                <div style="font-size:0.75rem; color:#94A3B8; line-height:1.45;">{desc}</div>
            </div>
            """), unsafe_allow_html=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # ── 4. FAQ ────────────────────────────────────────────────────────────
    st.markdown(clean_html("""
    <div style="text-align:center; max-width:600px; margin:0 auto 1.5rem;">
        <h2 style="font-size:1.65rem; font-weight:700; color:#FFFFFF; margin:0; letter-spacing:-0.03em;">
            Frequently Asked Questions
        </h2>
    </div>
    """), unsafe_allow_html=True)

    faq1, faq2 = st.columns(2)
    with faq1:
        with st.expander("What model powers the predictions?", expanded=True):
            st.write(
                "A tuned **Random Forest Classifier** trained on the BankChurners dataset (10,127 records). "
                "On a held-out test evaluation of 2,026 samples, it achieves **95.31% accuracy**, **0.9859 ROC-AUC**, and **86.77% recall**."
            )
        with st.expander("What file formats are accepted?"):
            st.write("Upload **CSV, XLSX, or XLS** files up to 200MB. The pipeline automatically maps standard column aliases.")

    with faq2:
        with st.expander("How does explainable AI work in BankCo?", expanded=True):
            st.write(
                "BankCo utilizes **TreeSHAP** to measure the exact contribution of each behavioral feature (such as transaction count changes and inactivity) to a customer's risk probability."
            )
        with st.expander("Is confidential data sent to third-party APIs?"):
            st.write("**No.** The machine learning pipeline runs locally in Python. No banking data is transmitted externally.")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # ── 5. FOOTER (With BankCo Logo) ────────────────────────────────────────
    st.markdown(clean_html(f"""
    <div style="padding:1.5rem 0; border-top:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div style="display:flex; align-items:center; gap:10px;">
            {render_logo_img(height=32, icon_only=True)}
            <span style="font-weight:800; color:#FFFFFF; font-size:1.05rem;">Bank<span style="color:#06B6D4;">Co</span></span>
            <span style="color:#64748B; font-size:0.75rem; border-left:1px solid rgba(255,255,255,0.12); padding-left:8px;">Smarter Banking. Brighter Future.</span>
        </div>
        <div style="display:flex; align-items:center; gap:16px; font-size:0.75rem; color:#94A3B8;">
            <span style="display:flex; align-items:center; gap:4px;">
                {get_icon("lock", size=13, color="#10B981")} SOC2 Compliant Schema
            </span>
            <span style="display:flex; align-items:center; gap:4px;">
                {get_icon("database", size=13, color="#3B82F6")} Local Execution
            </span>
            <span style="color:#64748B;">© 2026 BankCo Enterprise</span>
        </div>
    </div>
    """), unsafe_allow_html=True)
