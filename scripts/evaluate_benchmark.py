#!/usr/bin/env python3
"""
SENTRANET — Benchmark Evaluation CLI Tool (Phase 10)
Runs empirical evaluation of the frozen SENTRANET AI Core across network security benchmarks:
- Category A: CICIDS2017, UNSW-NB15, CIC-DDoS2019
- Category B: Synthetic Development Fixture (sample)

Usage:
    python -m scripts.evaluate_benchmark --dataset cicids2017
    python -m scripts.evaluate_benchmark --dataset sample
    python -m scripts.evaluate_benchmark --all
    python -m scripts.evaluate_benchmark --dataset sample --max-windows 50
"""

import os
import sys
import argparse

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.evaluation.evaluator import BenchmarkEvaluator
from ml.evaluation.manifest import generate_manifest, DATASET_SPECS
from ml.evaluation.summary import generate_cross_dataset_summary


def print_banner():
    print("=" * 70)
    print(" SENTRANET — Benchmark Evaluation & Empirical Validation (Phase 10)")
    print(" Tagline: 'From detecting attacks to forecasting them.'")
    print(" Model Strategy: FROZEN OPERATIONAL MODELS (No test fitting)")
    print("=" * 70)


def format_val(val, fmt="{:.4f}", default="N/A"):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return fmt.format(val)
    return str(val)


def display_results(result: dict):
    d_id = result.get("dataset_id", "unknown").upper()
    status = result.get("status")

    print("\n" + "-" * 70)
    print(f" DATASET: {d_id} ({result.get('category', 'Benchmark')})")
    print("-" * 70)

    if status == "NOT_AVAILABLE":
        print(" [!] STATUS: NOT AVAILABLE")
        print(f" Message:              {result.get('message')}")
        print(f" Expected Path:        {result.get('expected_path')}")
        print(f" Missing Files:        {len(result.get('missing_files', []))} files required")
        print(f" Download Source:      {result.get('download_instructions')}")
        print("-" * 70)
        return

    print(f" Status:               COMPLETED ({result.get('evaluation_mode')})")
    print(f" Windows Evaluated:    {result.get('windows_evaluated', 0):,}")
    print()

    # Classification
    cls = result.get("classification", {})
    print(" [1] XGBOOST MULTI-CLASS CLASSIFIER (Frozen)")
    print(f"   • Accuracy:         {format_val(cls.get('accuracy'))}")
    print(f"   • Macro F1 Score:   {format_val(cls.get('macro_f1'))}")
    print(f"   • Weighted F1 Score:{format_val(cls.get('weighted_f1'))}")
    print(f"   • Macro PR-AUC:     {format_val(cls.get('macro_pr_auc'))}")
    print(f"   • Multi-class Loss: {format_val(cls.get('log_loss'))}")

    # False Positives
    fp = result.get("false_positives", {})
    print()
    print(" [2] BENIGN FALSE POSITIVE ANALYSIS")
    print(f"   • Actual Benign:    {fp.get('actual_benign_windows', 0):,}")
    print(f"   • False Positives:  {fp.get('false_positive_count', 0):,}")
    print(f"   • Benign FPR:       {format_val(fp.get('false_positive_rate'))}")
    print(f"   • False Alarms/hr:  {format_val(fp.get('false_alarms_per_hour'), '{:.2f}')} alarms/hr")

    # Anomaly Detection
    ano = result.get("anomaly_detection", {})
    print()
    print(" [3] ISOLATION FOREST ANOMALY DETECTOR (Frozen)")
    print(f"   • Detection Rate:   {format_val(ano.get('attack_detection_rate'))}")
    print(f"   • Benign FPR:       {format_val(ano.get('benign_anomaly_fpr'))}")
    print(f"   • Benign Score:     mean={format_val(ano.get('benign_score_distribution', {}).get('mean'))} | "
          f"P95={format_val(ano.get('benign_score_distribution', {}).get('p95'))}")
    print(f"   • Attack Score:     mean={format_val(ano.get('attack_score_distribution', {}).get('mean'))} | "
          f"P95={format_val(ano.get('attack_score_distribution', {}).get('p95'))}")

    # Risk Fusion
    rf = result.get("risk_fusion", {})
    print()
    print(" [4] DUAL-ENGINE RISK FUSION")
    print(f"   • State Breakdown:  {rf.get('risk_state_counts', {})}")
    print(f"   • Attack High Rate: {format_val(rf.get('attack_high_rate'))}")
    print(f"   • False High Count: {rf.get('false_high_count', 0)}")

    # Forecasting
    fc = result.get("forecasting", {})
    print()
    print(" [5] TEMPORAL ATTACK FORECASTING")
    print(f"   • Attack Onsets:    {fc.get('attack_onsets_count', 0)}")
    print(f"   • Forecasted:       {fc.get('forecasted_onsets_count', 0)}")
    print(f"   • Mean Lead Time:   {format_val(fc.get('mean_lead_time_seconds'), '{:.1f}')} seconds")
    print(f"   • Median Lead Time: {format_val(fc.get('median_lead_time_seconds'), '{:.1f}')} seconds")
    print(f"   • Horizon 1m F1:    {format_val(fc.get('horizon_1m_f1'))}")
    print(f"   • Horizon 5m F1:    {format_val(fc.get('horizon_5m_f1'))}")

    # Performance
    perf = result.get("performance", {})
    print()
    print(" [6] PERFORMANCE & LATENCY")
    print(f"   • Latency Mean:     {format_val(perf.get('latency_ms_mean'), '{:.2f}')} ms / window")
    print(f"   • Latency P95:      {format_val(perf.get('latency_ms_p95'), '{:.2f}')} ms / window")
    print(f"   • Throughput:       {format_val(perf.get('throughput_windows_per_second'), '{:.1f}')} windows/sec")
    print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="SENTRANET Empirical Benchmark Evaluation Suite (Phase 10)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        choices=["sample", "cicids2017", "unsw_nb15", "cic_ddos2019"],
        help="Target benchmark dataset identifier to evaluate",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Evaluate all registered benchmark datasets sequentially",
    )
    parser.add_argument(
        "--max-windows",
        type=int,
        default=None,
        help="Quick evaluation mode: limit total temporal windows evaluated",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="artifacts/evaluation",
        help="Directory to save evaluation reports and plots",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip generating confusion matrix and distribution PNG plots",
    )

    args = parser.parse_args()

    print_banner()

    # Step 1: Update Dataset Manifest
    print("\nAuditing dataset availability...")
    manifest = generate_manifest()
    print(f"Manifest updated: {len(manifest['datasets'])} datasets cataloged.")

    evaluator = BenchmarkEvaluator(output_base_dir=args.output_dir)

    targets = []
    if args.all:
        targets = list(DATASET_SPECS.keys())
    elif args.dataset:
        targets = [args.dataset]
    else:
        # Default to sample (Category B fixture) for baseline demonstration
        targets = ["sample"]

    results = {}
    for target in targets:
        print(f"\nEvaluating dataset: {target.upper()}...")
        res = evaluator.evaluate_dataset(
            dataset_id=target,
            max_windows=args.max_windows,
            generate_plots=not args.no_plots,
        )
        results[target] = res
        display_results(res)

    # Step 2: Update Cross-Dataset Summary
    summary = generate_cross_dataset_summary(eval_dir=args.output_dir)
    print("\n[SUCCESS] Cross-dataset evaluation summary written to:")
    print("  • artifacts/evaluation/cross_dataset_summary.json")
    print("  • data/dataset_manifest.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
