"""
SENTRANET — Cross-Dataset Summary Generator (Phase 10)
Aggregates individual evaluation results from artifacts/evaluation/<dataset>/summary.json
into the centralized cross_dataset_summary.json.
"""

from typing import Dict, Any, List
import os
import json
from datetime import datetime, timezone

from ml.evaluation.manifest import DATASET_SPECS


def generate_cross_dataset_summary(
    eval_dir: str = "artifacts/evaluation",
    output_path: str = "artifacts/evaluation/cross_dataset_summary.json",
) -> Dict[str, Any]:
    """Scans all dataset evaluation summaries and creates the unified comparison manifest."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluation_type": "FROZEN_MODEL",
        "model_provenance": "Phase 2-5 Frozen Models (Category B Synthetic-Trained)",
        "datasets": {},
    }

    for d_id, spec in DATASET_SPECS.items():
        dataset_summary_file = os.path.join(eval_dir, d_id, "summary.json")

        if os.path.exists(dataset_summary_file):
            try:
                with open(dataset_summary_file, "r", encoding="utf-8") as f:
                    d_data = json.load(f)

                status = d_data.get("status", "UNKNOWN")
                if status == "COMPLETED":
                    summary["datasets"][d_id] = {
                        "name": d_data.get("name", spec["name"]),
                        "category": d_data.get("category", spec["category"]),
                        "status": "completed",
                        "evaluation_mode": d_data.get("evaluation_mode"),
                        "windows": d_data.get("windows_evaluated", 0),
                        "macro_f1": d_data.get("classification", {}).get("macro_f1"),
                        "weighted_f1": d_data.get("classification", {}).get("weighted_f1"),
                        "accuracy": d_data.get("classification", {}).get("accuracy"),
                        "false_alarms_per_hour": d_data.get("false_positives", {}).get("false_alarms_per_hour"),
                        "attack_detection_rate": d_data.get("anomaly_detection", {}).get("attack_detection_rate"),
                        "forecast_mean_lead_time_seconds": d_data.get("forecasting", {}).get("mean_lead_time_seconds"),
                        "throughput_windows_sec": d_data.get("performance", {}).get("throughput_windows_per_second"),
                    }
                else:
                    summary["datasets"][d_id] = {
                        "name": spec["name"],
                        "category": spec["category"],
                        "status": "not_available",
                        "windows": 0,
                        "macro_f1": None,
                        "weighted_f1": None,
                        "accuracy": None,
                        "false_alarms_per_hour": None,
                        "attack_detection_rate": None,
                        "forecast_mean_lead_time_seconds": None,
                        "throughput_windows_sec": None,
                        "message": d_data.get("message", "Dataset raw files not available locally."),
                    }
            except Exception as e:
                summary["datasets"][d_id] = {
                    "name": spec["name"],
                    "category": spec["category"],
                    "status": "error",
                    "error": str(e),
                }
        else:
            summary["datasets"][d_id] = {
                "name": spec["name"],
                "category": spec["category"],
                "status": "not_available",
                "windows": 0,
                "macro_f1": None,
                "weighted_f1": None,
                "accuracy": None,
                "false_alarms_per_hour": None,
                "attack_detection_rate": None,
                "forecast_mean_lead_time_seconds": None,
                "throughput_windows_sec": None,
                "message": f"Dataset raw files not available in '{spec['expected_path']}'.",
            }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
