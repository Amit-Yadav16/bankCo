"""components/navbar.py — Top navigation and sidebar for BankCo.
Reflects strictly verified model information, neutral guest state by default, and responsive styling.
"""
import streamlit as st
from components.icons import get_icon
from components.logo import render_logo_img

NAV_ITEMS = [
    ("Landing",       "Home"),
    ("Dashboard",     "Dashboard"),
    ("AI Explain",    "AI Explain"),
    ("Risk Customer", "Risk Customers"),
    ("History",       "History"),
    ("Upload",        "Upload Customer"),
]


def render_navbar():
    active = st.session_state.page
    authed = st.session_state.get("authed", False)
    user = st.session_state.get("user")

    # Ambient backdrop glow
    st.markdown('<div class="bc-ambient-glow"></div>', unsafe_allow_html=True)

    # Top Navigation Row — Unified single-row alignment across brand, nav items, and auth
    c_brand, c_home, c_dash, c_ai, c_risk, c_hist, c_up, c_auth = st.columns(
        [2.3, 0.85, 1.15, 1.1, 1.35, 0.95, 1.35, 1.15], gap="small"
    )

    with c_brand:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:9px; height:38px;">
            {render_logo_img(height=34, icon_only=True)}
            <div style="display:flex; align-items:baseline; gap:5px; white-space:nowrap; overflow:hidden;">
                <span style="font-family:var(--bc-font-head); font-weight:800; font-size:1.15rem; color:#FFFFFF; letter-spacing:-0.02em;">Bank<span style="color:#06B6D4;">Co</span></span>
                <span style="font-size:0.65rem; color:var(--bc-ink-faint); border-left:1px solid rgba(255,255,255,0.14); padding-left:5px;">Smarter Banking</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_home:
        if st.button("Home", key="nav_Landing", type="primary" if active == "Landing" else "secondary", use_container_width=True):
            st.session_state.page = "Landing"
            st.session_state.landing_section = None
            st.session_state.show_auth = None
            st.rerun()

    with c_dash:
        if st.button("Dashboard", key="nav_Dashboard", type="primary" if active == "Dashboard" else "secondary", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.session_state.landing_section = None
            st.session_state.show_auth = None
            st.rerun()

    with c_ai:
        if st.button("AI Explain", key="nav_AI_Explain", type="primary" if active == "AI Explain" else "secondary", use_container_width=True):
            st.session_state.page = "AI Explain"
            st.session_state.landing_section = None
            st.session_state.show_auth = None
            st.rerun()

    with c_risk:
        if st.button("Risk Customers", key="nav_Risk_Customer", type="primary" if active == "Risk Customer" else "secondary", use_container_width=True):
            st.session_state.page = "Risk Customer"
            st.session_state.landing_section = None
            st.session_state.show_auth = None
            st.rerun()

    with c_hist:
        if st.button("History", key="nav_History", type="primary" if active == "History" else "secondary", use_container_width=True):
            st.session_state.page = "History"
            st.session_state.landing_section = None
            st.session_state.show_auth = None
            st.rerun()

    with c_up:
        if st.button("Upload Customer", key="nav_Upload", type="primary" if active == "Upload" else "secondary", use_container_width=True):
            st.session_state.page = "Upload"
            st.session_state.landing_section = None
            st.session_state.show_auth = None
            st.rerun()

    with c_auth:
        if authed and user:
            name = user.get("name", "User")
            first_name = name.split()[0] if name else "User"
            if st.button(f"Sign Out ({first_name})", key="nav_signout_btn", type="secondary", use_container_width=True):
                st.session_state.authed = False
                st.session_state.user = None
                st.rerun()
        else:
            if st.button("Sign In", key="nav_signin_btn", type="secondary", use_container_width=True):
                st.session_state.show_auth = "signin"
                st.rerun()

    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.08); margin: 0.5rem 0 1.2rem 0;'></div>", unsafe_allow_html=True)


def render_sidebar():
    """Sidebar removed per user instruction in favor of direct full-width navigation."""
    pass

