"""Everything the UI needs from "the model" lives behind these three
functions. Each one is currently a transparent, rule-based placeholder so
the app runs end-to-end with zero training. Replace the body of each
function with your real model/SHAP explainer/recommendation logic — keep
the same inputs/outputs and no other file needs to change.
"""

import numpy as np
import pandas as pd

FEATURE_LABELS = {
    "InactivityMonths": "Months of inactivity",
    "TransactionFrequency": "Transaction frequency",
    "NumProducts": "Active products",
    "Tenure": "Customer tenure",
    "SupportTickets": "Support tickets",
    "MonthlyCharges": "Monthly spend",
}


def predict_churn(df: pd.DataFrame) -> np.ndarray:
    """Return a churn probability in [0, 1] for every row of df.

    # PLACEHOLDER — replace me
    Swap this out for e.g.:
        proba = trained_model.predict_proba(feature_matrix)[:, 1]
        return proba
    The scoring below is a deliberately readable weighted rule, not a
    trained model — it exists only so the UI has realistic numbers to
    render before a real model is wired in.
    """
    inactivity = (df["InactivityMonths"].clip(0, 6) / 6)
    low_txn = 1 - (df["TransactionFrequency"].clip(0, 25) / 25)
    tenure_protect = 1 - (df["Tenure"].clip(0, 60) / 60)
    few_products = 1 - ((df["NumProducts"].clip(1, 5) - 1) / 4)
    tickets = (df["SupportTickets"].clip(0, 5) / 5)

    score = (
        0.34 * inactivity
        + 0.24 * low_txn
        + 0.18 * few_products
        + 0.14 * tenure_protect
        + 0.10 * tickets
    )
    noise = np.random.default_rng(7).normal(0, 0.03, size=len(df))
    return np.clip(score + noise, 0.01, 0.99)


def risk_level(prob: float) -> str:
    if prob >= 0.6:
        return "High"
    if prob >= 0.3:
        return "Medium"
    return "Low"


def explain_customer(row: pd.Series) -> list[dict]:
    """Return per-feature contributions for one customer, most impactful
    first. Each item: {feature, label, impact (0-1 magnitude), direction
    ('increases'|'decreases')}.

    # PLACEHOLDER — replace me
    Swap this out for a real local explanation, e.g.:
        shap_values = explainer(feature_row)
        return [{"feature": f, "impact": abs(v), "direction": "increases" if v > 0 else "decreases"} ...]
    """
    contributions = {
        "InactivityMonths": (row["InactivityMonths"] / 6) - 0.35,
        "TransactionFrequency": 0.45 - (row["TransactionFrequency"] / 25),
        "NumProducts": 0.4 - ((row["NumProducts"] - 1) / 4),
        "Tenure": 0.3 - (row["Tenure"] / 60),
        "SupportTickets": (row["SupportTickets"] / 5) - 0.15,
    }
    items = []
    for feature, val in contributions.items():
        items.append({
            "feature": feature,
            "label": FEATURE_LABELS.get(feature, feature),
            "impact": min(abs(float(val)), 1.0),
            "direction": "increases" if val > 0 else "decreases",
        })
    items.sort(key=lambda d: d["impact"], reverse=True)
    return items


def recommend_action(row: pd.Series, factors: list[dict]) -> dict:
    """Return {"action": str, "reason": str} for the retention team.

    # PLACEHOLDER — replace me
    Swap this out for your own rules engine or an LLM call that takes the
    customer profile + top factors and drafts a tailored recommendation.
    """
    top = factors[0]["feature"] if factors else None

    if top == "InactivityMonths" and row["InactivityMonths"] >= 3:
        action = "Offer a personalised relationship-manager call and a re-engagement product benefit."
        reason = "The customer's activity has dropped sharply and re-engagement outreach tends to recover this segment."
    elif top == "TransactionFrequency":
        action = "Send a targeted cashback or fee-waiver offer tied to their most-used product."
        reason = "Declining transaction frequency responds well to a short-term usage incentive."
    elif top == "NumProducts":
        action = "Recommend a bundled product (savings + card) with an introductory rate."
        reason = "Customers with a single active product churn more often; cross-sell increases stickiness."
    elif row["SupportTickets"] >= 2:
        action = "Escalate to a senior support agent for a proactive resolution call."
        reason = "Repeated support contact without resolution is a strong churn precursor."
    else:
        action = "Continue standard engagement; monitor next billing cycle."
        reason = "No single dominant risk factor — behaviour is broadly in line with retained customers."

    return {"action": action, "reason": reason}
