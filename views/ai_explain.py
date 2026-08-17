import streamlit as st

from components.cards import gauge_svg, badge_html
from utils.helpers import RISK_COLORS, fmt_money, fmt_int
from utils.model import explain_customer, recommend_action


def render():
    st.markdown("<h2>AI Explain</h2>", unsafe_allow_html=True)
    df = st.session_state.customers
    if df is None:
        st.info("Upload a customer file or load the demo dataset from the Dashboard first.")
        return

    ids = df.sort_values("ChurnProbability", ascending=False)["CustomerID"].tolist()
    default = st.session_state.selected_customer if st.session_state.selected_customer in ids else ids[0]
    selected = st.selectbox("Select Customer", ids, index=ids.index(default))
    st.session_state.selected_customer = selected

    row = df[df["CustomerID"] == selected].iloc[0]
    factors = explain_customer(row)
    rec = recommend_action(row, factors)
    color = RISK_COLORS[row["RiskLevel"]]

    # ---- Customer overview + churn prediction ----
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown('<div class="bc-card">', unsafe_allow_html=True)
        st.markdown("##### Customer Overview")
        o1, o2 = st.columns(2)
        with o1:
            st.markdown(f"**Customer ID** <br>{row['CustomerID']}", unsafe_allow_html=True)
            st.markdown(f"**Customer Type** <br>{row['CustomerType']}", unsafe_allow_html=True)
            st.markdown(f"**Tenure** <br>{fmt_int(row['Tenure'])} months", unsafe_allow_html=True)
            st.markdown(f"**Active Products** <br>{fmt_int(row['NumProducts'])}", unsafe_allow_html=True)
        with o2:
            st.markdown(f"**Monthly Spend** <br>{fmt_money(row['MonthlyCharges'])}", unsafe_allow_html=True)
            st.markdown(f"**Total Spend** <br>{fmt_money(row['TotalSpend'])}", unsafe_allow_html=True)
            st.markdown(f"**Transactions / mo** <br>{fmt_int(row['TransactionFrequency'])}", unsafe_allow_html=True)
            st.markdown(f"**Support Tickets** <br>{fmt_int(row['SupportTickets'])}", unsafe_allow_html=True)
        st.markdown(f"**Inactivity** <br>{fmt_int(row['InactivityMonths'])} months since last activity", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="bc-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("##### Churn Prediction")
        st.markdown(
            f'<div style="display:flex; justify-content:center; margin: 0.6rem 0;">{gauge_svg(row["ChurnProbability"], color)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='font-weight:700; font-size:1.05rem;'>Churn Probability: {row['ChurnProbability']*100:.0f}%</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:0.4rem;'>{badge_html(row['RiskLevel'])}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Why is this customer at risk ----
    st.markdown("<div class='bc-section-title'>Why is this customer at risk?</div>", unsafe_allow_html=True)
    for i, f in enumerate(factors[:3], start=1):
        verb = "significantly increases" if f["direction"] == "increases" else "helps reduce"
        st.markdown(
            f"""<div class="bc-card" style="margin-bottom:0.6rem;">
                <b>{i}. {f['label']}</b><br>
                <span class="bc-caption">This factor {verb} churn risk for this customer.</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # ---- AI generated explanation / factor bars ----
    st.markdown("<div class='bc-section-title'>AI Generated Explanation</div>", unsafe_allow_html=True)
    positives = [f for f in factors if f["direction"] == "increases"]
    negatives = [f for f in factors if f["direction"] == "decreases"]

    top_pos = positives[0]["label"].lower() if positives else "no single dominant factor"
    top_neg = negatives[0]["label"].lower() if negatives else "no strong protective factor"
    st.markdown(
        f"<p>This customer's churn probability is estimated at "
        f"<b>{row['ChurnProbability']*100:.0f}%</b>, placing them in the "
        f"<b>{row['RiskLevel']}</b> risk band. The strongest driver is "
        f"<b>{top_pos}</b>, while <b>{top_neg}</b> is currently working in the customer's favor. "
        f"Together these behavioural signals — not any single event — shape the score.</p>",
        unsafe_allow_html=True,
    )

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("**Factors increasing churn risk**")
        for f in positives:
            _factor_bar(f, "pos")
    with fc2:
        st.markdown("**Factors reducing churn risk**")
        for f in negatives:
            _factor_bar(f, "neg")

    # ---- Retention recommendation ----
    st.markdown("<div class='bc-section-title'>Recommended Retention Strategy</div>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="bc-card">
            <div class="bc-caption" style="text-transform:uppercase; letter-spacing:0.04em; font-weight:700; margin-bottom:0.3rem;">Recommended Action</div>
            <p style="font-weight:600; margin-bottom:0.9rem;">"{rec['action']}"</p>
            <div class="bc-caption" style="text-transform:uppercase; letter-spacing:0.04em; font-weight:700; margin-bottom:0.3rem;">Why this action?</div>
            <p class="bc-caption">{rec['reason']}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.button("✨ Generate AI Retention Strategy", type="primary", key="gen_retention")
    st.markdown(
        "<p class='bc-caption' style='margin-top:0.5rem;'>This recommendation is an AI-assisted "
        "suggestion for your retention team to review — not a guaranteed action.</p>",
        unsafe_allow_html=True,
    )


def _factor_bar(f, kind):
    pct = int(f["impact"] * 100)
    st.markdown(
        f"""<div class="bc-factor">
            <div class="bc-factor-bar-wrap">
                <div class="bc-factor-top"><span>{f['label']}</span><span>{pct}%</span></div>
                <div class="bc-factor-track"><div class="bc-factor-fill {kind}" style="width:{pct}%;"></div></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
