from pathlib import Path

import streamlit as st

from utils.navigation import init_state
from components.navbar import render_navbar
from components.auth import render_auth_panel
from views import dashboard, ai_explain, risk_customer, history

st.set_page_config(
    page_title="BankCo — Retention Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_state()


def inject_css():
    css_path = Path(__file__).parent / "styles" / "style.css"
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
    # collapse the (now-empty) sidebar toggle affordance since navigation lives in the navbar
    st.markdown(
        "<style>section[data-testid='stSidebar'] {display:none;}</style>",
        unsafe_allow_html=True,
    )


inject_css()
render_navbar()

if st.session_state.show_auth:
    render_auth_panel()
else:
    router = {
        "Dashboard": dashboard.render,
        "AI Explain": ai_explain.render,
        "Risk Customer": risk_customer.render,
        "History": history.render,
    }
    router[st.session_state.page]()
