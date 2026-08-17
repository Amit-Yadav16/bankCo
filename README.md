# BankCo — Customer Churn Prediction & Retention Dashboard

A production-styled Streamlit frontend for a bank churn prediction & retention
system. The interface, navigation, and every page described in the design
brief are fully built. The **prediction / explainability / recommendation
logic is intentionally isolated** in `utils/model.py` so you can drop in your
own trained model without touching any UI code.

## Run it

```bash
cd bankco
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints. Use **+ Upload Customer File** on
the Dashboard to load a CSV, or click **Load Demo Dataset** to explore the
app immediately with synthetic customers.

## Plugging in your real dataset & model

Everything the UI needs from "the model" goes through three functions in
`utils/model.py`. Right now they're implemented with transparent, rule-based
placeholder logic (clearly marked `# PLACEHOLDER — replace me`) so the whole
app runs standalone with no training step required. Replace the body of each
function and the rest of the app (tables, charts, gauges, AI Explain page,
retention copy) keeps working unchanged:

- `predict_churn(df)` → swap in `model.predict_proba(X)[:, 1]`
- `explain_customer(row, df)` → swap in a real SHAP `Explainer` and return
  the same `[{feature, impact, direction}, ...]` shape
- `recommend_action(row, factors)` → swap in your own rules/LLM call, same
  `{action, reason}` return shape

To use your own data, upload a CSV from the **Dashboard** page — the loader
in `utils/data.py::load_customers` keeps columns that match its expected
schema and fills in sane synthetic defaults for anything missing, so the
dashboard never breaks on an unfamiliar file. Update `COLUMN_ALIASES` there
once you know your dataset's real column names, to map e.g. `tenure_months`
→ `Tenure`.

## Structure

```text
bankco/
├── app.py                    entry point, session-state router, global CSS
├── views/                    one module per page (imported, not auto-routed)
│   ├── dashboard.py
│   ├── ai_explain.py
│   ├── risk_customer.py
│   └── history.py
├── components/                reusable UI pieces
│   ├── navbar.py
│   ├── cards.py
│   ├── charts.py
│   ├── customer_table.py
│   ├── upload.py
│   └── auth.py
├── styles/
│   └── style.css               all custom styling (design tokens at the top)
├── utils/
│   ├── navigation.py            session-state routing helpers
│   ├── helpers.py               formatting, risk bucketing
│   ├── data.py                   synthetic data + CSV loader
│   └── model.py                   ← plug your real model in here
└── assets/
```

Note: page modules live in `views/`, not `pages/`, even though the original
brief sketch used `pages/`. Streamlit auto-generates a default sidebar
navigation for any folder literally named `pages/` next to the entry script,
which would fight with the custom navbar/session-state routing the brief
asks for. `views/` keeps the same separation of concerns without that
collision — see `app.py` for the router.
