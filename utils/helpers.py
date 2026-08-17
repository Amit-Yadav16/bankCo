def fmt_pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def fmt_money(x: float) -> str:
    return f"${x:,.0f}"


def fmt_int(x) -> str:
    return f"{int(x):,}"


RISK_COLORS = {
    "High": "#E0403A",
    "Medium": "#C98A12",
    "Low": "#1E9A63",
}

RISK_CSS_CLASS = {"High": "high", "Medium": "medium", "Low": "low"}
