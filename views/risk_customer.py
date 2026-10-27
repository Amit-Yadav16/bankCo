"""views/risk_customer.py — Risk Customers table and filtration matching Swiss fintech UI."""
import streamlit as st
from components.icons import get_icon
from utils.helpers import RISK_COLORS, clean_html
from utils.model import explain_customer, recommend_action
from utils.navigation import open_customer


def render():
    df = st.session_state.customers

    st.markdown("""
    <div style="margin-bottom: 0.8rem;">
        <h2 style="font-size: 1.45rem; font-weight: 700; color: #FFFFFF; margin: 0; letter-spacing: -0.02em;">Risk Registry</h2>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.info("Upload a customer file or load the demo dataset from the Dashboard first.")
        return

    # Counts
    high = int((df["RiskLevel"] == "High").sum())
    medium = int((df["RiskLevel"] == "Medium").sum())
    low = int((df["RiskLevel"] == "Low").sum())
    total = len(df)

    # ── 3 Summary KPI Cards on top ──
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        st.markdown(clean_html(f"""
        <div class="bc-card" style="display:flex; align-items:center; gap:16px; padding:1.1rem;">
            <div style="width:42px; height:42px; border-radius:10px; background:rgba(239,68,68,0.14); color:#EF4444; display:flex; align-items:center; justify-content:center;">
                {get_icon("user-alert", size=20, color="#EF4444")}
            </div>
            <div>
                <div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">High Risk (≥60%)</div>
                <div style="font-size:1.65rem; font-weight:800; color:#FFFFFF; line-height:1.1; font-family:var(--bc-font-head);">{high:,}</div>
                <div style="font-size:0.72rem; color:#EF4444; font-weight:600;">{(high/total)*100:.1f}% of total accounts</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with k_col2:
        st.markdown(clean_html(f"""
        <div class="bc-card" style="display:flex; align-items:center; gap:16px; padding:1.1rem;">
            <div style="width:42px; height:42px; border-radius:10px; background:rgba(245,158,11,0.14); color:#F59E0B; display:flex; align-items:center; justify-content:center;">
                {get_icon("alert-circle", size=20, color="#F59E0B")}
            </div>
            <div>
                <div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Medium Risk (30-59%)</div>
                <div style="font-size:1.65rem; font-weight:800; color:#FFFFFF; line-height:1.1; font-family:var(--bc-font-head);">{medium:,}</div>
                <div style="font-size:0.72rem; color:#F59E0B; font-weight:600;">{(medium/total)*100:.1f}% of total accounts</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with k_col3:
        st.markdown(clean_html(f"""
        <div class="bc-card" style="display:flex; align-items:center; gap:16px; padding:1.1rem;">
            <div style="width:42px; height:42px; border-radius:10px; background:rgba(16,185,129,0.14); color:#10B981; display:flex; align-items:center; justify-content:center;">
                {get_icon("user-check", size=20, color="#10B981")}
            </div>
            <div>
                <div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Low Risk (&lt;30%)</div>
                <div style="font-size:1.65rem; font-weight:800; color:#FFFFFF; line-height:1.1; font-family:var(--bc-font-head);">{low:,}</div>
                <div style="font-size:0.72rem; color:#10B981; font-weight:600;">{(low/total)*100:.1f}% of total accounts</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ── Search & Filter Controls ──
    f_c1, f_c2, f_c3, f_c4 = st.columns([2.2, 1.2, 1.2, 1.0])
    with f_c1:
        search = st.text_input("Search Customer", placeholder="Search by Account ID...", label_visibility="collapsed")
    with f_c2:
        risk_filter = st.selectbox("Risk Level", ["All Risk Tiers", "High", "Medium", "Low"], label_visibility="collapsed")
    with f_c3:
        product_filter = st.selectbox("Products", ["All Products", "1 Product", "2 Products", "3+ Products"], label_visibility="collapsed")
    with f_c4:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export CSV",
            data=csv_data,
            file_name="bankco_risk_registry.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Filtering data
    filtered = df.copy()
    if risk_filter != "All Risk Tiers":
        filtered = filtered[filtered["RiskLevel"] == risk_filter]
    if search:
        filtered = filtered[filtered["CustomerID"].astype(str).str.contains(search, case=False, na=False)]
    if product_filter == "1 Product":
        filtered = filtered[filtered["NumProducts"] == 1]
    elif product_filter == "2 Products":
        filtered = filtered[filtered["NumProducts"] == 2]
    elif product_filter == "3+ Products":
        filtered = filtered[filtered["NumProducts"] >= 3]

    filtered = filtered.sort_values("ChurnProbability", ascending=False).head(20)

    # ── Table View ──
    st.markdown(clean_html(f"""
    <div class="bc-card" style="padding-bottom: 0.8rem; margin-top: 10px;">
        <div style="font-size:0.78rem; color:#94A3B8; margin-bottom:10px; display:flex; justify-content:space-between;">
            <span>Showing top {len(filtered)} risk accounts sorted by churn probability</span>
            <span style="color:#64748B;">Total filtered: {len(filtered)}</span>
        </div>
        <div style="display:grid; grid-template-columns: 100px 120px 90px 80px 1fr 75px; font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase; padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.06); letter-spacing:0.06em;">
            <div>Account ID</div>
            <div>Client Name</div>
            <div>Probability</div>
            <div>Risk Tier</div>
            <div>Primary Driver</div>
            <div style="text-align:right;">Action</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    names = ["Rahul Sharma", "Priya Verma", "Amit Singh", "Neha Gupta", "Vikram Rao", "Pooja Mehta", "Suresh Kumar", "Anjali Das", "Rohan Patil", "Sneha Iyer"]

    for idx, (_, row) in enumerate(filtered.iterrows()):
        name = names[idx % len(names)]
        cid = row["CustomerID"]
        prob = row["ChurnProbability"]
        risk = row["RiskLevel"]
        risk_badge_cls = "bc-badge-high" if risk == "High" else "bc-badge-med" if risk == "Medium" else "bc-badge-low"
        bar_color = "#EF4444" if risk == "High" else "#F59E0B" if risk == "Medium" else "#10B981"

        factors = explain_customer(row)
        factor_text = factors[0]["label"] if factors else "Inactivity, Low Txn"

        c1, c2 = st.columns([5.0, 1.0])
        with c1:
            st.markdown(clean_html(f"""
            <div style="display:grid; grid-template-columns: 100px 120px 90px 80px 1fr; font-size: 0.82rem; align-items: center; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.04);">
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
        with c2:
            if st.button("Inspect", key=f"risk_view_{cid}", help="Open full SHAP breakdown", use_container_width=True):
                open_customer(cid)

