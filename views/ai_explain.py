"""views/ai_explain.py — AI Explainability view matching Swiss fintech UI."""
import textwrap
import streamlit as st
from components.icons import get_icon
from utils.helpers import RISK_COLORS, fmt_money, fmt_int, clean_html
from utils.model import explain_customer, recommend_action
from components.charts import shap_waterfall


def render():
    df = st.session_state.customers

    st.markdown("""
    <div style="margin-bottom: 0.8rem;">
        <h2 style="font-size: 1.45rem; font-weight: 700; color: #FFFFFF; margin: 0; letter-spacing: -0.02em;">Customer Diagnostics</h2>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.info("Upload a customer file or load the demo dataset from the Dashboard first.")
        return

    ids = df.sort_values("ChurnProbability", ascending=False)["CustomerID"].tolist()
    default = st.session_state.selected_customer if st.session_state.selected_customer in ids else ids[0]

    # Customer selector
    sel_c1, sel_c2 = st.columns([1.6, 2.4])
    with sel_c1:
        selected = st.selectbox("Select Account ID for In-Depth Audit", ids, index=ids.index(default))
        st.session_state.selected_customer = selected

    row = df[df["CustomerID"] == selected].iloc[0]
    factors = explain_customer(row)
    rec = recommend_action(row, factors)
    color = RISK_COLORS[row["RiskLevel"]]
    prob_pct = int(row["ChurnProbability"] * 100)
    risk_badge_cls = "bc-badge-high" if row['RiskLevel'] == "High" else "bc-badge-med" if row['RiskLevel'] == "Medium" else "bc-badge-low"

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ── Top Row: Customer Details & Churn Prediction Card ──
    top_c1, top_c2 = st.columns([1.4, 1.6])

    with top_c1:
        st.markdown(clean_html(f"""
        <div class="bc-card" style="height: 100%;">
            <div class="bc-card-title">
                {get_icon("users", size=18, color="#3B82F6")}
                <span>Account Profile Telemetry</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem; margin-top: 1rem;">
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px;">
                    <span style="color: #94A3B8;">Customer ID</span>
                    <span class="bc-mono-id">{row['CustomerID']}</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px;">
                    <span style="color: #94A3B8;">Inactivity Months</span>
                    <span style="color: #FFFFFF; font-weight: 600;">{fmt_int(row['InactivityMonths'])} mos</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px;">
                    <span style="color: #94A3B8;">Transaction Frequency</span>
                    <span style="color: #FFFFFF; font-weight: 600;">{fmt_int(row['TransactionFrequency'])} / mo</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px;">
                    <span style="color: #94A3B8;">Active Bank Products</span>
                    <span style="color: #FFFFFF; font-weight: 600;">{fmt_int(row['NumProducts'])} products</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px;">
                    <span style="color: #94A3B8;">Relationship Tenure</span>
                    <span style="color: #FFFFFF; font-weight: 600;">{fmt_int(row['Tenure'])} months</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px;">
                    <span style="color: #94A3B8;">Support Incidents</span>
                    <span style="color: #FFFFFF; font-weight: 600;">{fmt_int(row['SupportTickets'])} tickets</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color: #94A3B8;">Monthly Account Charges</span>
                    <span style="color: #FFFFFF; font-weight: 600;">{fmt_money(row['MonthlyCharges'])}</span>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with top_c2:
        ring_color = "#EF4444" if row['RiskLevel'] == "High" else "#F59E0B" if row['RiskLevel'] == "Medium" else "#10B981"
        st.markdown(clean_html(f"""
        <div class="bc-card" style="height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div class="bc-card-title" style="margin:0;">
                    {get_icon("brain", size=18, color="#60A5FA")}
                    <span>Predictive Risk Assessment</span>
                </div>
                <span class="{risk_badge_cls}">
                    {row['RiskLevel']} Tier
                </span>
            </div>

            <div style="display: flex; align-items: center; justify-content: center; gap: 2rem; margin: 1.2rem 0;">
                <div style="width: 110px; height: 110px; border-radius: 50%; border: 6px solid {ring_color}; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 20px {ring_color}33;">
                    <div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing:0.06em;">Churn Probability</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF; line-height:1.1; font-family:var(--bc-font-head);">{prob_pct}%</div>
                    <div style="font-size: 0.68rem; color: {ring_color}; font-weight: 700;">{row['RiskLevel']} Risk</div>
                </div>
            </div>

            <!-- Recommendation Alert Card -->
            <div style="background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.22); border-radius: 10px; padding: 12px 14px; margin-top: 1rem;">
                <div style="display:flex; align-items:center; gap:8px; color:#60A5FA; font-size:0.8rem; font-weight:700; margin-bottom:4px;">
                    {get_icon("lightbulb", size=16, color="#60A5FA")}
                    <span>Recommended Retention Action Plan</span>
                </div>
                <div style="color: #F8FAFC; font-size: 0.82rem; line-height: 1.45;">
                    "{rec['action']}"
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Bottom Row: Top Factors Influencing Prediction & Detailed Explanation ──
    b_col1, b_col2 = st.columns([1.5, 1.5])

    with b_col1:
        st.markdown('<div class="bc-card">', unsafe_allow_html=True)
        st.markdown('<div class="bc-card-title">Top Behavioral Factors (SHAP Values)</div>', unsafe_allow_html=True)
        st.plotly_chart(shap_waterfall(factors), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with b_col2:
        st.markdown('<div class="bc-card"><div class="bc-card-title">Natural Language Explanation</div>', unsafe_allow_html=True)

        for i, f in enumerate(factors[:4], start=1):
            is_risk_increase = (f["direction"] == "increases")
            arrow_label = "Increases churn risk" if is_risk_increase else "Reduces churn risk (Protective)"
            arrow_color = "#EF4444" if is_risk_increase else "#10B981"
            icon_name = "trending-up" if is_risk_increase else "trending-down"
            icon_svg = get_icon(icon_name, size=15, color=arrow_color)

            st.markdown(clean_html(f"""
            <div style="margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.04);">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
                    <span style="font-weight: 600; font-size: 0.85rem; color: #FFFFFF; display:flex; align-items:center; gap:6px;">
                        {icon_svg} {f['label']}
                    </span>
                    <span style="color: {arrow_color}; font-size: 0.74rem; font-weight: 600;">{arrow_label}</span>
                </div>
                <p style="color: #94A3B8; font-size: 0.78rem; margin: 0; line-height: 1.45;">
                    Feature impact coefficient: {f['impact']:.3f}. This behavioral signal actively shifts this customer's score toward the {row['RiskLevel'].lower()}-risk classification tier.
                </p>
            </div>
            """), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
