"""
SENTRANET — Comprehensive Benchmark Evaluator (Phase 10)
Executes frozen-model evaluations on network attack benchmarks:
- XGBoost multi-class metrics & confusion matrix
- Isolation Forest anomaly detection & score distribution
- Dual Engine Risk Fusion & risk state calibration
- Temporal attack episode reconstruction, forecasting lead times, and ETA error
- Performance benchmarking (latency, throughput)
- Safe handling of missing datasets without crashing
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import json
import time
import math
import numpy as np
import pandas as pd
from datetime import datetime, timezone

from ml.forecast.forecast_engine import ForecastEngine
from ml.evaluation.xgboost_metrics import XGBoostMetricsEvaluator
from ml.evaluation.manifest import audit_dataset_availability, DATASET_SPECS
from ml.preprocessing.labels import TARGET_CLASSES, normalize_label
from ml.preprocessing.pipeline import PreprocessingPipeline

CANONICAL_17_FEATURES = [
    "flow_count",
    "total_packets",
    "total_bytes",
    "avg_packet_rate",
    "avg_byte_rate",
    "unique_sources",
    "unique_destinations",
    "avg_packet_size",
    "avg_flow_duration",
    "syn_flag_count",
    "ack_flag_count",
    "privileged_port_ratio",
    "rolling_5_flow_count",
    "rolling_5_total_packets",
    "rolling_5_total_bytes",
    "rolling_5_avg_byte_rate",
    "rolling_5_unique_sources",
]


class BenchmarkEvaluator:
    """
    Evaluates the frozen SENTRANET AI Core against real network security benchmarks
    and synthetic development fixtures.
    """

    def __init__(
        self,
        output_base_dir: str = "artifacts/evaluation",
        forecast_engine: Optional[ForecastEngine] = None,
    ):
        self.output_base_dir = output_base_dir
        self.class_names = TARGET_CLASSES
        self.forecast_engine = forecast_engine or ForecastEngine()
        self.metrics_evaluator = XGBoostMetricsEvaluator(class_names=self.class_names)

    def evaluate_dataset(
        self,
        dataset_id: str,
        max_windows: Optional[int] = None,
        generate_plots: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes frozen model evaluation on a benchmark dataset.
        Handles missing datasets gracefully by returning a structured NOT_AVAILABLE report.
        """
        dataset_key = dataset_id.lower().replace("-", "_")
        target_dir = os.path.join(self.output_base_dir, dataset_key)
        os.makedirs(target_dir, exist_ok=True)

        # 1. Audit Dataset Availability
        availability = audit_dataset_availability(dataset_key)
        if not availability["available"]:
            not_avail_report = {
                "dataset_id": dataset_key,
                "name": availability["name"],
                "category": availability["category"],
                "status": "NOT_AVAILABLE",
                "evaluation_type": "FROZEN_MODEL",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "message": (
                    f"Dataset '{dataset_key}' is not available locally. "
                    f"Raw benchmark files are missing from '{availability['expected_path']}'."
                ),
                "expected_path": availability["expected_path"],
                "missing_files": availability["missing_files"],
                "download_instructions": availability["download_instructions"],
                "metrics": None,
            }
            with open(os.path.join(target_dir, "summary.json"), "w", encoding="utf-8") as f:
                json.dump(not_avail_report, f, indent=2)
            return not_avail_report

        # 2. Discover or Load Processed Temporal Windows
        window_df, quality_info = self._load_or_preprocess_windows(dataset_key, max_rows=None)

        if window_df.empty:
            empty_report = {
                "dataset_id": dataset_key,
                "name": availability["name"],
                "category": availability["category"],
                "status": "EMPTY_DATASET",
                "evaluation_type": "FROZEN_MODEL",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "message": f"Dataset '{dataset_key}' contains no valid temporal windows.",
                "metrics": None,
            }
            with open(os.path.join(target_dir, "summary.json"), "w", encoding="utf-8") as f:
                json.dump(empty_report, f, indent=2)
            return empty_report

        # Sort chronologically (strict causality requirement)
        window_df = window_df.sort_values("window_start").reset_index(drop=True)

        is_quick = max_windows is not None and len(window_df) > max_windows
        if max_windows:
            window_df = window_df.iloc[:max_windows].copy()

        total_windows = len(window_df)

        # 3. Execute Frozen AI Core Inference Over Chronological Stream
        inference_start_time = time.time()
        self.forecast_engine.reset()

        y_true_labels: List[str] = []
        y_pred_labels: List[str] = []
        y_true_indices: List[int] = []
        y_pred_indices: List[int] = []
        y_probabilities: List[List[float]] = []

        anomaly_scores: List[float] = []
        is_anomalous_flags: List[bool] = []
        risk_scores: List[float] = []
        risk_states: List[str] = []
        forecast_events: List[Dict[str, Any]] = []

        window_latencies_ms: List[float] = []

        class_to_idx = {c: i for i, c in enumerate(self.class_names)}

        for idx, row in window_df.iterrows():
            features_dict = {f: float(row[f]) for f in CANONICAL_17_FEATURES}
            ts_str = str(row["window_start"])
            true_label = str(row.get("label", "BENIGN"))
            norm_true_label = normalize_label(true_label, dataset_key)

            # Measure per-window latency
            t0 = time.perf_counter()
            decision = self.forecast_engine.update(window=features_dict, timestamp=ts_str)
            t_elapsed = (time.perf_counter() - t0) * 1000.0  # ms
            window_latencies_ms.append(t_elapsed)

            pred_class = decision["predicted_class"]
            probs_dict = decision["class_probabilities"]
            prob_vector = [float(probs_dict.get(c, 0.0)) for c in self.class_names]

            y_true_labels.append(norm_true_label)
            y_pred_labels.append(pred_class)
            y_true_indices.append(class_to_idx.get(norm_true_label, 4))
            y_pred_indices.append(class_to_idx.get(pred_class, 4))
            y_probabilities.append(prob_vector)

            anomaly_scores.append(float(decision["anomaly_score"]))
            is_anomalous_flags.append(bool(decision["is_anomalous"]))
            risk_scores.append(float(decision["risk_score"]))
            risk_states.append(str(decision["risk_state"]))

            if decision.get("forecast_available", False):
                forecast_events.append({
                    "window_index": idx,
                    "timestamp": ts_str,
                    "forecast_class": decision.get("forecast_class"),
                    "confidence": float(decision.get("forecast_confidence") or 0.0),
                    "eta_seconds": decision.get("time_to_impact_seconds"),
                    "risk_score": float(decision["risk_score"]),
                    "anomaly_score": float(decision["anomaly_score"]),
                })

        total_inference_time = time.time() - inference_start_time

        # 4. Compute Comprehensive Metric Suites
        # A. Classification Metrics (XGBoost)
        xgb_metrics = self.metrics_evaluator.evaluate(
            y_true=np.array(y_true_indices),
            y_pred=np.array(y_pred_indices),
            y_proba=np.array(y_probabilities),
            split_name=f"{dataset_key}_{'quick' if is_quick else 'full'}",
        )

        # B. Class Distribution
        class_series = pd.Series(y_true_labels)
        class_counts = class_series.value_counts().to_dict()
        class_percentages = (class_series.value_counts(normalize=True) * 100.0).round(2).to_dict()
        class_distribution = {
            "total_windows": total_windows,
            "counts": class_counts,
            "percentages": class_percentages,
        }

        # C. Benign False Positive Analysis
        benign_indices = [i for i, lbl in enumerate(y_true_labels) if lbl == "BENIGN"]
        actual_benign_count = len(benign_indices)
        benign_fp_count = sum(1 for i in benign_indices if y_pred_labels[i] != "BENIGN")
        benign_fpr = (benign_fp_count / actual_benign_count) if actual_benign_count > 0 else 0.0

        # Duration in hours
        ts_series = pd.to_datetime(window_df["window_start"])
        if len(ts_series) >= 2:
            time_span_seconds = max(1.0, (ts_series.iloc[-1] - ts_series.iloc[0]).total_seconds())
            time_span_hours = time_span_seconds / 3600.0
            false_alarms_per_hour = round(benign_fp_count / time_span_hours, 3)
        else:
            time_span_hours = 1.0 / 60.0
            false_alarms_per_hour = float(benign_fp_count)

        benign_fp_analysis = {
            "actual_benign_windows": actual_benign_count,
            "false_positive_count": benign_fp_count,
            "false_positive_rate": round(benign_fpr, 4),
            "time_span_hours": round(time_span_hours, 2),
            "false_alarms_per_hour": false_alarms_per_hour,
        }

        # D. Isolation Forest Anomaly Analysis
        anomaly_scores_np = np.array(anomaly_scores)
        is_attack_bool = np.array([lbl != "BENIGN" for lbl in y_true_labels])
        benign_anomaly_scores = anomaly_scores_np[~is_attack_bool] if (~is_attack_bool).any() else np.array([])
        attack_anomaly_scores = anomaly_scores_np[is_attack_bool] if is_attack_bool.any() else np.array([])

        def calc_dist(arr: np.ndarray) -> Dict[str, Optional[float]]:
            if len(arr) == 0:
                return {"mean": None, "median": None, "p95": None, "p99": None}
            return {
                "mean": round(float(np.mean(arr)), 4),
                "median": round(float(np.median(arr)), 4),
                "p95": round(float(np.percentile(arr, 95)), 4),
                "p99": round(float(np.percentile(arr, 99)), 4),
            }

        attack_windows_count = int(is_attack_bool.sum())
        detected_attacks = int((np.array(is_anomalous_flags) & is_attack_bool).sum())
        attack_detection_rate = (detected_attacks / attack_windows_count) if attack_windows_count > 0 else None

        false_anomalous_benign = int((np.array(is_anomalous_flags) & (~is_attack_bool)).sum())
        benign_anomaly_fpr = (false_anomalous_benign / actual_benign_count) if actual_benign_count > 0 else None

        anomaly_metrics = {
            "operational_threshold": self.forecast_engine.anomaly_detector.threshold,
            "benign_score_distribution": calc_dist(benign_anomaly_scores),
            "attack_score_distribution": calc_dist(attack_anomaly_scores),
            "attack_detection_rate": round(attack_detection_rate, 4) if attack_detection_rate is not None else None,
            "benign_anomaly_fpr": round(benign_anomaly_fpr, 4) if benign_anomaly_fpr is not None else None,
        }

        # E. Dual Engine Risk Fusion Analysis
        risk_series = pd.Series(risk_states)
        risk_counts = risk_series.value_counts().to_dict()

        # Breakdown by benign vs attack
        benign_risk_states = pd.Series([risk_states[i] for i in benign_indices]).value_counts().to_dict()
        attack_indices = [i for i, lbl in enumerate(y_true_labels) if lbl != "BENIGN"]
        attack_risk_states = pd.Series([risk_states[i] for i in attack_indices]).value_counts().to_dict()

        false_high_windows = benign_risk_states.get("HIGH", 0)
        attack_high_windows = attack_risk_states.get("HIGH", 0)
        attack_high_rate = (attack_high_windows / attack_windows_count) if attack_windows_count > 0 else None

        risk_metrics = {
            "fusion_formula": "clip(0.60 * S_attack + 0.40 * anomaly_score, 0, 1)",
            "risk_state_counts": risk_counts,
            "benign_risk_distribution": benign_risk_states,
            "attack_risk_distribution": attack_risk_states,
            "false_high_count": false_high_windows,
            "attack_high_rate": round(attack_high_rate, 4) if attack_high_rate is not None else None,
        }

        # F. Temporal Attack Episodes & Forecast Evaluation
        forecast_results = self._evaluate_forecasting(
            window_df=window_df,
            y_true_labels=y_true_labels,
            forecast_events=forecast_events,
        )

        # G. Performance Latency
        performance_metrics = {
            "total_windows_evaluated": total_windows,
            "total_inference_time_seconds": round(total_inference_time, 3),
            "throughput_windows_per_second": round(total_windows / max(0.001, total_inference_time), 1),
            "latency_ms_mean": round(float(np.mean(window_latencies_ms)), 2),
            "latency_ms_median": round(float(np.median(window_latencies_ms)), 2),
            "latency_ms_p95": round(float(np.percentile(window_latencies_ms, 95)), 2),
        }

        # 5. Persist All Modular JSON Artifacts
        with open(os.path.join(target_dir, "quality.json"), "w", encoding="utf-8") as f:
            json.dump(quality_info, f, indent=2)

        with open(os.path.join(target_dir, "class_distribution.json"), "w", encoding="utf-8") as f:
            json.dump(class_distribution, f, indent=2)

        with open(os.path.join(target_dir, "classification_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(xgb_metrics, f, indent=2)

        with open(os.path.join(target_dir, "confusion_matrix.json"), "w", encoding="utf-8") as f:
            json.dump({
                "classes": self.class_names,
                "matrix": xgb_metrics["confusion_matrix"]["matrix"],
            }, f, indent=2)

        with open(os.path.join(target_dir, "anomaly_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(anomaly_metrics, f, indent=2)

        with open(os.path.join(target_dir, "risk_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(risk_metrics, f, indent=2)

        with open(os.path.join(target_dir, "forecast_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(forecast_results, f, indent=2)

        with open(os.path.join(target_dir, "performance.json"), "w", encoding="utf-8") as f:
            json.dump(performance_metrics, f, indent=2)

        # 6. Render Confusion Matrix Plot (if enabled)
        if generate_plots:
            cm_plot_path = os.path.join(target_dir, "confusion_matrix.png")
            cm_arr = np.array(xgb_metrics["confusion_matrix"]["matrix"], dtype=int)
            self.metrics_evaluator.plot_confusion_matrix(
                cm=cm_arr,
                output_path=cm_plot_path,
                title=f"Confusion Matrix — {availability['name']} ({'Quick' if is_quick else 'Full'})",
            )

        # 7. Build Unified Evaluation Summary
        summary_payload = {
            "dataset_id": dataset_key,
            "name": availability["name"],
            "category": availability["category"],
            "status": "COMPLETED",
            "evaluation_type": "FROZEN_MODEL",
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "evaluation_mode": "QUICK EVALUATION — NOT FULL DATASET" if is_quick else "FULL EVALUATION",
            "model_version": {
                "xgboost": "models/xgboost/sentranet_xgboost.json",
                "isolation_forest": "models/isolation_forest/sentranet_isolation_forest.joblib",
                "scaler": "SafeFeatureScaler (Phase 2 Standard)",
            },
            "windows_evaluated": total_windows,
            "classification": {
                "accuracy": xgb_metrics.get("accuracy_reference"),
                "macro_f1": xgb_metrics.get("macro_f1"),
                "weighted_f1": xgb_metrics.get("weighted_f1"),
                "macro_pr_auc": xgb_metrics.get("macro_pr_auc"),
                "log_loss": xgb_metrics.get("multiclass_log_loss"),
            },
            "false_positives": benign_fp_analysis,
            "anomaly_detection": anomaly_metrics,
            "risk_fusion": risk_metrics,
            "forecasting": {
                "attack_onsets_count": forecast_results["attack_onsets_count"],
                "forecasted_onsets_count": forecast_results["forecasted_onsets_count"],
                "mean_lead_time_seconds": forecast_results["lead_times"]["mean"],
                "median_lead_time_seconds": forecast_results["lead_times"]["median"],
                "horizon_1m_f1": forecast_results["horizon_metrics"]["1m"]["f1"],
                "horizon_5m_f1": forecast_results["horizon_metrics"]["5m"]["f1"],
            },
            "performance": performance_metrics,
        }

        with open(os.path.join(target_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2)

        return summary_payload

    def _load_or_preprocess_windows(
        self, dataset_id: str, max_rows: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Loads existing processed parquet windows or processes raw dataset."""
        processed_path = f"data/processed/{dataset_id}/test.parquet"
        full_processed_path = f"data/processed/{dataset_id}"

        # If already preprocessed into parquet, load directly
        if os.path.exists(processed_path):
            df = pd.read_parquet(processed_path)
            quality = {
                "dataset": dataset_id,
                "loaded_from": processed_path,
                "window_count": len(df),
                "features_present": [c for c in CANONICAL_17_FEATURES if c in df.columns],
                "cleaned": True,
            }
            return df, quality

        # Check for multiple parquets in directory
        if os.path.exists(full_processed_path) and os.path.isdir(full_processed_path):
            p_files = [
                os.path.join(full_processed_path, f)
                for f in sorted(os.listdir(full_processed_path))
                if f.endswith(".parquet") and not f.startswith(".")
            ]
            if p_files:
                dfs = [pd.read_parquet(pf) for pf in p_files]
                combined = pd.concat(dfs, ignore_index=True)
                quality = {
                    "dataset": dataset_id,
                    "loaded_from": full_processed_path,
                    "partitions": [os.path.basename(pf) for pf in p_files],
                    "window_count": len(combined),
                    "features_present": [c for c in CANONICAL_17_FEATURES if c in combined.columns],
                    "cleaned": True,
                }
                return combined, quality

        # Otherwise, run PreprocessingPipeline if raw files exist
        spec = DATASET_SPECS.get(dataset_id, {})
        raw_path = spec.get("expected_path", f"data/raw/{dataset_id}")
        if os.path.exists(raw_path):
            pipeline = PreprocessingPipeline(
                dataset_name=dataset_id,
                window_size_seconds=60,
                rolling_window_count=5,
            )
            out_dir = f"data/processed/{dataset_id}"
            metadata = pipeline.run(input_path=raw_path, output_dir=out_dir, max_rows=max_rows)
            df = pd.read_parquet(os.path.join(out_dir, "test.parquet"))
            return df, metadata

        return pd.DataFrame(), {"dataset": dataset_id, "status": "no_data"}

    def _evaluate_forecasting(
        self,
        window_df: pd.DataFrame,
        y_true_labels: List[str],
        forecast_events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Reconstructs attack episodes and evaluates forecast precision, recall,
        lead times, and ETA estimation errors.
        """
        # Reconstruct attack episodes (contiguous non-benign windows)
        episodes = []
        in_episode = False
        current_ep = None

        for idx, row in window_df.iterrows():
            lbl = y_true_labels[idx]
            ts = pd.to_datetime(row["window_start"])

            if lbl != "BENIGN":
                if not in_episode:
                    in_episode = True
                    current_ep = {
                        "attack_class": lbl,
                        "onset_index": idx,
                        "onset_timestamp": ts,
                        "end_timestamp": ts,
                        "window_count": 1,
                    }
                else:
                    current_ep["end_timestamp"] = ts
                    current_ep["window_count"] += 1
            else:
                if in_episode:
                    in_episode = False
                    episodes.append(current_ep)
                    current_ep = None

        if in_episode and current_ep:
            episodes.append(current_ep)

        # Match forecasts to attack onsets
        forecasted_count = 0
        lead_times_seconds: List[float] = []
        eta_errors_seconds: List[float] = []

        onset_records = []

        for ep in episodes:
            onset_ts = ep["onset_timestamp"]
            onset_idx = ep["onset_index"]
            att_class = ep["attack_class"]

            # Prior forecasts before onset (within 15 minutes = 900 seconds)
            prior_forecasts = [
                fc for fc in forecast_events
                if fc["window_index"] < onset_idx
                and 0 < (onset_ts - pd.to_datetime(fc["timestamp"])).total_seconds() <= 900
            ]

            if prior_forecasts:
                forecasted_count += 1
                # Earliest valid precursor forecast
                first_fc = prior_forecasts[0]
                fc_ts = pd.to_datetime(first_fc["timestamp"])
                lead_time = (onset_ts - fc_ts).total_seconds()
                lead_times_seconds.append(lead_time)

                # ETA Error: predicted ETA vs actual lead time
                pred_eta = first_fc.get("eta_seconds")
                eta_err = abs(pred_eta - lead_time) if pred_eta is not None else None
                if eta_err is not None:
                    eta_errors_seconds.append(eta_err)

                onset_records.append({
                    "attack_class": att_class,
                    "onset": onset_ts.isoformat(),
                    "forecast_raised": True,
                    "first_forecast": fc_ts.isoformat(),
                    "lead_time_seconds": lead_time,
                    "confidence": first_fc["confidence"],
                    "risk_at_forecast": first_fc["risk_score"],
                    "eta_error_seconds": eta_err,
                })
            else:
                onset_records.append({
                    "attack_class": att_class,
                    "onset": onset_ts.isoformat(),
                    "forecast_raised": False,
                    "first_forecast": None,
                    "lead_time_seconds": None,
                    "confidence": None,
                    "risk_at_forecast": None,
                    "eta_error_seconds": None,
                })

        # Calculate horizon precision/recall across 1m, 2m, 5m, 10m, 15m
        horizons = [1, 2, 5, 10, 15]
        horizon_metrics = {}

        for h in horizons:
            h_seconds = h * 60
            # TP: attack onset that had a forecast within [h_seconds - 60, h_seconds + 60] or up to h_seconds
            tp = sum(1 for rec in onset_records if rec["forecast_raised"] and rec["lead_time_seconds"] <= h_seconds)
            fn = len(episodes) - tp
            # FP: forecast events that were not followed by an attack onset within h_seconds
            fp = 0
            for fc in forecast_events:
                fc_t = pd.to_datetime(fc["timestamp"])
                followed_by_attack = any(
                    0 < (ep["onset_timestamp"] - fc_t).total_seconds() <= h_seconds
                    for ep in episodes
                )
                if not followed_by_attack:
                    fp += 1

            prec = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            rec = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1_h = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

            horizon_metrics[f"{h}m"] = {
                "horizon_minutes": h,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1_h, 4),
            }

        lead_stats = {
            "mean": round(float(np.mean(lead_times_seconds)), 1) if lead_times_seconds else None,
            "median": round(float(np.median(lead_times_seconds)), 1) if lead_times_seconds else None,
            "min": round(float(np.min(lead_times_seconds)), 1) if lead_times_seconds else None,
            "max": round(float(np.max(lead_times_seconds)), 1) if lead_times_seconds else None,
        }

        eta_stats = {
            "mean_eta_error_seconds": round(float(np.mean(eta_errors_seconds)), 1) if eta_errors_seconds else None,
            "median_eta_error_seconds": round(float(np.median(eta_errors_seconds)), 1) if eta_errors_seconds else None,
        }

        return {
            "attack_onsets_count": len(episodes),
            "forecasted_onsets_count": forecasted_count,
            "episodes": onset_records,
            "lead_times": lead_stats,
            "eta_accuracy": eta_stats,
            "horizon_metrics": horizon_metrics,
        }
