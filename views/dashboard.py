"""views/dashboard.py — Dashboard matching Swiss/Minimalist dark fintech design."""
import textwrap
import streamlit as st
import pandas as pd
from components.cards import stat_card
from components.charts import (
    churn_trend_line,
    risk_distribution_donut,
    churn_probability_hist,
)
from components.upload import render_upload_zone
from utils.helpers import fmt_int, clean_html
from utils.model import explain_customer
from utils.navigation import open_customer


def render():
    df = st.session_state.customers

    # ── Top Header Row (Clean 2-3 word title, zero fluff) ──
    h_col1, h_col2 = st.columns([3.5, 1.2])
    with h_col1:
        st.markdown("""
        <div style="margin-bottom: 0.8rem;">
            <h2 style="font-size: 1.45rem; font-weight: 700; color: #FFFFFF; margin: 0; letter-spacing: -0.02em;">Dashboard Overview</h2>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        st.selectbox("Timeframe", ["Last 30 Days", "Last 90 Days", "Year to Date"], label_visibility="collapsed", key="dash_timeframe")

    if df is None:
        render_upload_zone()
        return

    # Calculate real KPIs
    total = len(df)
    high = int((df["RiskLevel"] == "High").sum())
    medium = int((df["RiskLevel"] == "Medium").sum())
    low = int((df["RiskLevel"] == "Low").sum())
    churn_rate = (df["ChurnProbability"].mean()) * 100
    retention_rate = 100 - churn_rate

    # ── 4 Top Stat Cards ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Total Accounts", f"{total:,}", risk_key="total", delta="12%", delta_dir="up")
    with c2:
        stat_card("High Risk Accounts", f"{high:,}", risk_key="high", delta="8%", delta_dir="down")
    with c3:
        stat_card("Average Churn Rate", f"{churn_rate:.1f}%", risk_key="churn", delta="3.2%", delta_dir="down")
    with c4:
        stat_card("Customer Retention", f"{retention_rate:.1f}%", risk_key="retention", delta="3.2%", delta_dir="up")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Row 1 Charts: Trend & Risk Donut ──
    ch_col1, ch_col2 = st.columns([1.65, 1.15])
    with ch_col1:
        st.markdown("""
        <div class="bc-card">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.5rem;">Retention Trajectory Trend</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(churn_trend_line(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with ch_col2:
        st.markdown("""
        <div class="bc-card">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.5rem;">Risk Distribution Donut</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(
            risk_distribution_donut({"High": high, "Medium": medium, "Low": low}, total=total),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Row 2: At-Risk Accounts Table & Histogram ──
    t_col1, t_col2 = st.columns([1.8, 1.2])
    with t_col1:
        st.markdown("""
        <div class="bc-card" style="padding-bottom: 0.8rem;">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; display:flex; align-items:center; gap:6px; margin-bottom: 0.8rem;">
                <span style="color:#EF4444;">●</span> Priority At-Risk Accounts
            </div>
            <div style="display:grid; grid-template-columns: 100px 110px 90px 80px 1fr 75px; font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase; padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.06); letter-spacing:0.06em;">
                <div>Account ID</div>
                <div>Client</div>
                <div>Probability</div>
                <div>Tier</div>
                <div>Primary Driver</div>
                <div style="text-align:right;">Action</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        high_risk_sample = df.sort_values("ChurnProbability", ascending=False).head(5)
        names = ["Rahul Sharma", "Priya Verma", "Amit Singh", "Neha Gupta", "Vikram Rao"]

        for idx, (_, row) in enumerate(high_risk_sample.iterrows()):
            name = names[idx % len(names)]
            cid = row["CustomerID"]
            prob = row["ChurnProbability"]
            risk = row["RiskLevel"]
            risk_badge_cls = "bc-badge-high" if risk == "High" else "bc-badge-med" if risk == "Medium" else "bc-badge-low"
            bar_color = "#EF4444" if risk == "High" else "#F59E0B" if risk == "Medium" else "#10B981"

            factors = explain_customer(row)
            factor_text = factors[0]["label"] if factors else "Inactivity, Low Txn"

            col_a, col_b = st.columns([5.0, 1.0])
            with col_a:
                st.markdown(clean_html(f"""
                <div style="display:grid; grid-template-columns: 100px 110px 90px 80px 1fr; font-size: 0.82rem; align-items: center; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.04);">
                    <div class="bc-mono-id">{cid}</div>
                    <div style="color:#FFFFFF; font-weight:500;">{name}</div>
                    <div>
                        <div style="font-weight:700; color:{bar_color}; font-size:0.82rem;">{prob:.1%}</div>
                        <div class="bc-prob-bar-track">
                            <div class="bc-prob-bar-fill" style="width:{prob*100:.0f}%; background:{bar_color};"></div>
                        </div>
                    </div>
                    <div><span class="{risk_badge_cls}">{risk}</span></div>
                    <div style="color:#94A3B8; font-size:0.75rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{factor_text}</div>
                </div>
                """), unsafe_allow_html=True)
            with col_b:
                if st.button("Analyze", key=f"dash_view_{cid}", help="Drilldown into customer SHAP profile", use_container_width=True):
                    open_customer(cid)

    with t_col2:
        st.markdown("""
        <div class="bc-card">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.5rem;">Probability Distribution Histogram</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(churn_probability_hist(df["ChurnProbability"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

