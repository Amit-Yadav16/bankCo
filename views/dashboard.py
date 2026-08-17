import streamlit as st

from components.cards import stat_card
from components.charts import risk_distribution_donut, churn_probability_hist, segment_bar, top_factors_bar
from components.upload import render_upload_zone
from utils.helpers import fmt_int
from utils.model import explain_customer, FEATURE_LABELS

BLOG_POSTS = [
    ("📉", "Why Do Bank Customers Churn?", "Inactivity, thinning product usage, and unresolved support issues are the three earliest warning signs retention teams overlook."),
    ("🤖", "How AI Predicts Customer Churn", "A short walkthrough of how behavioural signals — tenure, spend, transaction cadence — get turned into a single risk score."),
    ("🔍", "Using Explainable AI in Banking", "Why a probability alone isn't enough, and how factor-level explanations help frontline staff act with confidence."),
]


def render():
    st.markdown('<div class="bc-hero">', unsafe_allow_html=True)
    st.markdown('<span class="bc-hero-eyebrow">● Retention Intelligence</span>', unsafe_allow_html=True)
    st.markdown("<h1>Customer Churn Prediction &amp; Retention System</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p>Identify high-risk customers, understand why they may leave, and take data-driven "
        "retention actions — all from one dashboard.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    render_upload_zone()

    df = st.session_state.customers
    if df is None:
        st.markdown("<div class='bc-section-title'>From the BankCo journal</div>", unsafe_allow_html=True)
        render_blog_section()
        return

    total = len(df)
    high = int((df["RiskLevel"] == "High").sum())
    medium = int((df["RiskLevel"] == "Medium").sum())
    low = int((df["RiskLevel"] == "Low").sum())

    st.markdown("<div class='bc-section-title'>Portfolio overview</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Total Customers", fmt_int(total), "👥")
    with c2:
        stat_card("High Risk", fmt_int(high), "🔴", risk_key="high")
    with c3:
        stat_card("Medium Risk", fmt_int(medium), "🟡", risk_key="medium")
    with c4:
        stat_card("Low Risk", fmt_int(low), "🟢", risk_key="low")

    st.markdown("<div class='bc-section-title'>Analytics</div>", unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.plotly_chart(
            risk_distribution_donut({"High": high, "Medium": medium, "Low": low}),
            use_container_width=True, config={"displayModeBar": False},
        )
    with r1c2:
        st.plotly_chart(
            churn_probability_hist(df["ChurnProbability"]),
            use_container_width=True, config={"displayModeBar": False},
        )

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.plotly_chart(segment_bar(df), use_container_width=True, config={"displayModeBar": False})
    with r2c2:
        sample = df.sample(min(len(df), 250), random_state=1)
        all_factors = [explain_customer(row) for _, row in sample.iterrows()]
        import pandas as pd
        fmeans = pd.DataFrame([{f["feature"]: f["impact"] for f in row} for row in all_factors]).mean()
        fmeans.index = [FEATURE_LABELS.get(i, i) for i in fmeans.index]
        st.plotly_chart(top_factors_bar(fmeans.sort_values()), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='bc-section-title'>From the BankCo journal</div>", unsafe_allow_html=True)
    render_blog_section()


def render_blog_section():
    cols = st.columns(3)
    for col, (icon, title, desc) in zip(cols, BLOG_POSTS):
        with col:
            st.markdown(
                f"""<div class="bc-blog-card">
                    <div class="bc-blog-thumb">{icon}</div>
                    <div class="bc-blog-body">
                        <div class="bc-blog-title">{title}</div>
                        <div class="bc-blog-desc">{desc}</div>
                        <div class="bc-blog-link">Read More →</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
