import streamlit as st

from components.customer_table import render_customer_rows
from utils.model import explain_customer, recommend_action


def render():
    st.markdown("<h2>Risk Customer</h2>", unsafe_allow_html=True)
    df = st.session_state.customers
    if df is None:
        st.info("Upload a customer file or load the demo dataset from the Dashboard first.")
        return

    st.markdown('<p class="bc-caption">Filter, search, and drill into any customer\'s churn risk.</p>', unsafe_allow_html=True)

    f1, f2 = st.columns([2.2, 1])
    with f1:
        risk_filter = st.radio(
            "Filter", ["All", "High Risk", "Medium Risk", "Low Risk"],
            horizontal=True, label_visibility="collapsed",
        )
    with f2:
        search = st.text_input("Search", placeholder="🔍 Search Customer ID…", label_visibility="collapsed")

    filtered = df
    if risk_filter != "All":
        level = risk_filter.split(" ")[0]
        filtered = filtered[filtered["RiskLevel"] == level]
    if search:
        filtered = filtered[filtered["CustomerID"].str.contains(search, case=False, na=False)]

    filtered = filtered.sort_values("ChurnProbability", ascending=False).head(60)
    st.markdown(f'<p class="bc-caption">{len(filtered)} customers shown (sorted by churn probability)</p>', unsafe_allow_html=True)

    factor_lookup = {}
    for _, row in filtered.iterrows():
        factors = explain_customer(row)
        rec = recommend_action(row, factors)
        factor_lookup[row["CustomerID"]] = {
            "label": factors[0]["label"] if factors else "—",
            "action": rec["action"],
        }

    render_customer_rows(filtered, factor_lookup)
