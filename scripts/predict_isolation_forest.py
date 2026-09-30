#!/usr/bin/env python3
"""
SENTRANET — Phase 4 Isolation Forest CLI Prediction Tool
Runs standalone unsupervised anomaly scoring on a specified test/evaluation sample.
"""

import os
import sys
import argparse
import pandas as pd

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.models.isolation_forest_detector import IsolationForestDetector

def main():
    parser = argparse.ArgumentParser(description="Run inference using trained SENTRANET Isolation Forest detector.")
    parser.add_argument("--model", type=str, default="models/isolation_forest/sentranet_isolation_forest.joblib", help="Path to model joblib")
    parser.add_argument("--reference", type=str, default="models/isolation_forest/anomaly_reference.json", help="Path to reference JSON")
    parser.add_argument("--test-data", type=str, default="data/processed/sample/test.parquet", help="Path to test parquet file")
    parser.add_argument("--row-index", type=int, default=0, help="Row index from test data to evaluate")

    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"[ERROR] Trained model artifact '{args.model}' not found. Run 'python scripts/train_isolation_forest.py' first.")
        sys.exit(1)

    if not os.path.exists(args.test_data):
        print(f"[ERROR] Test data file '{args.test_data}' not found.")
        sys.exit(1)

    detector = IsolationForestDetector(model_path=args.model, reference_path=args.reference)
    test_df = pd.read_parquet(args.test_data)

    if args.row_index >= len(test_df):
        print(f"[ERROR] row-index {args.row_index} out of bounds (max {len(test_df)-1})")
        sys.exit(1)

    sample_row = test_df.iloc[[args.row_index]]
    actual_label = sample_row["label"].values[0] if "label" in sample_row else "Unknown"
    window_time = str(sample_row["window_start"].values[0]) if "window_start" in sample_row else None

    # Inference
    raw_dec = detector.raw_decision_function(sample_row)[0]
    norm_score = detector.anomaly_score(sample_row)[0]
    is_ano = detector.is_anomalous(sample_row)[0]
    decisions = detector.predict_decision(sample_row, timestamp=window_time)
    decision = decisions[0]

    bar_len = int(norm_score * 30)
    bar = "█" * bar_len + "░" * (30 - bar_len)

    print("\n" + "=" * 55)
    print("SENTRANET Isolation Forest Prediction")
    print("=" * 55)
    print(f"Sample Window Timestamp:      {decision['timestamp']}")
    print(f"Actual Ground Truth Label:    {actual_label} (post-hoc reference only)")
    print(f"Raw Model Decision Value (s): {raw_dec:>+.4f}")
    print(f"Normalized Anomaly Score:     {norm_score:.4f}  [{bar}]")
    print(f"Anomaly Threshold:            {detector.threshold:.4f} (Benign P99)")
    print(f"Anomalous:                    {str(is_ano).upper()}")
    print("-" * 55)
    print("Behavioral Status:")
    if is_ano:
        print("  >> ABNORMAL: Traffic pattern deviates significantly from benign baseline.")
    else:
        print("  >> NORMAL: Traffic conforms to learned benign baseline envelope.")
    print("-" * 55)
    print("DecisionObject Future Context:")
    print("  Risk Score:      N/A (Phase 5)")
    print("  Time to Impact:  N/A (Phase 5)")
    print(f"  Forecast Available: {str(decision['forecast_available']).upper()}")
    print("=" * 55 + "\n")

if __name__ == "__main__":
    main()
