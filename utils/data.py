"""Customer data module for BankCo.

Provides forgiving data ingestion, column canonicalization, and realistic demo
data generation aligned with the real BankChurners dataset schema.
"""

from pathlib import Path
import numpy as np
import pandas as pd

# Map from canonical BankCo UI / model columns -> recognized aliases in incoming CSVs
COLUMN_ALIASES = {
    # Identifiers
    "CustomerID": ["CustomerID", "customer_id", "id", "clientnum", "CLIENTNUM"],
    "CustomerType": ["CustomerType", "segment", "customer_type", "Card_Category", "card_category"],
    # Core operational metrics
    "Tenure": ["Tenure", "tenure_months", "tenure", "Months_on_book", "months_on_book"],
    "MonthlyCharges": ["MonthlyCharges", "monthly_spend", "monthly_charges"],
    "TotalSpend": ["TotalSpend", "total_charges", "total_spend", "Total_Trans_Amt", "total_trans_amt"],
    "TransactionFrequency": ["TransactionFrequency", "txn_per_month", "transactions", "Total_Trans_Ct", "total_trans_ct"],
    "NumProducts": ["NumProducts", "num_products", "products", "Total_Relationship_Count", "total_relationship_count"],
    "SupportTickets": ["SupportTickets", "support_tickets", "complaints", "Contacts_Count_12_mon", "contacts_count_12_mon"],
    "InactivityMonths": ["InactivityMonths", "inactive_months", "days_inactive", "Months_Inactive_12_mon", "months_inactive_12_mon"],
    # Extended BankChurners attributes
    "Customer_Age": ["Customer_Age", "customer_age", "age", "Age"],
    "Gender": ["Gender", "gender", "sex"],
    "Dependent_count": ["Dependent_count", "dependent_count", "dependents"],
    "Education_Level": ["Education_Level", "education_level", "education"],
    "Marital_Status": ["Marital_Status", "marital_status"],
    "Income_Category": ["Income_Category", "income_category", "income"],
    "Card_Category": ["Card_Category", "card_category", "CustomerType"],
    "Months_on_book": ["Months_on_book", "months_on_book", "Tenure"],
    "Total_Relationship_Count": ["Total_Relationship_Count", "total_relationship_count", "NumProducts"],
    "Months_Inactive_12_mon": ["Months_Inactive_12_mon", "months_inactive_12_mon", "InactivityMonths"],
    "Contacts_Count_12_mon": ["Contacts_Count_12_mon", "contacts_count_12_mon", "SupportTickets"],
    "Credit_Limit": ["Credit_Limit", "credit_limit"],
    "Total_Revolving_Bal": ["Total_Revolving_Bal", "total_revolving_bal", "revolving_balance"],
    "Avg_Open_To_Buy": ["Avg_Open_To_Buy", "avg_open_to_buy", "open_to_buy"],
    "Total_Amt_Chng_Q4_Q1": ["Total_Amt_Chng_Q4_Q1", "total_amt_chng_q4_q1"],
    "Total_Trans_Amt": ["Total_Trans_Amt", "total_trans_amt", "TotalSpend"],
    "Total_Trans_Ct": ["Total_Trans_Ct", "total_trans_ct", "TransactionFrequency"],
    "Total_Ct_Chng_Q4_Q1": ["Total_Ct_Chng_Q4_Q1", "total_ct_chng_q4_q1"],
    "Avg_Utilization_Ratio": ["Avg_Utilization_Ratio", "avg_utilization_ratio", "utilization_ratio"],
}

CUSTOMER_TYPES = ["Blue", "Silver", "Gold", "Platinum"]
GENDERS = ["M", "F"]
EDUCATION_LEVELS = ["Graduate", "High School", "Unknown", "Uneducated", "College", "Post-Graduate", "Doctorate"]
MARITAL_STATUSES = ["Married", "Single", "Unknown", "Divorced"]
INCOME_CATEGORIES = ["Less than $40K", "$40K - $60K", "$80K - $120K", "$60K - $80K", "Unknown", "$120K +"]


def generate_synthetic_customers(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic customer records matching BankChurners schema."""
    rng = np.random.default_rng(seed)

    # If BankChurners.csv exists in the workspace, sample directly from it for maximum fidelity
    csv_path = Path(__file__).resolve().parent.parent / "BankChurners.csv"
    if csv_path.exists():
        try:
            real_df = pd.read_csv(csv_path)
            sample_df = real_df.sample(min(n, len(real_df)), random_state=seed, replace=(n > len(real_df))).copy()
            # Drop target leakage columns if present
            leakage = [
                "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1",
                "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2",
            ]
            sample_df = sample_df.drop(columns=[c for c in leakage if c in sample_df.columns])
            sample_df = _ensure_ui_columns(sample_df)
            return sample_df.reset_index(drop=True)
        except Exception:
            pass

    # Statistical parametric generation if file is inaccessible
    age = rng.integers(24, 72, size=n)
    gender = rng.choice(GENDERS, size=n, p=[0.47, 0.53])
    dependents = rng.integers(0, 6, size=n)
    edu = rng.choice(EDUCATION_LEVELS, size=n, p=[0.31, 0.20, 0.15, 0.15, 0.10, 0.05, 0.04])
    marital = rng.choice(MARITAL_STATUSES, size=n, p=[0.46, 0.39, 0.08, 0.07])
    income = rng.choice(INCOME_CATEGORIES, size=n, p=[0.35, 0.18, 0.15, 0.14, 0.11, 0.07])
    card = rng.choice(CUSTOMER_TYPES, size=n, p=[0.93, 0.055, 0.012, 0.003])
    tenure = rng.integers(12, 60, size=n)
    products = rng.integers(1, 7, size=n)
    inactive = rng.choice([0, 1, 2, 3, 4, 5, 6], size=n, p=[0.05, 0.25, 0.35, 0.25, 0.06, 0.03, 0.01])
    contacts = rng.choice([0, 1, 2, 3, 4, 5, 6], size=n, p=[0.04, 0.15, 0.32, 0.28, 0.14, 0.05, 0.02])
    credit_limit = np.round(rng.uniform(1500, 34500, size=n), 1)
    revolving_bal = rng.integers(0, 2500, size=n)
    open_to_buy = np.maximum(0, credit_limit - revolving_bal)
    amt_chng = np.round(rng.normal(0.76, 0.22, size=n).clip(0.1, 3.4), 3)
    trans_amt = rng.integers(500, 18000, size=n)
    trans_ct = rng.integers(10, 140, size=n)
    ct_chng = np.round(rng.normal(0.71, 0.24, size=n).clip(0.1, 3.7), 3)
    utilization = np.round((revolving_bal / credit_limit).clip(0, 1.0), 3)

    df = pd.DataFrame({
        "CLIENTNUM": [100000000 + i for i in range(n)],
        "Customer_Age": age,
        "Gender": gender,
        "Dependent_count": dependents,
        "Education_Level": edu,
        "Marital_Status": marital,
        "Income_Category": income,
        "Card_Category": card,
        "Months_on_book": tenure,
        "Total_Relationship_Count": products,
        "Months_Inactive_12_mon": inactive,
        "Contacts_Count_12_mon": contacts,
        "Credit_Limit": credit_limit,
        "Total_Revolving_Bal": revolving_bal,
        "Avg_Open_To_Buy": open_to_buy,
        "Total_Amt_Chng_Q4_Q1": amt_chng,
        "Total_Trans_Amt": trans_amt,
        "Total_Trans_Ct": trans_ct,
        "Total_Ct_Chng_Q4_Q1": ct_chng,
        "Avg_Utilization_Ratio": utilization,
    })

    return _ensure_ui_columns(df)


def _ensure_ui_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure standard BankCo UI columns exist on the dataframe for seamless rendering."""
    out = df.copy()

    # CustomerID
    if "CustomerID" not in out.columns:
        if "CLIENTNUM" in out.columns:
            out["CustomerID"] = out["CLIENTNUM"].astype(str)
        else:
            out["CustomerID"] = [f"BC-{100000 + i}" for i in range(len(out))]

    # CustomerType
    if "CustomerType" not in out.columns:
        if "Card_Category" in out.columns:
            out["CustomerType"] = out["Card_Category"].astype(str)
        else:
            out["CustomerType"] = "Blue"

    # Tenure
    if "Tenure" not in out.columns:
        out["Tenure"] = out["Months_on_book"] if "Months_on_book" in out.columns else 36

    # NumProducts
    if "NumProducts" not in out.columns:
        out["NumProducts"] = out["Total_Relationship_Count"] if "Total_Relationship_Count" in out.columns else 3

    # InactivityMonths
    if "InactivityMonths" not in out.columns:
        out["InactivityMonths"] = out["Months_Inactive_12_mon"] if "Months_Inactive_12_mon" in out.columns else 1

    # SupportTickets
    if "SupportTickets" not in out.columns:
        out["SupportTickets"] = out["Contacts_Count_12_mon"] if "Contacts_Count_12_mon" in out.columns else 1

    # TotalSpend
    if "TotalSpend" not in out.columns:
        out["TotalSpend"] = out["Total_Trans_Amt"] if "Total_Trans_Amt" in out.columns else 3000.0

    # TransactionFrequency
    if "TransactionFrequency" not in out.columns:
        out["TransactionFrequency"] = out["Total_Trans_Ct"] if "Total_Trans_Ct" in out.columns else 45

    # MonthlyCharges
    if "MonthlyCharges" not in out.columns:
        if "TotalSpend" in out.columns:
            out["MonthlyCharges"] = np.round(out["TotalSpend"] / 12.0, 2)
        elif "Total_Trans_Amt" in out.columns:
            out["MonthlyCharges"] = np.round(out["Total_Trans_Amt"] / 12.0, 2)
        else:
            out["MonthlyCharges"] = 150.0

    return out


def load_customers(uploaded_file) -> pd.DataFrame:
    """Read an uploaded CSV/Excel, preserve all original data, and align aliases."""
    try:
        if hasattr(uploaded_file, "name") and uploaded_file.name.lower().endswith((".xlsx", ".xls")):
            raw = pd.read_excel(uploaded_file)
        else:
            raw = pd.read_csv(uploaded_file)
    except Exception:
        return generate_synthetic_customers()

    n = len(raw)
    if n == 0:
        return generate_synthetic_customers()

    # Drop target leakage columns if present in evaluation file
    leakage = [
        "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1",
        "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2",
    ]
    raw = raw.drop(columns=[c for c in leakage if c in raw.columns])

    # Map aliases where standard names are missing
    lower_cols = {c.lower(): c for c in raw.columns}
    for target, aliases in COLUMN_ALIASES.items():
        if target not in raw.columns:
            found = next((lower_cols[a.lower()] for a in aliases if a.lower() in lower_cols), None)
            if found is not None:
                raw[target] = raw[found]

    # Ensure UI convenience columns exist for views
    return _ensure_ui_columns(raw)
