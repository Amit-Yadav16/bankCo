import streamlit as st


def render_auth_panel():
    mode = st.session_state.show_auth
    if mode not in ("signin", "signup"):
        return

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown('<div class="bc-card bc-fade-in">', unsafe_allow_html=True)
        if mode == "signin":
            st.markdown("#### Sign in to BankCo")
            st.text_input("Email", key="signin_email", placeholder="you@bankco.com")
            st.text_input("Password", key="signin_pw", type="password", placeholder="••••••••")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Sign In", key="do_signin", type="primary", use_container_width=True):
                    st.session_state.authed = True
                    st.session_state.show_auth = None
                    st.rerun()
            with c2:
                if st.button("Cancel", key="cancel_signin", use_container_width=True):
                    st.session_state.show_auth = None
                    st.rerun()
            st.button("Forgot Password?", key="forgot_pw")
            st.markdown(
                "<div class='bc-caption'>New here? "
                "</div>", unsafe_allow_html=True,
            )
            if st.button("Create an account instead", key="switch_signup"):
                st.session_state.show_auth = "signup"
                st.rerun()
        else:
            st.markdown("#### Create your BankCo account")
            st.text_input("Name", key="signup_name", placeholder="Full name")
            st.text_input("Email", key="signup_email", placeholder="you@bankco.com")
            st.text_input("Password", key="signup_pw", type="password")
            st.text_input("Confirm Password", key="signup_pw2", type="password")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Create Account", key="do_signup", type="primary", use_container_width=True):
                    st.session_state.authed = True
                    st.session_state.show_auth = None
                    st.rerun()
            with c2:
                if st.button("Cancel", key="cancel_signup", use_container_width=True):
                    st.session_state.show_auth = None
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
