# BankCo — Customer Churn Prediction & Retention System

BankCo is an enterprise-grade customer churn intelligence platform built with Python, scikit-learn, and Streamlit. It pairs a genuinely trained, serialized machine learning pipeline with local SHAP explainability and interactive retention intelligence workflows.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Core dependencies:
- `streamlit >= 1.32` — Interactive dashboard and reactive UI
- `scikit-learn >= 1.3.0` — Production Pipeline, ColumnTransformer, Random Forest
- `shap >= 0.42.0` — Local TreeExplainer attribution
- `plotly >= 5.18` — Portfolio analytics and risk distribution visualizations
- `pandas >= 2.0`, `numpy >= 1.24`, `joblib >= 1.3.0`, `matplotlib >= 3.7.0`

---

## 📁 Dataset & Configuration

Place your labeled customer dataset directly in the project root:
- **Default Path:** `BankChurners.csv` (10,127 records)
- **Target Column:** `Attrition_Flag`
  - **Positive Class (Churn):** `Attrited Customer` (1,627 records / 16.07%)
  - **Negative Class (Retained):** `Existing Customer` (8,500 records / 83.93%)
- **Identifiers Dropped:** `CLIENTNUM`
- **Data Leakage Columns Removed:**
  - `Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1`
  - `Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2`

---

## 🏋️‍♂️ Model Training & Evaluation

To train, cross-validate, and evaluate the production model pipeline from scratch:

```bash
python train_model.py
```

### Reproducible Training Pipeline:
1. **Stratified Split:** 80% train (8,101 rows) / 20% held-out test (2,026 rows) with fixed random seed (`42`).
2. **Preprocessing:** Strict `ColumnTransformer` fitted strictly on train data to prevent data leakage:
   - Numerical: `StandardScaler` on 14 numerical features.
   - Categorical: `OneHotEncoder(handle_unknown='ignore')` on 5 categorical features.
3. **Cross-Validation Comparison (5-Fold CV on Train Set):**
   - *Logistic Regression (Baseline):* ROC-AUC: 0.9254 | PR-AUC: 0.7485 | F1: 0.6434 | Recall: 0.8472
   - *HistGradientBoosting:* ROC-AUC: 0.9937 | PR-AUC: 0.9709 | F1: 0.9147 | Recall: 0.9255
   - *Random Forest (Selected Production Model):* ROC-AUC: 0.9877 | PR-AUC: 0.9418 | F1: 0.8727 | Recall: 0.8864
4. **Final Model:** Tuned `RandomForestClassifier` (`n_estimators=150`, `max_depth=14`, `criterion='entropy'`, `class_weight='balanced'`) providing optimal trade-off between predictive power, inference speed (<15ms), and exact tree-based SHAP explainability.

### Test Set Performance (2,026 Held-Out Customers):
- **Accuracy:** `95.31%`
- **Precision (Churn):** `84.43%`
- **Recall (Churn):** `86.77%` (Detects 282 out of 325 actual churners)
- **F1-Score (Churn):** `0.8558`
- **ROC-AUC:** `0.9859`
- **PR-AUC (Average Precision):** `0.9444`

#### Confusion Matrix:
| | Predicted Retained | Predicted Churn |
| :--- | :---: | :---: |
| **Actual Retained (1,701)** | 1,649 (TN) | 52 (FP) |
| **Actual Churn (325)** | 43 (FN) | 282 (TP) |

### Saved Artifacts:
- `models/churn_pipeline.joblib`: Serialized scikit-learn Pipeline containing preprocessor and trained classifier.
- `models/model_metadata.json`: Feature definitions, hyperparameters, class mappings, threshold settings, and metrics.
- `models/evaluation_curves.png`: High-resolution Confusion Matrix and ROC / PR curve plots.

---

## 💻 Running the Streamlit Application

Launch the web application:
```bash
streamlit run app.py
```

### Application Features:
1. **Dashboard:**
   - Portfolio overview stat cards (Total Customers, High Risk, Medium Risk, Low Risk).
   - Risk distribution donut chart & churn probability histogram.
   - Segment-level average churn rate bar chart.
   - Portfolio-wide top churn risk factor importance chart.
2. **AI Explain:**
   - Customer-level drill-down with probability gauge and risk tier.
   - Local SHAP factor attribution detailing which features increase vs reduce churn risk.
   - Rule-based, transparent retention actions mapped to primary behavioral drivers.
3. **Risk Customer:**
   - Filterable, searchable portfolio table (High / Medium / Low risk bands).
   - Instant customer risk badges and action recommendations.
4. **History:**
   - Audit trail of previous analysis sessions, customer volumes, and high-risk flags.

---

## 🧪 Running Tests

A comprehensive unit and integration test suite verifies model loading, probability bounds, class selection, error handling, SHAP explanations, and loader compatibility:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## ⚠️ Limitations & Assumptions
- **Class Imbalance:** Bank customer churn is intrinsically imbalanced (~16% churn). Balanced class weighting was applied to prioritize recall (identifying actual churners) without excessive false positives.
- **Domain Focus:** Trained on consumer credit card relationship metrics (`Total_Trans_Ct`, `Total_Trans_Amt`, `Total_Revolving_Bal`, `Months_Inactive_12_mon`, `Contacts_Count_12_mon`). When ingesting retail deposit-only accounts, `COLUMN_ALIASES` maps comparable spend, activity, and contact metrics.
- **Explainability:** SHAP values provide local feature attribution for model transparency. Retention recommendations are rule-based advisory suggestions for banking personnel and do not imply causal guarantees.
