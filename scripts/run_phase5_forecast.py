#!/usr/bin/env python3
"""
SENTRANET — Phase 5 Temporal Forecasting CLI Demonstration & Evaluation Pipeline
Processes sequential temporal windows, executes Risk Fusion, tracks trajectory,
emits pre-attack forecasts with ETA, and performs offline evaluation across horizons.
"""

import os
import sys
import argparse
import json
import pandas as pd

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.forecast.forecast_engine import ForecastEngine
from ml.evaluation.forecast_metrics import ForecastEvaluator

def main():
    parser = argparse.ArgumentParser(description="Run SENTRANET Phase 5 Forecast Engine on temporal dataset.")
    parser.add_argument("--data-path", type=str, default="data/processed/sample/validation.parquet", help="Path to evaluation parquet file")
    parser.add_argument("--full-timeline", action="store_true", help="Evaluate across combined train+val+test timeline")
    parser.add_argument("--save-reports", action="store_true", default=True, help="Save evaluation metrics and timeline plots")

    args = parser.parse_args()

    print("=" * 70)
    print("SENTRANET — PHASE 5 TEMPORAL FORECAST ENGINE")
    print("=" * 70)

    engine = ForecastEngine()
    evaluator = ForecastEvaluator()

    if args.full_timeline:
        print("\nLoading full chronological timeline (train + val + test)...")
        train_df = pd.read_parquet("data/processed/sample/train.parquet")
        val_df = pd.read_parquet("data/processed/sample/validation.parquet")
        test_df = pd.read_parquet("data/processed/sample/test.parquet")
        df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    else:
        print(f"\nLoading partition: {args.data_path}")
        df = pd.read_parquet(args.data_path)

    df_sorted = df.sort_values("window_start").reset_index(drop=True)
    print(f"Total temporal windows: {len(df_sorted)} ({df_sorted['window_start'].min()} -> {df_sorted['window_start'].max()})\n")

    # Run evaluation
    results = evaluator.evaluate_sequence(df_sorted, forecast_engine=engine)

    # Print live sample stream across sequential windows
    print("-" * 70)
    print("CHRONOLOGICAL STREAM SAMPLES (Key Transition Points)")
    print("-" * 70)

    # Sample key transition windows to display
    display_indices = [0, 5, 10, 15, 20, 25, 30]
    display_indices = [idx for idx in display_indices if idx < len(df_sorted)]

    # Also include any window where forecast_available was True
    for idx, rec in enumerate(results["timeline_data"]):
        if rec["forecast_available"] and idx not in display_indices:
            display_indices.append(idx)
    display_indices = sorted(display_indices)[:12]

    for idx in display_indices:
        rec = results["timeline_data"][idx]
        ts_str = str(rec["timestamp"])[:19]
        print(f"\n[Time: {ts_str}] Actual Ground Truth: {rec['actual_label']}")
        print(f"  Classification:      {rec['predicted_class']}")
        print(f"  Fused Risk Score:    {rec['risk_score']:.4f}  [{rec['risk_state']}]")
        print(f"  Risk Velocity:       {rec['risk_velocity']:+.4f}/min")
        if rec["forecast_available"]:
            print(f"  >> FORECAST ACTIVE:  Emerging {rec['forecast_class']}")
            eta_str = f"~{rec['time_to_impact_seconds']}s" if rec['time_to_impact_seconds'] is not None else "N/A"
            print(f"     Estimated ETA:    {eta_str}")
            print(f"     Forecast Conf:    {rec['forecast_confidence']:.4f}")
        else:
            print("  >> FORECAST:         No Emerging Attack Signature (forecast_available=FALSE)")

    print("\n" + "=" * 70)
    print("OFFLINE FORECAST EVALUATION METRICS ACROSS HORIZONS")
    print("=" * 70)

    print(f"\nAttack Onsets Detected: {len(results['attack_onsets_identified'])}")
    for onset in results["attack_onsets_identified"]:
        print(f"  • {onset['timestamp'][:19]} -> {onset['attack_class']} ({onset['transition']})")

    print("\nHorizon-Specific Forecasting Metrics:")
    print(f"{'Horizon':<10} {'Status':<18} {'Onsets':<8} {'Precision':<11} {'Recall':<9} {'F1':<8} {'Lead Time':<12} {'ETA Err':<10}")
    print("-" * 86)

    for h_name, h_metrics in results["horizon_metrics"].items():
        status = h_metrics["status"]
        if status == "INSUFFICIENT DATA":
            print(f"{h_name:<10} {'INSUFFICIENT DATA':<18} {'0':<8} {'N/A':<11} {'N/A':<9} {'N/A':<8} {'N/A':<12} {'N/A':<10}")
        else:
            p_str = f"{h_metrics['precision']:.4f}" if h_metrics['precision'] is not None else "N/A"
            r_str = f"{h_metrics['recall']:.4f}" if h_metrics['recall'] is not None else "N/A"
            f_str = f"{h_metrics['f1']:.4f}" if h_metrics['f1'] is not None else "N/A"
            lead_str = f"{h_metrics['mean_lead_time_seconds']}s" if h_metrics['mean_lead_time_seconds'] is not None else "N/A"
            eta_str = f"{h_metrics['median_eta_error_seconds']}s" if h_metrics['median_eta_error_seconds'] is not None else "N/A"
            print(f"{h_name:<10} {status:<18} {h_metrics['valid_onsets']:<8} {p_str:<11} {r_str:<9} {f_str:<8} {lead_str:<12} {eta_str:<10}")

    if args.save_reports:
        # Save json metrics
        metrics_file = "reports/phase5_forecast_metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            # Strip timestamp objects from json dump
            json_save = {
                "evaluation_timestamp": results["evaluation_timestamp"],
                "total_windows_evaluated": results["total_windows_evaluated"],
                "total_forecast_events_emitted": results["total_forecast_events_emitted"],
                "attack_onsets_identified": results["attack_onsets_identified"],
                "horizon_metrics": results["horizon_metrics"]
            }
            json.dump(json_save, f, indent=2)
        print(f"\nSaved metrics: {metrics_file}")

        # Save plot
        plot_file = "reports/phase5_risk_timeline.png"
        evaluator.plot_timeline(results["timeline_data"], output_png_path=plot_file)
        print(f"Saved timeline plot: {plot_file}")

        # Save Markdown report
        md_file = "docs/phase5_forecast_evaluation.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# SENTRANET — Phase 5 Attack Forecasting Evaluation Report\n\n")
            f.write("## 1. Experimental Overview\n\n")
            f.write("> [!IMPORTANT]\n")
            f.write("> **Scientific Honesty Statement:**  \n")
            f.write("> The Phase 5 forecasting engine is a **temporal risk-emergence baseline**. ")
            f.write("Forecast availability and lead-time performance depend on the presence of valid precursor-to-attack sequences in the evaluation dataset.  \n")
            f.write("> The current development fixture is **synthetic (Category B)** and is not evidence of real-world forecasting performance on CICIDS2017.\n\n")
            f.write(f"- **Evaluated Windows:** {results['total_windows_evaluated']}\n")
            f.write(f"- **Forecast Events Emitted:** {results['total_forecast_events_emitted']}\n")
            f.write(f"- **Identified Attack Onsets:** {len(results['attack_onsets_identified'])}\n\n")
            f.write("## 2. Multi-Horizon Forecasting Performance\n\n")
            f.write("| Horizon | Status | Valid Onsets | Precision | Recall | F1 Score | Mean Lead Time | Median ETA Error |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            for h_name, h_metrics in results["horizon_metrics"].items():
                if h_metrics["status"] == "INSUFFICIENT DATA":
                    f.write(f"| **{h_name}** | INSUFFICIENT DATA | 0 | N/A | N/A | N/A | N/A | N/A |\n")
                else:
                    p = f"{h_metrics['precision']:.4f}" if h_metrics['precision'] is not None else "N/A"
                    r = f"{h_metrics['recall']:.4f}" if h_metrics['recall'] is not None else "N/A"
                    f1 = f"{h_metrics['f1']:.4f}" if h_metrics['f1'] is not None else "N/A"
                    lt = f"{h_metrics['mean_lead_time_seconds']}s" if h_metrics['mean_lead_time_seconds'] is not None else "N/A"
                    ee = f"{h_metrics['median_eta_error_seconds']}s" if h_metrics['median_eta_error_seconds'] is not None else "N/A"
                    f.write(f"| **{h_name}** | {h_metrics['status']} | {h_metrics['valid_onsets']} | {p} | {r} | {f1} | {lt} | {ee} |\n")
            f.write("\n## 3. Timeline Visualization\n\n")
            f.write("The complete continuous risk curve and emitted forecast events are visualized in `reports/phase5_risk_timeline.png`.\n")
        print(f"Saved evaluation markdown: {md_file}")

    print("\n" + "=" * 70)
    print("PHASE 5 FORECAST DEMONSTRATION COMPLETE")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
