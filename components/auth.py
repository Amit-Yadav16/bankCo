"""components/auth.py — Authentication panel for BankCo.
Provides explicit sign in / sign up flows and never assumes an automatic logged-in state.
"""
import streamlit as st
from components.logo import render_logo_img


def render_auth_panel():
    mode = st.session_state.show_auth
    if mode not in ("signin", "signup"):
        return

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.container(border=True):
            if mode == "signin":
                st.markdown(f"""
                <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
                    <div style="margin-bottom:8px;">{render_logo_img(height=42, icon_only=True)}</div>
                    <h3 style="margin:0; font-size:1.3rem; font-weight:700; color:#FFFFFF;">Sign In</h3>
                </div>
                """, unsafe_allow_html=True)
                email = st.text_input("Email", key="signin_email", placeholder="analyst@bankco.com")
                st.text_input("Password", key="signin_pw", type="password", placeholder="••••••••")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Sign In", key="do_signin", type="primary", use_container_width=True):
                        user_name = email.split("@")[0].replace(".", " ").title() if email else "Analyst"
                        st.session_state.authed = True
                        st.session_state.user = {
                            "name": user_name,
                            "email": email or "analyst@bankco.com",
                            "role": "Risk Analyst",
                        }
                        st.session_state.show_auth = None
                        st.rerun()
                with c2:
                    if st.button("Cancel", key="cancel_signin", use_container_width=True):
                        st.session_state.show_auth = None
                        st.rerun()

                if st.button("New to BankCo? Create Account", key="switch_signup", use_container_width=True):
                    st.session_state.show_auth = "signup"
                    st.rerun()

            else:
                st.markdown(f"""
                <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
                    <div style="margin-bottom:8px;">{render_logo_img(height=42, icon_only=True)}</div>
                    <h3 style="margin:0; font-size:1.3rem; font-weight:700; color:#FFFFFF;">Create Account</h3>
                </div>
                """, unsafe_allow_html=True)
                name = st.text_input("Full Name", key="signup_name", placeholder="e.g. Sarah Connor")
                email = st.text_input("Work Email", key="signup_email", placeholder="s.connor@bankco.com")
                st.text_input("Password", key="signup_pw", type="password")
                st.text_input("Confirm Password", key="signup_pw2", type="password")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Create Account", key="do_signup", type="primary", use_container_width=True):
                        st.session_state.authed = True
                        st.session_state.user = {
                            "name": name if name else "Analyst",
                            "email": email if email else "analyst@bankco.com",
                            "role": "Risk Analyst",
                        }
                        st.session_state.show_auth = None
                        st.rerun()
                with c2:
                    if st.button("Cancel", key="cancel_signup", use_container_width=True):
                        st.session_state.show_auth = None
                        st.rerun()

                if st.button("Already have an account? Sign In", key="switch_signin", use_container_width=True):
                    st.session_state.show_auth = "signin"
                    st.rerun()
