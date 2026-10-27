"""tests/test_model.py — Unit and Integration Tests for BankCo Customer Churn Model."""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from utils.data import generate_synthetic_customers, load_customers
from utils.model import (
    MODEL_PATH,
    METADATA_PATH,
    explain_customer,
    load_model,
    predict_churn,
    recommend_action,
    risk_level,
)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "BankChurners.csv"


class TestBankCoChurnModel(unittest.TestCase):
    """Test suite validating production ML model pipeline and interfaces."""

    @classmethod
    def setUpClass(cls):
        """Ensure model artifact is loaded and sample data is available."""
        cls.pipeline, cls.explainer, cls.metadata = load_model()
        if CSV_PATH.exists():
            cls.raw_df = pd.read_csv(CSV_PATH)
        else:
            cls.raw_df = generate_synthetic_customers(100)

    def test_01_model_artifacts_exist(self):
        """Verify serialized model pipeline and metadata files exist on disk."""
        self.assertTrue(MODEL_PATH.exists(), f"Model file missing at {MODEL_PATH}")
        self.assertTrue(METADATA_PATH.exists(), f"Metadata file missing at {METADATA_PATH}")
        self.assertIsNotNone(self.pipeline)
        self.assertIn("classifier", self.pipeline.named_steps)
        self.assertIn("preprocessor", self.pipeline.named_steps)

    def test_02_empty_dataframe_handling(self):
        """Empty input DataFrame should safely return an empty NumPy array."""
        empty_df = pd.DataFrame()
        preds = predict_churn(empty_df)
        self.assertIsInstance(preds, np.ndarray)
        self.assertEqual(len(preds), 0)

        none_preds = predict_churn(None)
        self.assertIsInstance(none_preds, np.ndarray)
        self.assertEqual(len(none_preds), 0)

    def test_03_prediction_length_and_probability_bounds(self):
        """Predictions must equal input row count with values strictly in [0.0, 1.0]."""
        sample = self.raw_df.head(25)
        preds = predict_churn(sample)

        self.assertEqual(len(preds), len(sample))
        self.assertTrue(np.all(preds >= 0.0))
        self.assertTrue(np.all(preds <= 1.0))

    def test_04_positive_class_probability_alignment(self):
        """Verify model outputs high churn probabilities for known attrited customers."""
        if "Attrition_Flag" in self.raw_df.columns:
            attrited_sample = self.raw_df[self.raw_df["Attrition_Flag"] == "Attrited Customer"].head(20)
            existing_sample = self.raw_df[self.raw_df["Attrition_Flag"] == "Existing Customer"].head(20)

            attrited_probs = predict_churn(attrited_sample)
            existing_probs = predict_churn(existing_sample)

            # Average probability for attrited customers should be substantially higher than existing
            self.assertGreater(
                attrited_probs.mean(),
                existing_probs.mean(),
                f"Attrited mean ({attrited_probs.mean():.3f}) should exceed existing mean ({existing_probs.mean():.3f})"
            )

    def test_05_missing_columns_validation(self):
        """Invalid inputs lacking required features should raise a clear ValueError."""
        invalid_df = pd.DataFrame({
            "completely_irrelevant_col_1": [1, 2, 3],
            "completely_irrelevant_col_2": ["a", "b", "c"],
        })
        with self.assertRaises(ValueError) as ctx:
            predict_churn(invalid_df)
        self.assertIn("missing required features", str(ctx.exception).lower())

    def test_06_risk_level_thresholds(self):
        """Verify probability mapping to High, Medium, and Low risk bands."""
        self.assertEqual(risk_level(0.95), "High")
        self.assertEqual(risk_level(0.60), "High")
        self.assertEqual(risk_level(0.59), "Medium")
        self.assertEqual(risk_level(0.30), "Medium")
        self.assertEqual(risk_level(0.29), "Low")
        self.assertEqual(risk_level(0.01), "Low")

    def test_07_customer_explanation_format(self):
        """Local explanation should return structured factor contributions sorted by impact."""
        row = self.raw_df.iloc[0]
        factors = explain_customer(row)

        self.assertIsInstance(factors, list)
        self.assertGreater(len(factors), 0)

        # Check required keys and value constraints
        for factor in factors:
            self.assertIn("feature", factor)
            self.assertIn("label", factor)
            self.assertIn("impact", factor)
            self.assertIn("direction", factor)
            self.assertIsInstance(factor["impact"], (float, int))
            self.assertTrue(0.0 <= factor["impact"] <= 1.0)
            self.assertIn(factor["direction"], ["increases", "decreases"])

        # Verify sorted descending by impact
        impacts = [f["impact"] for f in factors]
        self.assertEqual(impacts, sorted(impacts, reverse=True))

    def test_08_retention_recommendation_format(self):
        """Recommendation engine should return transparent action and rationale."""
        row = self.raw_df.iloc[0]
        factors = explain_customer(row)
        rec = recommend_action(row, factors)

        self.assertIsInstance(rec, dict)
        self.assertIn("action", rec)
        self.assertIn("reason", rec)
        self.assertTrue(len(rec["action"]) > 5)
        self.assertTrue(len(rec["reason"]) > 5)

    def test_09_synthetic_customers_pipeline_compatibility(self):
        """Synthetic demo generator output must be 100% compatible with ML pipeline."""
        demo_df = generate_synthetic_customers(50, seed=123)
        self.assertEqual(len(demo_df), 50)

        probs = predict_churn(demo_df)
        self.assertEqual(len(probs), 50)

        risk_levels = [risk_level(p) for p in probs]
        self.assertEqual(len(risk_levels), 50)
        self.assertTrue(all(r in ["High", "Medium", "Low"] for r in risk_levels))

    def test_10_file_loader_compatibility(self):
        """load_customers should preserve rows and populate UI columns."""
        if CSV_PATH.exists():
            with open(CSV_PATH, "rb") as f:
                loaded = load_customers(f)
                self.assertGreater(len(loaded), 1000)
                # Verify standard UI columns exist
                for col in ["CustomerID", "CustomerType", "Tenure", "TotalSpend", "MonthlyCharges"]:
                    self.assertIn(col, loaded.columns)
                probs = predict_churn(loaded.head(10))
                self.assertEqual(len(probs), 10)


if __name__ == "__main__":
    unittest.main()
