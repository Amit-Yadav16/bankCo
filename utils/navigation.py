"""utils/navigation.py — Session state router and navigation management for BankCo."""
import streamlit as st

PAGES = ["Landing", "Dashboard", "AI Explain", "Risk Customer", "History", "Upload"]

DEFAULTS = {
    "page": "Landing",
    "authed": False,
    "show_auth": None,          # None | "signin" | "signup"
    "show_profile": False,
    "customers": None,          # DataFrame once uploaded/generated
    "predicted": False,
    "pipeline_status": "idle",  # idle | running | done
    "selected_customer": None,
    "uploaded_filename": None,
    "history": [],               # list of past-session summary dicts
    "user": None,               # None by default — never assume a logged-in user
}


def init_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(page_name: str):
    st.session_state.page = page_name
    st.session_state.show_profile = False
    st.session_state.show_auth = None


def open_customer(customer_id):
    st.session_state.selected_customer = customer_id
    st.session_state.page = "AI Explain"
