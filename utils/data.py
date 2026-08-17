"""Customer data: synthetic demo generator + a forgiving CSV loader.

`load_customers` is the seam between "whatever CSV the bank uploads" and the
rest of the app. It keeps any column whose name it recognizes (see
COLUMN_ALIASES) and fills in the rest synthetically, so the dashboard never
breaks on an unfamiliar schema. Update COLUMN_ALIASES with your real
dataset's column names when you plug in production data.
"""

import numpy as np
import pandas as pd

# Map from "what BankCo needs" -> list of likely real-world column names.
COLUMN_ALIASES = {
    "CustomerID": ["CustomerID", "customer_id", "id"],
    "CustomerType": ["CustomerType", "segment", "customer_type"],
    "Tenure": ["Tenure", "tenure_months", "tenure"],
    "MonthlyCharges": ["MonthlyCharges", "monthly_spend", "monthly_charges"],
    "TotalSpend": ["TotalSpend", "total_charges", "total_spend"],
    "TransactionFrequency": ["TransactionFrequency", "txn_per_month", "transactions"],
    "NumProducts": ["NumProducts", "num_products", "products"],
    "SupportTickets": ["SupportTickets", "support_tickets", "complaints"],
    "InactivityMonths": ["InactivityMonths", "inactive_months", "days_inactive"],
}

CUSTOMER_TYPES = ["Retail", "Premium", "Business", "Student"]


def generate_synthetic_customers(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "CustomerID": [f"BC-{100000 + i}" for i in range(n)],
        "CustomerType": rng.choice(CUSTOMER_TYPES, size=n, p=[0.5, 0.2, 0.15, 0.15]),
        "Tenure": rng.integers(1, 121, size=n),
        "MonthlyCharges": np.round(rng.normal(65, 28, size=n).clip(10, 260), 2),
        "TransactionFrequency": rng.integers(0, 40, size=n),
        "NumProducts": rng.integers(1, 6, size=n),
        "SupportTickets": rng.poisson(1.1, size=n),
        "InactivityMonths": rng.choice(
            [0, 1, 2, 3, 4, 5, 6], size=n, p=[0.42, 0.18, 0.12, 0.1, 0.08, 0.06, 0.04]
        ),
    })
    df["TotalSpend"] = np.round(df["MonthlyCharges"] * df["Tenure"] * rng.uniform(0.85, 1.0, size=n), 2)
    return df


def load_customers(uploaded_file) -> pd.DataFrame:
    """Read an uploaded CSV/Excel, map recognizable columns, synthesize the
    rest. Falls back to a full synthetic set if the file can't be parsed."""
    try:
        if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
            raw = pd.read_excel(uploaded_file)
        else:
            raw = pd.read_csv(uploaded_file)
    except Exception:
        return generate_synthetic_customers()

    n = len(raw)
    if n == 0:
        return generate_synthetic_customers()

    mapped = {}
    lower_cols = {c.lower(): c for c in raw.columns}
    for target, aliases in COLUMN_ALIASES.items():
        found = next((lower_cols[a.lower()] for a in aliases if a.lower() in lower_cols), None)
        if found is not None:
            mapped[target] = raw[found]

    synthetic = generate_synthetic_customers(n)
    out = synthetic.copy()
    for col, series in mapped.items():
        out[col] = series.reset_index(drop=True).values[:n]

    return out
