import plotly.graph_objects as go
import pandas as pd

ACCENT = "#2B4CE0"
RISK_COLORS = {"High": "#E0403A", "Medium": "#C98A12", "Low": "#1E9A63"}

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#4B5266", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


def risk_distribution_donut(counts: dict):
    fig = go.Figure(data=[go.Pie(
        labels=list(counts.keys()),
        values=list(counts.values()),
        hole=0.62,
        marker=dict(colors=[RISK_COLORS[k] for k in counts.keys()]),
        textinfo="percent",
        textfont=dict(size=12, color="white"),
    )])
    fig.update_layout(**BASE_LAYOUT, height=280, title="Risk Distribution")
    return fig


def churn_probability_hist(probs):
    fig = go.Figure(data=[go.Histogram(
        x=probs, nbinsx=24, marker=dict(color=ACCENT, line=dict(width=0)),
    )])
    fig.update_layout(**BASE_LAYOUT, height=280, title="Churn Probability Distribution",
                       xaxis_title="Predicted probability", yaxis_title="Customers")
    return fig


def segment_bar(df: pd.DataFrame):
    grp = df.groupby("CustomerType")["ChurnProbability"].mean().sort_values(ascending=False)
    fig = go.Figure(data=[go.Bar(
        x=grp.index, y=grp.values, marker=dict(color=ACCENT),
        text=[f"{v*100:.0f}%" for v in grp.values], textposition="outside",
    )])
    fig.update_layout(**BASE_LAYOUT, height=280, title="Avg. Churn Probability by Segment",
                       yaxis_title="Avg. probability", yaxis_tickformat=".0%")
    return fig


def top_factors_bar(factor_means: pd.Series):
    fig = go.Figure(data=[go.Bar(
        x=factor_means.values, y=factor_means.index, orientation="h",
        marker=dict(color=ACCENT),
    )])
    fig.update_layout(**BASE_LAYOUT, height=280, title="Top Churn Factors (portfolio-wide)",
                       xaxis_title="Avg. impact")
    return fig
