import streamlit as st

from components.cards import gauge_svg, badge_html
from utils.helpers import RISK_COLORS
from utils.navigation import open_customer


def render_customer_rows(df, factor_lookup):
    st.markdown(
        """<div class="bc-row bc-row-head" style="border:none;margin-bottom:0.2rem;">
            <div>Customer</div><div>Churn Probability</div><div>Risk Level</div>
            <div>Main Risk Factor</div><div>Recommended Action</div><div></div>
        </div>""",
        unsafe_allow_html=True,
    )

    for _, row in df.iterrows():
        cid = row["CustomerID"]
        prob = row["ChurnProbability"]
        risk = row["RiskLevel"]
        color = RISK_COLORS[risk]
        top_factor = factor_lookup.get(cid, {}).get("label", "—")
        action = factor_lookup.get(cid, {}).get("action", "—")

        c = st.container()
        with c:
            cols = st.columns([1.1, 1.3, 0.9, 1.6, 1.6, 0.7])
            with cols[0]:
                st.markdown(f'<div class="bc-row-id">{cid}</div><div class="bc-row-sub">{row["CustomerType"]}</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(gauge_svg(prob, color, "bc-gauge-sm"), unsafe_allow_html=True)
            with cols[2]:
                st.markdown(badge_html(risk), unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f'<div class="bc-row-sub">{top_factor}</div>', unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f'<div class="bc-row-sub">{action}</div>', unsafe_allow_html=True)
            with cols[5]:
                if st.button("View →", key=f"view_{cid}"):
                    open_customer(cid)
