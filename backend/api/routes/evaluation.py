"""
SENTRANET — Evaluation Routes (Phase 10)
Serves benchmark evaluation artifacts — always read-only, frozen model results.

These endpoints distinguish:
  - Category B: Synthetic Development Fixture (sample)
  - Category A: Real Benchmark Captures (CICIDS2017, UNSW-NB15, CIC-DDoS2019)
"""
import json
import os
from typing import Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

ARTIFACTS_ROOT = "artifacts/evaluation"
SUMMARY_PATH = os.path.join(ARTIFACTS_ROOT, "cross_dataset_summary.json")
DATASET_KEYS = ["sample", "cicids2017", "unsw_nb15", "cic_ddos2019"]

ARTIFACT_FILES = [
    "summary.json",
    "quality.json",
    "class_distribution.json",
    "classification_metrics.json",
    "confusion_matrix.json",
    "anomaly_metrics.json",
    "risk_metrics.json",
    "forecast_metrics.json",
    "performance.json",
]


def _load_json(path: str) -> Optional[dict]:
    """Load JSON file safely, return None if missing."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@router.get("/summary")
def get_evaluation_summary():
    """
    GET /api/evaluation/summary

    Returns the cross-dataset evaluation summary.
    Shows frozen model performance across all evaluated datasets.
    Clearly marks which datasets are AVAILABLE vs NOT_AVAILABLE.

    Note: Metrics labeled BENCHMARK EVALUATION — Frozen Models.
    Do NOT interpret these as live telemetry metrics.
    """
    data = _load_json(SUMMARY_PATH)
    if data is None:
        return {
            "status": "NO_EVALUATION",
            "message": "No benchmark evaluation has been run yet. "
                       "Run: python -m scripts.evaluate_benchmark --all",
            "datasets": {},
            "evaluation_type": "none",
            "display_label": "BENCHMARK EVALUATION — Frozen Models",
        }
    return {
        **data,
        "display_label": "BENCHMARK EVALUATION — Frozen Models",
        "caution": (
            "These are out-of-sample evaluation metrics for the frozen SENTRANET AI Core. "
            "Category A (Real Benchmark) datasets require external download. "
            "Do NOT interpret these metrics as live production accuracy."
        ),
    }


@router.get("/{dataset}")
def get_dataset_evaluation(dataset: str):
    """
    GET /api/evaluation/{dataset}

    Returns full evaluation results for a specific dataset.
    dataset: sample | cicids2017 | unsw_nb15 | cic_ddos2019

    Returns NOT_AVAILABLE if the dataset was not evaluated or raw files are missing.
    """
    dataset_key = dataset.lower().replace("-", "_")
    if dataset_key not in DATASET_KEYS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown dataset '{dataset}'. Valid options: {DATASET_KEYS}",
        )

    dataset_dir = os.path.join(ARTIFACTS_ROOT, dataset_key)
    summary = _load_json(os.path.join(dataset_dir, "summary.json"))

    if summary is None:
        return {
            "status": "NOT_EVALUATED",
            "dataset": dataset_key,
            "message": (
                f"Dataset '{dataset_key}' has not been evaluated. "
                "Run: python -m scripts.evaluate_benchmark --dataset "
                + dataset_key
            ),
        }

    # If the dataset was not available, return the summary as-is
    if summary.get("status") == "NOT_AVAILABLE":
        return summary

    # Load all artifact files and bundle them
    artifacts = {"summary": summary}
    for fname in ARTIFACT_FILES[1:]:  # skip summary.json (already loaded)
        key = fname.replace(".json", "")
        artifacts[key] = _load_json(os.path.join(dataset_dir, fname))

    return {
        "status": "COMPLETED",
        "dataset": dataset_key,
        "evaluation_type": "FROZEN_MODEL",
        "display_label": "BENCHMARK EVALUATION — Frozen Models",
        "mode_note": (
            "BENCHMARK EVALUATION. These results use frozen SENTRANET Phase 3 XGBoost + "
            "Phase 4 Isolation Forest. No retraining occurred."
        ),
        **artifacts,
    }
