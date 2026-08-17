import streamlit as st

from utils.navigation import PAGES, go_to

LOGO_SVG = """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2L2 7.5V9H22V7.5L12 2Z" fill="white"/>
<rect x="4" y="10" width="2.4" height="9" fill="white"/>
<rect x="10.8" y="10" width="2.4" height="9" fill="white"/>
<rect x="17.6" y="10" width="2.4" height="9" fill="white"/>
<rect x="2" y="20" width="20" height="2" fill="white"/>
</svg>"""

NAV_ICONS = {"Dashboard": "🏠", "AI Explain": "🧠", "Risk Customer": "⚠️", "History": "📊"}


def render_navbar():
    st.markdown('<div class="bc-navbar">', unsafe_allow_html=True)

    top_l, top_r = st.columns([3, 2])
    with top_l:
        st.markdown(
            f"""<div class="bc-brand">
                <div class="bc-brand-mark">{LOGO_SVG}</div>
                <div>
                    <div class="bc-brand-name">BankCo</div>
                    <div class="bc-brand-tag">Retention Intelligence</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with top_r:
        a1, a2, a3 = st.columns([1, 1, 0.7])
        with a1:
            if st.button("Sign In", key="nav_signin", use_container_width=True):
                st.session_state.show_auth = "signin"
        with a2:
            if st.button("Sign Up", key="nav_signup", use_container_width=True, type="primary"):
                st.session_state.show_auth = "signup"
        with a3:
            if st.button("👤", key="nav_profile", use_container_width=True):
                st.session_state.show_profile = not st.session_state.show_profile

    nav_cols = st.columns(len(PAGES) + 5)
    for i, page in enumerate(PAGES):
        with nav_cols[i]:
            active_class = "bc-navzone-active" if st.session_state.page == page else "bc-navzone"
            st.markdown(f'<div class="{active_class}">', unsafe_allow_html=True)
            if st.button(f"{NAV_ICONS[page]}  {page}", key=f"nav_{page}", use_container_width=True):
                go_to(page)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.show_profile:
        render_profile_panel()


def render_profile_panel():
    user = st.session_state.user
    with st.container():
        st.markdown('<div class="bc-card bc-fade-in" style="max-width:320px;">', unsafe_allow_html=True)
        st.markdown(f"**{user['name']}**")
        st.markdown(f"<span class='bc-caption'>{user['email']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='bc-caption'>Role: {user['role']}</span>", unsafe_allow_html=True)
        st.markdown("<span class='bc-caption'>Last login: Today, 9:14 AM</span>", unsafe_allow_html=True)
        st.markdown("<hr class='bc-hr' style='margin:0.7rem 0;'>", unsafe_allow_html=True)
        if st.button("Log out", key="profile_logout"):
            st.session_state.show_profile = False
        st.markdown("</div>", unsafe_allow_html=True)
