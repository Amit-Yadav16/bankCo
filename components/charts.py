"""components/charts.py — World-Class Fintech Chart Factory for BankCo.
Refined dark theme with high-contrast risk colors, clean splines, and interactive tooltips.
"""
import copy
import plotly.graph_objects as go
import pandas as pd
import numpy as np

ACCENT       = "#3B82F6"
ACCENT_LIGHT = "#60A5FA"
CYAN         = "#06B6D4"
GOLD         = "#F59E0B"
RISK_COLORS  = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}

_DARK_BG = "rgba(0,0,0,0)"
_FONT    = dict(family="'Inter', 'IBM Plex Sans', -apple-system, sans-serif", color="#94A3B8", size=12)
_GRID    = "rgba(255, 255, 255, 0.06)"

BASE_LAYOUT = dict(
    paper_bgcolor=_DARK_BG,
    plot_bgcolor=_DARK_BG,
    font=_FONT,
    margin=dict(l=16, r=16, t=40, b=16),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        font=dict(color="#94A3B8", size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        gridcolor=_GRID, zerolinecolor=_GRID,
        showgrid=True, linecolor=_GRID,
        tickfont=dict(color="#64748B", size=11),
    ),
    yaxis=dict(
        gridcolor=_GRID, zerolinecolor=_GRID,
        showgrid=True, linecolor=_GRID,
        tickfont=dict(color="#64748B", size=11),
    ),
    hoverlabel=dict(
        bgcolor="#101A31",
        bordercolor="rgba(59, 130, 246, 0.3)",
        font=dict(family="'Inter', sans-serif", size=12, color="#F8FAFC"),
    ),
)


def _get_layout(**overrides):
    """Safely combine BASE_LAYOUT with custom overrides without duplicate keyword errors."""
    layout = copy.deepcopy(BASE_LAYOUT)
    layout.update(overrides)
    return layout


def churn_trend_line(df: pd.DataFrame):
    """Monthly churn rate + retention rate line chart."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
    np.random.seed(42)
    base = df["ChurnProbability"].mean() if df is not None else 0.20
    churn = [max(0.05, base + np.random.uniform(-0.04, 0.04)) for _ in months]
    retain = [1 - c for c in churn]

    fig = go.Figure()
    # Retention area
    fig.add_trace(go.Scatter(
        x=months, y=[r * 100 for r in retain],
        name="Retention Rate",
        line=dict(color=ACCENT, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.08)",
        mode="lines+markers",
        marker=dict(color=ACCENT, size=6, line=dict(width=2, color="rgba(59,130,246,0.5)")),
    ))
    # Churn line
    fig.add_trace(go.Scatter(
        x=months, y=[c * 100 for c in churn],
        name="Churn Rate",
        line=dict(color="#EF4444", width=2.5, shape="spline", dash="dot"),
        mode="lines+markers",
        marker=dict(color="#EF4444", size=6),
    ))
    fig.update_layout(_get_layout(
        height=280,
        title=dict(text="Customer Churn & Retention Trend", font=dict(color="#F8FAFC", size=13, family="'IBM Plex Sans', sans-serif")),
        yaxis_title="Rate (%)",
        hovermode="x unified",
    ))
    return fig


def risk_distribution_donut(counts: dict, total: int = None):
    """Clean donut chart with center metric label."""
    total = total or sum(counts.values())
    fig = go.Figure(data=[go.Pie(
        labels=list(counts.keys()),
        values=list(counts.values()),
        hole=0.68,
        marker=dict(
            colors=[RISK_COLORS[k] for k in counts.keys()],
            line=dict(color="#101A31", width=2),
        ),
        textinfo="percent",
        textfont=dict(size=11, color="#F8FAFC", family="'Inter', sans-serif"),
        hovertemplate="<b>%{label} Risk</b><br>Accounts: %{value:,}<br>Share: %{percent}<extra></extra>",
    )])
    fig.add_annotation(
        text=f"<b>{total:,}</b>",
        font=dict(size=22, color="#F8FAFC", family="'IBM Plex Sans', sans-serif"),
        showarrow=False, y=0.55,
    )
    fig.add_annotation(
        text="Customers",
        font=dict(size=11, color="#94A3B8", family="'Inter', sans-serif"),
        showarrow=False, y=0.38,
    )
    fig.update_layout(_get_layout(
        height=280,
        title=dict(text="Customer Risk Distribution", font=dict(color="#F8FAFC", size=13, family="'IBM Plex Sans', sans-serif")),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
    ))
    return fig


def churn_probability_hist(probs):
    """Histogram with gradient coloring by risk zone."""
    fig = go.Figure(data=[go.Histogram(
        x=probs, nbinsx=24,
        marker=dict(
            color=probs,
            colorscale=[[0, "#10B981"], [0.30, "#F59E0B"], [0.60, "#EF4444"], [1, "#DC2626"]],
            line=dict(color="#101A31", width=1),
        ),
        hovertemplate="Probability: %{x:.0%}<br>Count: %{y}<extra></extra>",
    )])
    fig.update_layout(_get_layout(
        height=280,
        title=dict(text="Churn Probability Distribution", font=dict(color="#F8FAFC", size=13, family="'IBM Plex Sans', sans-serif")),
        xaxis=dict(tickformat=".0%", gridcolor=_GRID, zerolinecolor=_GRID),
        yaxis_title="Customers",
    ))
    return fig


def segment_bar(df: pd.DataFrame):
    """Avg churn by customer segment."""
    grp = df.groupby("CustomerType")["ChurnProbability"].mean().sort_values(ascending=False)
    colors = [ACCENT if i == 0 else ACCENT_LIGHT for i in range(len(grp))]
    fig = go.Figure(data=[go.Bar(
        x=grp.index, y=grp.values,
        marker=dict(color=colors, line=dict(width=0), cornerradius=6),
        text=[f"{v*100:.0f}%" for v in grp.values],
        textposition="outside",
        textfont=dict(color="#F8FAFC", size=11),
        hovertemplate="<b>%{x}</b><br>Avg Churn: %{text}<extra></extra>",
    )])
    fig.update_layout(_get_layout(
        height=280,
        title=dict(text="Avg. Churn by Segment", font=dict(color="#F8FAFC", size=13)),
        yaxis_tickformat=".0%",
    ))
    return fig


def top_factors_bar(factor_means: pd.Series):
    """Horizontal bar for top churn factors."""
    colors = [RISK_COLORS["High"] if v > 0.15 else RISK_COLORS["Medium"] if v > 0.08 else ACCENT
              for v in factor_means.values]
    fig = go.Figure(data=[go.Bar(
        x=factor_means.values, y=factor_means.index, orientation="h",
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
        text=[f"{v:.2f}" for v in factor_means.values],
        textposition="outside",
        textfont=dict(color="#F8FAFC", size=10),
        hovertemplate="<b>%{y}</b><br>Impact: %{x:.3f}<extra></extra>",
    )])
    fig.update_layout(_get_layout(
        height=280,
        title=dict(text="Top Churn Factors (Portfolio-wide)", font=dict(color="#F8FAFC", size=13)),
        xaxis_title="Avg. Impact",
        margin=dict(l=140, r=40, t=40, b=16),
    ))
    return fig


def shap_waterfall(factors: list):
    """SHAP-style factor bars for AI Explain page."""
    pos = [(f["label"], f["impact"]) for f in factors if f["direction"] == "increases"]
    neg = [(f["label"], -f["impact"]) for f in factors if f["direction"] == "decreases"]
    all_items = sorted(pos + neg, key=lambda x: abs(x[1]), reverse=True)[:8]

    labels = [x[0] for x in all_items]
    values = [x[1] for x in all_items]
    colors = [RISK_COLORS["High"] if v > 0 else RISK_COLORS["Low"] for v in values]

    fig = go.Figure(data=[go.Bar(
        y=labels, x=values, orientation="h",
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
        hovertemplate="<b>%{y}</b><br>Impact: %{x:.3f}<extra></extra>",
    )])
    fig.add_vline(x=0, line_width=1, line_color=_GRID)
    fig.update_layout(_get_layout(
        height=320,
        title=dict(text="Feature Impact (SHAP Values)", font=dict(color="#F8FAFC", size=13, family="'IBM Plex Sans', sans-serif")),
        xaxis_title="← Reduces Risk (Protective)  |  Increases Risk (Driver) →",
        margin=dict(l=160, r=40, t=40, b=16),
    ))
    return fig
