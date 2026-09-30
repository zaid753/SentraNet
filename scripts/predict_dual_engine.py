#!/usr/bin/env python3
"""
SENTRANET — Phase 4 Dual AI Engine CLI Tool
Runs both XGBoost (Supervised Classification) and Isolation Forest (Unsupervised Anomaly Detection)
on the same feature vector and constructs the unified Phase 4 DecisionObject.
"""

import os
import sys
import argparse
import json
import pandas as pd

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.models.xgboost_classifier import XGBoostClassifier
from ml.models.isolation_forest_detector import IsolationForestDetector

def main():
    parser = argparse.ArgumentParser(description="Run dual-engine inference for SENTRANET.")
    parser.add_argument("--xgb-model", type=str, default="models/xgboost/sentranet_xgboost.json", help="Path to XGBoost booster JSON")
    parser.add_argument("--if-model", type=str, default="models/isolation_forest/sentranet_isolation_forest.joblib", help="Path to Isolation Forest joblib")
    parser.add_argument("--if-reference", type=str, default="models/isolation_forest/anomaly_reference.json", help="Path to Isolation Forest reference JSON")
    parser.add_argument("--test-data", type=str, default="data/processed/sample/test.parquet", help="Path to test parquet file")
    parser.add_argument("--row-index", type=int, default=0, help="Row index from dataset to evaluate")

    args = parser.parse_args()

    if not os.path.exists(args.xgb_model):
        print(f"[ERROR] XGBoost model '{args.xgb_model}' missing. Train Phase 3 model first.")
        sys.exit(1)
    if not os.path.exists(args.if_model):
        print(f"[ERROR] Isolation Forest model '{args.if_model}' missing. Train Phase 4 model first.")
        sys.exit(1)
    if not os.path.exists(args.test_data):
        print(f"[ERROR] Dataset '{args.test_data}' missing.")
        sys.exit(1)

    xgb_classifier = XGBoostClassifier(model_path=args.xgb_model)
    if_detector = IsolationForestDetector(model_path=args.if_model, reference_path=args.if_reference)

    df = pd.read_parquet(args.test_data)
    if args.row_index >= len(df):
        print(f"[ERROR] Row index {args.row_index} out of bounds (dataset size: {len(df)})")
        sys.exit(1)

    sample_row = df.iloc[[args.row_index]]
    actual_label = sample_row["label"].values[0] if "label" in sample_row else "Unknown"
    window_time = str(sample_row["window_start"].values[0]) if "window_start" in sample_row else "2026-09-30T12:00:00.000000"

    # 1. XGBoost Supervised Classification
    xgb_decisions = xgb_classifier.predict_decision(sample_row, timestamp=window_time)
    xgb_decision = xgb_decisions[0]

    # 2. Isolation Forest Unsupervised Anomaly Detection
    ano_score = float(round(float(if_detector.anomaly_score(sample_row)[0]), 4))
    is_ano = bool(if_detector.is_anomalous(sample_row)[0])

    # 3. Fuse into Unified Phase 4 DecisionObject
    clean_probs = {k: float(round(float(v), 4)) for k, v in xgb_decision["class_probabilities"].items()}
    decision_object = {
        "timestamp": xgb_decision["timestamp"],
        "predicted_class": xgb_decision["predicted_class"],
        "class_probabilities": clean_probs,
        "classification_confidence": float(round(float(xgb_decision["classification_confidence"]), 4)),
        "anomaly_score": ano_score,
        "is_anomalous": is_ano,
        "risk_score": None,
        "time_to_impact_seconds": None,
        "forecast_available": False,
        "explanation": None,
    }

    print("\n" + "=" * 55)
    print("SENTRANET DUAL AI ENGINE (PHASE 4)")
    print("=" * 55)
    print(f"Sample Window Timestamp:    {decision_object['timestamp']}")
    print(f"Actual Ground Truth Label:  {actual_label} (post-hoc evaluation reference)")
    print("-" * 55)
    print("Classification (XGBoost Engine)")
    print("--------------------------------")
    print(f"Predicted Class:            {decision_object['predicted_class']}")
    print(f"Classification Confidence:  {decision_object['classification_confidence']:.4f}")
    print("\nClass Probabilities:")
    for cls_name, prob in decision_object["class_probabilities"].items():
        bar_len = int(prob * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        print(f"  {cls_name:<14} {prob:>6.4f}  [{bar}]")
    print("-" * 55)
    print("Anomaly Detection (Isolation Forest Engine)")
    print("--------------------------------------------")
    ano_bar_len = int(decision_object["anomaly_score"] * 25)
    ano_bar = "█" * ano_bar_len + "░" * (25 - ano_bar_len)
    print(f"Normalized Anomaly Score:   {decision_object['anomaly_score']:.4f}  [{ano_bar}]")
    print(f"Anomaly Threshold (P99):    {if_detector.threshold:.4f}")
    print(f"Anomalous Flag:             {str(decision_object['is_anomalous']).upper()}")
    print("-" * 55)
    print("Forecasting (Phase 5 Engine — Pending)")
    print("---------------------------------------")
    print("Risk Score:                 N/A (Phase 5)")
    print("Time to Impact:             N/A (Phase 5)")
    print(f"Forecast Available:         {str(decision_object['forecast_available']).upper()}")
    print("=" * 55)
    print("\nComplete DecisionObject JSON Payload:")
    print(json.dumps(decision_object, indent=2))
    print("=" * 55 + "\n")

if __name__ == "__main__":
    main()
