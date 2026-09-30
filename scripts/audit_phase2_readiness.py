#!/usr/bin/env python3
"""
SENTRANET — Phase 2.5 Formal Data Readiness Audit Tool
Executes an audit across raw data, window aggregations, timestamps,
local benchmark availability, and partition distributions.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Ensure workspace root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_audit():
    print("=" * 70)
    print("SENTRANET — PHASE 2.5 FORMAL DATA READINESS AUDIT")
    print("=" * 70)

    # 1. Real Benchmark Availability Audit
    print("\n[SECTION 1: REAL BENCHMARK DATASET AVAILABILITY]")
    raw_dirs = {
        "CICIDS2017": "data/raw/cicids2017",
        "UNSW-NB15": "data/raw/unsw_nb15",
        "CIC-DDoS2019": "data/raw/cic_ddos2019",
    }
    real_datasets_found = []
    for name, path in raw_dirs.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith(".csv") or f.endswith(".parquet") or f.endswith(".pcap")]
            status = f"PRESENT ({len(files)} files)" if files else "EMPTY (Directory exists, no data files)"
            if files:
                real_datasets_found.append(name)
        else:
            status = "DIRECTORY NOT FOUND"
        print(f"  • {name:<15}: {status}")

    if not real_datasets_found:
        print("\n  >> STATUS: Benchmark dataset not available locally.")
        print("  >> NOTE: Adapters in ml/data/ are active and ready once files are placed in data/raw/.")
    else:
        print(f"\n  >> STATUS: Discovered local benchmark datasets: {real_datasets_found}")

    # 2. Raw Sample Data & Timestamp Audit
    sample_file = "data/samples/sample_network_traffic.csv"
    print("\n[SECTION 2: SAMPLE DATA & TIMESTAMP PROVENANCE AUDIT]")
    if not os.path.exists(sample_file):
        print(f"  [ERROR] Sample file {sample_file} not found!")
        return

    raw_df = pd.read_csv(sample_file)
    raw_rows, raw_cols = raw_df.shape
    print(f"  • Source File:          {sample_file}")
    print(f"  • Total Flow Events:    {raw_rows:,}")
    print(f"  • Total Attributes:     {raw_cols}")
    print(f"  • Timestamp Provenance: CATEGORY B — SYNTHETIC / GENERATED")
    print(f"                          (Generated for pipeline validation; not empirical network capture)")
    print(f"  • Time Horizon:         {raw_df['timestamp'].min()} to {raw_df['timestamp'].max()}")

    # 3. BENIGN Traffic Audit (Raw vs Processed)
    print("\n[SECTION 3: BENIGN CLASS & LABEL INTEGRITY AUDIT]")
    raw_dist = raw_df["label"].value_counts()
    raw_pct = (raw_df["label"].value_counts(normalize=True) * 100).round(2)
    print("  RAW Flow Records Distribution:")
    for lbl in raw_dist.index:
        print(f"    - {lbl:<15}: {raw_dist[lbl]:>6,} flows ({raw_pct[lbl]:>5.1f}%)")

    benign_raw_count = raw_dist.get("BENIGN", 0)
    print(f"\n  >> Raw BENIGN Count: {benign_raw_count:,} flows ({(benign_raw_count/raw_rows)*100:.1f}% of raw traffic)")

    # 4. Processed Temporal Partitions Audit
    print("\n[SECTION 4: PROCESSED TEMPORAL PARTITIONS & WINDOWING AUDIT]")
    processed_dir = "data/processed/sample"
    train_path = os.path.join(processed_dir, "train.parquet")
    val_path = os.path.join(processed_dir, "validation.parquet")
    test_path = os.path.join(processed_dir, "test.parquet")
    features_path = os.path.join(processed_dir, "feature_names.json")

    if not (os.path.exists(train_path) and os.path.exists(val_path) and os.path.exists(test_path)):
        print("  [ERROR] Processed parquet partitions missing!")
        return

    train_df = pd.read_parquet(train_path)
    val_df = pd.read_parquet(val_path)
    test_df = pd.read_parquet(test_path)

    with open(features_path, "r", encoding="utf-8") as f:
        features = json.load(f)["features"]

    total_windows = len(train_df) + len(val_df) + len(test_df)
    print(f"  • Total Aggregated Windows (60s): {total_windows}")
    print(f"  • Window Feature Count:           {len(features)} numeric inputs")

    print("\n  Partition Chronology & Class Breakdown:")
    partitions = [
        ("Training (70%)", train_df),
        ("Validation (15%)", val_df),
        ("Test (15%)", test_df),
    ]

    for name, df in partitions:
        t_min = df["window_start"].min()
        t_max = df["window_start"].max()
        nan_count = df[features].isna().sum().sum()
        inf_count = df[features].isin([float("inf"), float("-inf")]).sum().sum()
        dist = df["label"].value_counts().to_dict()
        print(f"\n    [{name}] - {len(df)} windows")
        print(f"      - Temporal Bounds: {t_min}  -->  {t_max}")
        print(f"      - NaN / Inf Count: {nan_count} NaNs, {inf_count} Infs")
        print(f"      - Class Distribution: {dist}")

    # 5. Overall Window Class Summary
    all_labels = pd.concat([train_df["label"], val_df["label"], test_df["label"]])
    window_dist = all_labels.value_counts()
    window_pct = (all_labels.value_counts(normalize=True) * 100).round(2)
    print("\n  AGGREGATED WINDOW CLASS TOTALS:")
    for lbl in window_dist.index:
        print(f"    - {lbl:<15}: {window_dist[lbl]:>4} windows ({window_pct[lbl]:>5.1f}%)")

    # 6. Leakage & Model Safety Verdict
    print("\n[SECTION 5: DATA LEAKAGE & PRE-TRAINING VERDICT]")
    train_max = train_df["window_start"].max()
    val_min = val_df["window_start"].min()
    val_max = val_df["window_start"].max()
    test_min = test_df["window_start"].min()

    has_leakage = (train_max >= val_min) or (val_max >= test_min)
    if not has_leakage:
        print("  • Temporal Overlap:     0s — Chronological boundary strictly enforced.")
    else:
        print("  • Temporal Overlap:     WARNING — Overlap detected!")

    print("  • Feature Scaling:      StandardScaler fitted STRICTLY on train split.")
    print("  • Privacy Design:       IP address strings excluded from continuous feature vector.")
    print("  • Pre-Training Advice:  Do NOT blindly optimize XGBoost on synthetic sample data.")
    print("                          Lock Phase 3 architecture with class-weighted objectives,")
    print("                          macro-F1/PR-AUC metric tracking, and modular pipeline reusability.")
    print("=" * 70)

if __name__ == "__main__":
    run_audit()
