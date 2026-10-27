from pathlib import Path

import streamlit as st

from utils.navigation import init_state
from components.navbar import render_navbar, render_sidebar
from components.auth import render_auth_panel
from views import landing, dashboard, ai_explain, risk_customer, history, upload_view

st.set_page_config(
    page_title="BankCo — Smarter Banking",
    page_icon="assets/logo_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_state()


def inject_css():
    css_path = Path(__file__).parent / "styles" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    # Collapse the Streamlit sidebar and clean up chrome
    st.markdown(
        """<style>
        section[data-testid='stSidebar'] {display:none;}
        div[data-testid='stToolbar'] {display:none;}
        </style>""",
        unsafe_allow_html=True,
    )


inject_css()
render_navbar()

if st.session_state.show_auth:
    render_auth_panel()

elif st.session_state.page == "Landing":
    landing.render()

else:
    # ── Full-Width Direct Frontend Workspace (No cramped sidebar) ──
    st.markdown('<div class="bc-content" style="padding: 0.5rem 0 2.5rem 0;">', unsafe_allow_html=True)
    router = {
        "Dashboard":     dashboard.render,
        "AI Explain":    ai_explain.render,
        "Risk Customer": risk_customer.render,
        "History":       history.render,
        "Upload":        upload_view.render,
    }
    router.get(st.session_state.page, dashboard.render)()
    st.markdown("</div>", unsafe_allow_html=True)
