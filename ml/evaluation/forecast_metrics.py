"""
SENTRANET — Offline Forecast Evaluation Engine (Phase 5)
Evaluates forecast precision, recall, F1, lead time, and ETA error against known
ground-truth attack onsets across configurable forecast horizons (1, 2, 5, 10, 15 min).
Generates reports/phase5_forecast_metrics.json and reports/phase5_risk_timeline.png.
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import json
import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ml.forecast.forecast_engine import ForecastEngine

DEFAULT_CONFIG_PATH = "config/risk.yaml"

class ForecastEvaluator:
    """
    Offline evaluation framework for attack forecasting.
    Compares causal forecast events emitted at time T against ground-truth attack onsets at T + H.
    Strictly prohibits lookahead leakage at runtime.
    """

    def __init__(
        self,
        config_path: str = DEFAULT_CONFIG_PATH,
        horizons_minutes: Optional[List[int]] = None,
    ):
        self.config_path = config_path
        self.horizons = horizons_minutes or [1, 2, 5, 10, 15]

    def find_ground_truth_onsets(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifies all true attack onset boundaries (where label transitions from BENIGN or lower attack to new attack).
        """
        onsets = []
        df_sorted = df.sort_values("window_start").reset_index(drop=True)
        prev_label = None

        for idx, row in df_sorted.iterrows():
            curr_label = row["label"]
            curr_ts = pd.to_datetime(row["window_start"])

            # Onset occurs when non-benign begins after benign, or a major escalation happens
            if curr_label != "BENIGN":
                if prev_label == "BENIGN":
                    onsets.append({
                        "onset_index": idx,
                        "timestamp": curr_ts,
                        "attack_class": curr_label,
                        "type": f"{prev_label}_TO_{curr_label}"
                    })
                elif prev_label is not None and prev_label != curr_label and curr_label == "DDOS":
                    onsets.append({
                        "onset_index": idx,
                        "timestamp": curr_ts,
                        "attack_class": curr_label,
                        "type": f"{prev_label}_TO_{curr_label}"
                    })
            prev_label = curr_label

        return onsets

    def evaluate_sequence(
        self,
        df: pd.DataFrame,
        forecast_engine: Optional[ForecastEngine] = None,
    ) -> Dict[str, Any]:
        """
        Runs the forecast engine across the chronological sequence and evaluates
        forecasting accuracy, lead times, and ETA errors.
        """
        engine = forecast_engine or ForecastEngine(config_path=self.config_path)
        engine.reset()

        df_sorted = df.sort_values("window_start").reset_index(drop=True)
        onsets = self.find_ground_truth_onsets(df_sorted)

        timeline_records = []
        forecast_events = []

        # Step 1: Run causal sequential inference
        for idx, row in df_sorted.iterrows():
            curr_ts = pd.to_datetime(row["window_start"])
            actual_label = row["label"]

            decision = engine.update(df_sorted.iloc[[idx]], timestamp=curr_ts.isoformat())

            rec = {
                "window_index": idx,
                "timestamp": curr_ts,
                "actual_label": actual_label,
                "predicted_class": decision["predicted_class"],
                "risk_score": decision["risk_score"],
                "risk_state": decision["risk_state"],
                "risk_velocity": decision["risk_velocity"],
                "forecast_available": decision["forecast_available"],
                "forecast_class": decision["forecast_class"],
                "time_to_impact_seconds": decision["time_to_impact_seconds"],
                "forecast_confidence": decision["forecast_confidence"]
            }
            timeline_records.append(rec)

            if decision["forecast_available"]:
                forecast_events.append(rec)

        # Step 2: Evaluate per-horizon forecasting performance
        horizon_results = {}

        for h in self.horizons:
            h_seconds = h * 60

            # Count True Positives, False Positives, False Negatives
            # An attack onset at T_onset is considered successfully forecasted (TP) if
            # at least one forecast occurred in [T_onset - h, T_onset) with matching class.
            tp_onsets = 0
            fn_onsets = 0
            lead_times = []
            eta_errors = []

            for onset in onsets:
                t_onset = onset["timestamp"]
                expected_class = onset["attack_class"]

                # Find valid pre-onset forecast events in the horizon window [t_onset - h, t_onset]
                pre_forecasts = [
                    f for f in forecast_events
                    if 0 <= (t_onset - f["timestamp"]).total_seconds() <= h_seconds
                    and f["forecast_class"] == expected_class
                ]

                if pre_forecasts:
                    tp_onsets += 1
                    # Record lead time of earliest forecast
                    first_f = pre_forecasts[0]
                    lead_time_sec = (t_onset - first_f["timestamp"]).total_seconds()
                    lead_times.append(lead_time_sec)

                    # Compute ETA error
                    if first_f["time_to_impact_seconds"] is not None:
                        predicted_eta = first_f["time_to_impact_seconds"]
                        eta_err = abs(predicted_eta - lead_time_sec)
                        eta_errors.append(eta_err)
                else:
                    fn_onsets += 1

            # False Positives: Forecasts that occurred when NO attack onset followed within H minutes
            fp_forecasts = 0
            for f in forecast_events:
                f_ts = f["timestamp"]
                has_matching_onset = any(
                    0 <= (o["timestamp"] - f_ts).total_seconds() <= h_seconds
                    and o["attack_class"] == f["forecast_class"]
                    for o in onsets
                )
                # If traffic is already in ongoing attack, it is not a false alarm
                is_currently_attack = (f["actual_label"] == f["forecast_class"])
                if not has_matching_onset and not is_currently_attack:
                    fp_forecasts += 1

            total_valid_onsets = len(onsets)

            # Safeguard: if total onsets is too small (< 2), flag as insufficient data
            if total_valid_onsets == 0:
                horizon_results[f"{h}m"] = {
                    "horizon_minutes": h,
                    "status": "INSUFFICIENT DATA",
                    "valid_onsets": 0,
                    "precision": None,
                    "recall": None,
                    "f1": None,
                    "mean_lead_time_seconds": None,
                    "median_eta_error_seconds": None
                }
            else:
                prec = tp_onsets / (tp_onsets + fp_forecasts) if (tp_onsets + fp_forecasts) > 0 else 0.0
                rec = tp_onsets / (tp_onsets + fn_onsets) if (tp_onsets + fn_onsets) > 0 else 0.0
                f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

                horizon_results[f"{h}m"] = {
                    "horizon_minutes": h,
                    "status": "EVALUATED" if total_valid_onsets >= 2 else "LOW_SAMPLE_WARNING",
                    "valid_onsets": total_valid_onsets,
                    "tp_onsets": tp_onsets,
                    "fp_forecasts": fp_forecasts,
                    "fn_onsets": fn_onsets,
                    "precision": round(prec, 4),
                    "recall": round(rec, 4),
                    "f1": round(f1, 4),
                    "mean_lead_time_seconds": round(float(np.mean(lead_times)), 1) if lead_times else None,
                    "median_lead_time_seconds": round(float(np.median(lead_times)), 1) if lead_times else None,
                    "mean_eta_error_seconds": round(float(np.mean(eta_errors)), 1) if eta_errors else None,
                    "median_eta_error_seconds": round(float(np.median(eta_errors)), 1) if eta_errors else None,
                }

        results = {
            "evaluation_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_windows_evaluated": len(df_sorted),
            "total_forecast_events_emitted": len(forecast_events),
            "attack_onsets_identified": [
                {
                    "timestamp": o["timestamp"].isoformat(),
                    "attack_class": o["attack_class"],
                    "transition": o["type"]
                }
                for o in onsets
            ],
            "horizon_metrics": horizon_results,
            "timeline_data": timeline_records
        }

        return results

    def plot_timeline(
        self,
        timeline_data: List[Dict[str, Any]],
        output_png_path: str = "reports/phase5_risk_timeline.png",
    ) -> None:
        """
        Generates publication-quality risk trajectory visualization
        showing Risk Score, Risk States, Predicted Class, and Forecast Events.
        """
        os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
        times = [d["timestamp"] for d in timeline_data]
        risks = [d["risk_score"] for d in timeline_data]
        forecast_flags = [d["forecast_available"] for d in timeline_data]

        plt.figure(figsize=(15, 6), dpi=150)
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

        # Plot risk curve
        plt.plot(times, risks, color="#1E88E5", linewidth=2.0, label="Fused Security Risk Score", zorder=3)

        # Plot State Bands
        plt.axhspan(0.00, 0.24, color="#4CAF50", alpha=0.10, label="LOW Risk (0.00–0.24)")
        plt.axhspan(0.24, 0.49, color="#FFC107", alpha=0.10, label="GUARDED Risk (0.25–0.49)")
        plt.axhspan(0.49, 0.74, color="#FF9800", alpha=0.12, label="ELEVATED Risk (0.50–0.74)")
        plt.axhspan(0.74, 1.00, color="#E53935", alpha=0.15, label="HIGH Risk (0.75–1.00)")

        # Highlight Forecast Events
        f_times = [times[i] for i, f in enumerate(forecast_flags) if f]
        f_risks = [risks[i] for i, f in enumerate(forecast_flags) if f]
        if f_times:
            plt.scatter(
                f_times, f_risks, color="#E53935", s=60, marker="^",
                label="Forecast Event Emitted", zorder=5, edgecolors="black"
            )

        plt.title("SENTRANET — Temporal Risk Trajectory & Forecast Timeline (Phase 5)", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Time (Chronological Windows)", fontsize=10, labelpad=8)
        plt.ylabel("Security Risk Score [0.0, 1.0]", fontsize=10, labelpad=8)
        plt.ylim(-0.02, 1.05)

        # Formatting
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9, fontsize=8)
        plt.tight_layout()

        plt.savefig(output_png_path, dpi=150)
        plt.close()
