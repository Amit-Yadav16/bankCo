import math

import streamlit as st

from utils.helpers import RISK_CSS_CLASS


def stat_card(label, value, icon, risk_key=None, delta=None):
    risk_class = f"risk-{risk_key}" if risk_key else ""
    delta_html = ""
    if delta:
        arrow = "▲" if delta.startswith("+") else "▼"
        cls = "up" if delta.startswith("+") else "down"
        delta_html = f'<div class="bc-stat-delta {cls}">{arrow} {delta} vs last cycle</div>'
    st.markdown(
        f"""<div class="bc-card bc-card-hover bc-stat-card {risk_class}">
            <div class="bc-stat-top">
                <div class="bc-stat-label">{label}</div>
                <div class="bc-stat-icon">{icon}</div>
            </div>
            <div class="bc-stat-value">{value}</div>
            {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )


def gauge_svg(prob: float, color: str, size: str = "") -> str:
    """A small circular progress ring used as BankCo's churn-probability motif."""
    radius = 30
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - prob)
    pct = f"{prob * 100:.0f}%"
    size_class = f"bc-gauge {size}".strip()
    return f"""
    <div class="{size_class}">
        <svg width="100%" height="100%" viewBox="0 0 70 70">
            <circle class="bc-gauge-track" cx="35" cy="35" r="{radius}"></circle>
            <circle class="bc-gauge-value" cx="35" cy="35" r="{radius}"
                stroke="{color}"
                stroke-dasharray="{circumference:.1f}"
                stroke-dashoffset="{offset:.1f}"></circle>
        </svg>
        <div class="bc-gauge-label">{pct}</div>
    </div>
    """


def badge_html(risk: str) -> str:
    cls = RISK_CSS_CLASS.get(risk, "low")
    return f'<span class="bc-badge {cls}"><span class="bc-dot {cls}"></span>{risk} Risk</span>'
