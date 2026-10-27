"""components/cards.py — Premium stat cards, gauges, and badges for BankCo."""
import math
import streamlit as st
from components.icons import get_icon
from utils.helpers import RISK_CSS_CLASS, clean_html

ICON_CONFIGS = {
    "total":     ("rgba(59,130,246,0.14)",   "#3B82F6", "users"),
    "high":      ("rgba(239,68,68,0.14)",    "#EF4444", "user-alert"),
    "medium":    ("rgba(245,158,11,0.14)",   "#F59E0B", "alert-circle"),
    "low":       ("rgba(16,185,129,0.14)",   "#10B981", "user-check"),
    "churn":     ("rgba(239,68,68,0.14)",    "#EF4444", "trending-down"),
    "retention": ("rgba(16,185,129,0.14)",   "#10B981", "shield-check"),
    "cyan":      ("rgba(6,182,212,0.14)",    "#06B6D4", "activity"),
}


def stat_card(label: str, value: str, icon: str = None,
              risk_key: str = None, delta: str = None, delta_dir: str = None):
    """
    World-class stat card with SVG vector icons and micro-trends.
    risk_key: 'total' | 'high' | 'medium' | 'low' | 'churn' | 'retention' | 'cyan'
    """
    key = risk_key or "total"
    bg_color, fg_color, default_icon = ICON_CONFIGS.get(key, ICON_CONFIGS["total"])
    icon_name = default_icon

    delta_html = ""
    if delta:
        if delta_dir is None:
            delta_dir = "up" if (delta.startswith("+") or delta.startswith("↑")) else "down"
        arrow = "▲" if delta_dir == "up" else "▼"
        css_dir = "up" if delta_dir == "up" else "down"
        delta_html = f'<div class="bc-stat-delta {css_dir}"><span>{arrow}</span><span>{delta} vs last month</span></div>'

    icon_svg = get_icon(icon_name, size=20, color=fg_color)
    icon_html = f'<div class="bc-stat-icon-wrap" style="background:{bg_color}; color:{fg_color};">{icon_svg}</div>'

    card_markup = (
        f'<div class="bc-stat-card">'
        f'<div class="bc-stat-top"><div class="bc-stat-label">{label}</div>{icon_html}</div>'
        f'<div class="bc-stat-value">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )
    st.markdown(card_markup, unsafe_allow_html=True)


def gauge_svg(prob: float, color: str, size: str = "") -> str:
    """Circular progress ring for churn probability."""
    radius = 32
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - prob)
    pct = f"{prob * 100:.0f}%"
    
    return f"""
    <div style="position:relative; width:90px; height:90px; display:flex; align-items:center; justify-content:center;">
        <svg width="90" height="90" viewBox="0 0 80 80" style="transform:rotate(-90deg);">
            <circle cx="40" cy="40" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="7"></circle>
            <circle cx="40" cy="40" r="{radius}" fill="none" stroke="{color}" stroke-width="7"
                stroke-linecap="round"
                stroke-dasharray="{circumference:.1f}"
                stroke-dashoffset="{offset:.1f}"></circle>
        </svg>
        <div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-family:var(--bc-font-head); font-weight:700; font-size:1.1rem; color:#FFFFFF;">
            {pct}
        </div>
    </div>
    """


def badge_html(risk: str) -> str:
    cls = RISK_CSS_CLASS.get(risk, "low")
    dot_color = "#EF4444" if risk == "High" else "#F59E0B" if risk == "Medium" else "#10B981"
    badge_cls = f"bc-badge-{cls}"
    return f'<span class="{badge_cls}"><span style="width:6px; height:6px; border-radius:50%; background:{dot_color};"></span>{risk} Risk</span>'


def kpi_mini(label: str, value: str, color: str = "#3B82F6") -> str:
    """Inline mini KPI chip for dashboard header."""
    return f"""<div style="display:inline-flex; align-items:center; gap:6px; background:var(--bc-surface-raised); border:1px solid var(--bc-border-subtle); padding:4px 10px; border-radius:8px;">
        <span style="font-weight:700; font-family:var(--bc-font-head); color:{color}; font-size:0.9rem;">{value}</span>
        <span style="color:var(--bc-ink-faint); font-size:0.74rem;">{label}</span>
    </div>"""
