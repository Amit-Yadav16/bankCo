def fmt_pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def fmt_money(x: float) -> str:
    return f"${x:,.0f}"


def fmt_int(x) -> str:
    return f"{int(x):,}"


RISK_COLORS = {
    "High": "#FF4757",
    "Medium": "#FFA502",
    "Low": "#2ED573",
}

RISK_CSS_CLASS = {"High": "high", "Medium": "medium", "Low": "low"}


def clean_html(s: str) -> str:
    """Strips all leading and trailing whitespace from every line to eliminate CommonMark code block parsing."""
    return " ".join(line.strip() for line in str(s).splitlines() if line.strip())
