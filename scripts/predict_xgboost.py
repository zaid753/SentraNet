#!/usr/bin/env python3
"""
SENTRANET — Phase 3 XGBoost CLI Prediction Tool
Loads trained model and generates real class probabilities and standardized DecisionObject.
"""

import os
import sys
import argparse
import pandas as pd

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.models.xgboost_classifier import XGBoostClassifier

def main():
    parser = argparse.ArgumentParser(description="Run inference using trained SENTRANET XGBoost model.")
    parser.add_argument("--model", type=str, default="models/xgboost/sentranet_xgboost.json", help="Path to booster model JSON")
    parser.add_argument("--test-data", type=str, default="data/processed/sample/test.parquet", help="Path to test parquet file")
    parser.add_argument("--row-index", type=int, default=0, help="Row index from test data to evaluate")

    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"[ERROR] Trained model artifact '{args.model}' not found. Run 'python scripts/train_xgboost.py' first.")
        sys.exit(1)

    if not os.path.exists(args.test_data):
        print(f"[ERROR] Test data file '{args.test_data}' not found.")
        sys.exit(1)

    classifier = XGBoostClassifier(model_path=args.model)
    test_df = pd.read_parquet(args.test_data)

    if args.row_index >= len(test_df):
        print(f"[ERROR] row-index {args.row_index} out of bounds (max {len(test_df)-1})")
        sys.exit(1)

    sample_row = test_df.iloc[[args.row_index]]
    actual_label = sample_row["label"].values[0] if "label" in sample_row else "Unknown"
    window_time = str(sample_row["window_start"].values[0]) if "window_start" in sample_row else None

    # Predict decision object
    decisions = classifier.predict_decision(sample_row, timestamp=window_time)
    decision = decisions[0]

    print("\n" + "=" * 50)
    print("SENTRANET XGBoost Prediction")
    print("=" * 50)
    print(f"Sample Window Timestamp:    {decision['timestamp']}")
    print(f"Actual Ground Truth Label:  {actual_label}")
    print(f"Predicted Class:            {decision['predicted_class']}")
    print(f"Classification Confidence:  {decision['classification_confidence']:.4f}")
    print("-" * 50)
    print("Class Probabilities:")
    for cls_name, prob in decision["class_probabilities"].items():
        bar_len = int(prob * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"  {cls_name:<14} {prob:>6.4f}  [{bar}]")
    print("-" * 50)
    print("DecisionObject Future Context:")
    print("  Anomaly Score:   N/A (Phase 4)")
    print("  Risk Score:      N/A (Phase 4)")
    print("  Time to Impact:  N/A (Phase 5)")
    print(f"  Forecast Available: {str(decision['forecast_available']).upper()}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
