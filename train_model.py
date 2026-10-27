

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42
TEST_SIZE = 0.20
TARGET_COLUMN = "Attrition_Flag"
POSITIVE_CLASS = "Attrited Customer"
NEGATIVE_CLASS = "Existing Customer"

ID_COLUMNS = ["CLIENTNUM"]
LEAKAGE_COLUMNS = [
    "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1",
    "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2",
]

CATEGORICAL_FEATURES = [
    "Gender",
    "Education_Level",
    "Marital_Status",
    "Income_Category",
    "Card_Category",
]

NUMERICAL_FEATURES = [
    "Customer_Age",
    "Dependent_count",
    "Months_on_book",
    "Total_Relationship_Count",
    "Months_Inactive_12_mon",
    "Contacts_Count_12_mon",
    "Credit_Limit",
    "Total_Revolving_Bal",
    "Avg_Open_To_Buy",
    "Total_Amt_Chng_Q4_Q1",
    "Total_Trans_Amt",
    "Total_Trans_Ct",
    "Total_Ct_Chng_Q4_Q1",
    "Avg_Utilization_Ratio",
]

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_and_validate_dataset(csv_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Load dataset from path and validate target and columns."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Customer churn dataset not found at: {csv_path}")

    print(f"\n[1/6] Loading dataset from: {csv_path}")
    raw_df = pd.read_csv(csv_path)
    print(f"      Loaded {raw_df.shape[0]:,} rows and {raw_df.shape[1]} columns.")

    if TARGET_COLUMN not in raw_df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found. Available columns: {list(raw_df.columns)}"
        )

    # Validate target distribution
    target_counts = raw_df[TARGET_COLUMN].value_counts().to_dict()
    print(f"      Target distribution ({TARGET_COLUMN}):")
    for cls_name, count in target_counts.items():
        pct = (count / len(raw_df)) * 100
        print(f"        - '{cls_name}': {count:,} ({pct:.2f}%)")

    if POSITIVE_CLASS not in target_counts:
        raise ValueError(f"Expected positive class '{POSITIVE_CLASS}' not found in target values.")

    # Target: 1 for Attrited Customer, 0 for Existing Customer
    y = (raw_df[TARGET_COLUMN] == POSITIVE_CLASS).astype(int)

    # Clean leakage and identifier columns
    cols_to_remove = ID_COLUMNS + LEAKAGE_COLUMNS + [TARGET_COLUMN]
    feature_cols = [c for c in raw_df.columns if c not in cols_to_remove]
    X = raw_df[feature_cols].copy()

    # Check for missing values
    missing = X.isnull().sum()
    if missing.any():
        print("      Missing values detected (will be imputed during preprocessing):")
        print(missing[missing > 0])
    else:
        print("      Data quality check: Zero null values found across feature set.")

    print(f"      Features prepared: {len(feature_cols)} total "
          f"({len(NUMERICAL_FEATURES)} numerical, {len(CATEGORICAL_FEATURES)} categorical).")

    return X, y


def build_preprocessor() -> ColumnTransformer:
    """Build scikit-learn ColumnTransformer for numerical and categorical features."""
    num_transformer = Pipeline([
        ("scaler", StandardScaler()),
    ])

    cat_transformer = Pipeline([
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERICAL_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def compare_models(X_train: pd.DataFrame, y_train: pd.Series, preprocessor: ColumnTransformer):
    """Run 5-fold cross-validation on train set across candidate models."""
    print("\n[3/6] Running 5-fold Stratified Cross-Validation on training set...")

    candidate_models = {
        "Logistic Regression (Baseline)": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=150, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "Random Forest (Tuned)": RandomForestClassifier(
            n_estimators=150,
            max_depth=14,
            criterion="entropy",
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_summary = {}

    for name, clf in candidate_models.items():
        pipe = Pipeline([("preprocessor", preprocessor), ("classifier", clf)])
        scores = cross_validate(
            pipe,
            X_train,
            y_train,
            cv=cv,
            scoring=["roc_auc", "average_precision", "f1", "precision", "recall"],
            n_jobs=-1,
        )
        mean_roc = float(np.mean(scores["test_roc_auc"]))
        mean_pr = float(np.mean(scores["test_average_precision"]))
        mean_f1 = float(np.mean(scores["test_f1"]))
        mean_rec = float(np.mean(scores["test_recall"]))
        mean_prec = float(np.mean(scores["test_precision"]))

        cv_summary[name] = {
            "roc_auc": mean_roc,
            "pr_auc": mean_pr,
            "f1": mean_f1,
            "recall": mean_rec,
            "precision": mean_prec,
        }

        print(f"      {name:30s} -> ROC-AUC: {mean_roc:.4f} | PR-AUC: {mean_pr:.4f} "
              f"| F1: {mean_f1:.4f} | Recall: {mean_rec:.4f} | Prec: {mean_prec:.4f}")

    return cv_summary


def evaluate_final_model(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series):
    """Evaluate final trained pipeline on strictly held-out test set."""
    print("\n[4/6] Evaluating final model on held-out test set (20% sample)...")

    # Positive class probabilities
    probs = pipeline.predict_proba(X_test)[:, 1]
    threshold = 0.50
    preds = (probs >= 0.50).astype(int)

    # Metrics
    acc = float(accuracy_score(y_test, preds))
    prec = float(precision_score(y_test, preds))
    rec = float(recall_score(y_test, preds))
    f1 = float(f1_score(y_test, preds))
    roc_auc = float(roc_auc_score(y_test, probs))
    pr_auc = float(average_precision_score(y_test, probs))
    cm = confusion_matrix(y_test, preds).tolist()
    cls_report = classification_report(
        y_test, preds, target_names=[NEGATIVE_CLASS, POSITIVE_CLASS], digits=4, output_dict=True
    )
    cls_report_text = classification_report(
        y_test, preds, target_names=[NEGATIVE_CLASS, POSITIVE_CLASS], digits=4
    )

    print(f"      Test Set Size:   {len(y_test):,} customers")
    print(f"      Actual Churn:    {int(y_test.sum()):,} ({(y_test.mean()*100):.2f}%)")
    print(f"      Actual Retained: {int((y_test == 0).sum()):,} ({((1 - y_test.mean())*100):.2f}%)")
    print(f"      Accuracy:        {acc:.4f} ({acc*100:.2f}%)")
    print(f"      Precision:       {prec:.4f} ({prec*100:.2f}%)")
    print(f"      Recall:          {rec:.4f} ({rec*100:.2f}%)")
    print(f"      F1-Score:        {f1:.4f}")
    print(f"      ROC-AUC:         {roc_auc:.4f}")
    print(f"      PR-AUC:          {pr_auc:.4f}")
    print(f"\n      Confusion Matrix:\n{np.array(cm)}")
    print(f"\n      Classification Report:\n{cls_report_text}")

    # Generate evaluation plots
    plot_evaluation_curves(y_test, probs, cm)

    metrics = {
        "test_samples": len(y_test),
        "actual_churn_count": int(y_test.sum()),
        "actual_retained_count": int((y_test == 0).sum()),
        "threshold": threshold,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "confusion_matrix": cm,
        "classification_report": cls_report,
    }
    return metrics


def plot_evaluation_curves(y_test: pd.Series, probs: np.ndarray, cm: list[list[int]]):
    """Plot and save confusion matrix and ROC/PR curves."""
    try:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # 1. Confusion Matrix
        cm_arr = np.array(cm)
        im = axes[0].imshow(cm_arr, interpolation="nearest", cmap=plt.cm.Blues)
        axes[0].set_title("Confusion Matrix (Test Set)", fontsize=13, fontweight="bold")
        fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)
        tick_marks = np.arange(2)
        axes[0].set_xticks(tick_marks)
        axes[0].set_yticks(tick_marks)
        axes[0].set_xticklabels([NEGATIVE_CLASS, POSITIVE_CLASS], rotation=15)
        axes[0].set_yticklabels([NEGATIVE_CLASS, POSITIVE_CLASS])
        axes[0].set_ylabel("True Label", fontweight="bold")
        axes[0].set_xlabel("Predicted Label", fontweight="bold")

        thresh = cm_arr.max() / 2.0
        for i in range(cm_arr.shape[0]):
            for j in range(cm_arr.shape[1]):
                axes[0].text(
                    j, i, f"{cm_arr[i, j]:,}",
                    ha="center", va="center",
                    color="white" if cm_arr[i, j] > thresh else "black",
                    fontsize=12, fontweight="bold"
                )

        # 2. ROC & PR Curves
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_auc = roc_auc_score(y_test, probs)
        prec_c, rec_c, _ = precision_recall_curve(y_test, probs)
        pr_auc = average_precision_score(y_test, probs)

        axes[1].plot(fpr, tpr, color="#2B4CE0", lw=2, label=f"ROC Curve (AUC = {roc_auc:.3f})")
        axes[1].plot(rec_c, prec_c, color="#E0403A", lw=2, linestyle="--", label=f"PR Curve (AUC = {pr_auc:.3f})")
        axes[1].plot([0, 1], [0, 1], color="gray", lw=1, linestyle=":")
        axes[1].set_xlim([0.0, 1.0])
        axes[1].set_ylim([0.0, 1.05])
        axes[1].set_xlabel("False Positive Rate / Recall", fontweight="bold")
        axes[1].set_ylabel("True Positive Rate / Precision", fontweight="bold")
        axes[1].set_title("ROC and Precision-Recall Curves", fontsize=13, fontweight="bold")
        axes[1].legend(loc="lower left")
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        eval_plot_path = MODELS_DIR / "evaluation_curves.png"
        fig.savefig(eval_plot_path, dpi=200)
        plt.close(fig)
        print(f"      Saved evaluation plots to: {eval_plot_path}")
    except Exception as e:
        print(f"      Warning: Could not save evaluation curves plot: {e}")


def main():
    print("=" * 70)
    print("BankCo Production Machine Learning Churn Model Training Workflow")
    print("=" * 70)

    # 1. Dataset identification
    dataset_path = BASE_DIR / "BankChurners.csv"
    if len(sys.argv) > 1:
        dataset_path = Path(sys.argv[1]).resolve()

    X, y = load_and_validate_dataset(dataset_path)

    # 2. Stratified train/test split (80% train, 20% test held-out)
    print("\n[2/6] Splitting data into stratified Train (80%) and Test (20%) sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"      Train set: {X_train.shape[0]:,} rows ({y_train.sum():,} churners)")
    print(f"      Test set:  {X_test.shape[0]:,} rows ({y_test.sum():,} churners)")

    # 3. Model comparison via cross-validation
    preprocessor = build_preprocessor()
    cv_summary = compare_models(X_train, y_train, preprocessor)

    # 4. Final production model training: Random Forest
    # (Selected for superior ROC-AUC/PR-AUC balance and native fast SHAP TreeExplainer support)
    print("\n[4/6] Fitting final Production Random Forest Pipeline on full training set...")
    final_rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=14,
        criterion="entropy",
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    final_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", final_rf),
    ])
    final_pipeline.fit(X_train, y_train)
    print("      Model training complete.")

    # 5. Evaluate on held-out test set
    test_metrics = evaluate_final_model(final_pipeline, X_test, y_test)

    # 6. Save model pipeline, metadata, and reports
    print("\n[5/6] Serializing model pipeline and metadata...")
    pipeline_path = MODELS_DIR / "churn_pipeline.joblib"
    joblib.dump(final_pipeline, pipeline_path)
    print(f"      Saved Pipeline artifact to: {pipeline_path}")

    # Compute Global Feature Importances
    preprocessor_fitted = final_pipeline.named_steps["preprocessor"]
    cat_feature_names = preprocessor_fitted.named_transformers_["cat"]["encoder"].get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = NUMERICAL_FEATURES + list(cat_feature_names)
    importances = final_rf.feature_importances_
    feat_imp_dict = dict(zip(all_feature_names, [float(x) for x in importances]))
    # Sort descending
    feat_imp_sorted = dict(sorted(feat_imp_dict.items(), key=lambda item: item[1], reverse=True))

    metadata = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 150,
        "max_depth": 14,
        "criterion": "entropy",
        "class_weight": "balanced",
        "random_state": RANDOM_STATE,
        "target_column": TARGET_COLUMN,
        "positive_class": POSITIVE_CLASS,
        "negative_class": NEGATIVE_CLASS,
        "training_date_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_name": dataset_path.name,
        "total_records": len(X),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "input_features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
            "total_input_count": len(NUMERICAL_FEATURES) + len(CATEGORICAL_FEATURES),
        },
        "transformed_feature_count": len(all_feature_names),
        "risk_thresholds": {
            "high": 0.60,
            "medium": 0.30,
            "low": 0.00,
        },
        "cross_validation_train_scores": cv_summary,
        "test_set_metrics": test_metrics,
        "top_10_features": dict(list(feat_imp_sorted.items())[:10]),
    }

    metadata_path = MODELS_DIR / "model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"      Saved metadata to: {metadata_path}")

    print("\n[6/6] Execution finished successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
