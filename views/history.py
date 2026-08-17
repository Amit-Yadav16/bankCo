import streamlit as st


def render():
    st.markdown("<h2>History</h2>", unsafe_allow_html=True)
    hist = st.session_state.history

    if not hist:
        st.info("No previous prediction sessions yet — run an analysis from the Dashboard.")
        return

    st.markdown('<p class="bc-caption">Previous prediction sessions for this workspace.</p>', unsafe_allow_html=True)
    st.markdown(
        """<div class="bc-row bc-row-head" style="grid-template-columns: 1.4fr 2fr 1fr 1fr 1fr; border:none;">
            <div>Date</div><div>File</div><div>Customers</div><div>High Risk</div><div>Status</div>
        </div>""",
        unsafe_allow_html=True,
    )
    for i, h in enumerate(hist):
        st.markdown(
            f"""<div class="bc-row" style="grid-template-columns: 1.4fr 2fr 1fr 1fr 1fr;">
                <div>{h['date']}</div>
                <div>{h['file']}</div>
                <div>{h['customers']:,}</div>
                <div style="color:#E0403A; font-weight:700;">{h['high_risk']:,}</div>
                <div><span class="bc-badge low">✓ {h['status']}</span></div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='bc-section-title'>Session detail</div>", unsafe_allow_html=True)
    labels = [f"{h['date']} — {h['file']}" for h in hist]
    picked = st.selectbox("View a past session", labels, label_visibility="collapsed")
    h = hist[labels.index(picked)]
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers analysed", f"{h['customers']:,}")
    c2.metric("High risk flagged", f"{h['high_risk']:,}")
    c3.metric("Status", h["status"])
    st.markdown(
        "<p class='bc-caption'>Full per-customer results, AI explanations, and generated "
        "recommendations for this session are available on the Risk Customer and AI Explain "
        "pages while its dataset is active.</p>",
        unsafe_allow_html=True,
    )
