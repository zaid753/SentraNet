"""
SENTRANET — Isolation Forest Anomaly Detection Service (Phase 4)
Provides unsupervised behavioral unusualness estimation, normalized anomaly scoring,
and standardized DecisionObject integration without API dependencies.
"""

from typing import Dict, Any, List, Optional, Union
import os
import json
import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger("sentranet.isolation_forest")

class IsolationForestDetector:
    """
    Unsupervised behavioral anomaly detector for SENTRANET.
    Learns normal baseline traffic and estimates deviation/unusualness.
    Produces deterministic, normalized anomaly scores in [0.0, 1.0].
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        reference_path: Optional[str] = None,
        feature_names_path: Optional[str] = None,
    ):
        self.model: Optional[IsolationForest] = None
        self.reference: Dict[str, Any] = {}
        self.expected_features: List[str] = []
        self.threshold: float = 0.50
        self.s_high: float = 0.10
        self.s_low: float = -0.25

        if model_path:
            self.load_model(model_path, reference_path, feature_names_path)

    def load_model(
        self,
        model_path: str,
        reference_path: Optional[str] = None,
        feature_names_path: Optional[str] = None,
    ) -> None:
        """Loads serialized Isolation Forest joblib model, calibration reference, and schema."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Isolation Forest model file '{model_path}' does not exist.")

        self.model = joblib.load(model_path)

        model_dir = os.path.dirname(model_path)
        ref_path = reference_path or os.path.join(model_dir, "anomaly_reference.json")

        if os.path.exists(ref_path):
            with open(ref_path, "r", encoding="utf-8") as f:
                self.reference = json.load(f)
                self.threshold = float(self.reference.get("threshold", 0.50))
                self.s_high = float(self.reference.get("reference_high", 0.10))
                self.s_low = float(self.reference.get("reference_low", -0.25))
        else:
            raise FileNotFoundError(f"Anomaly reference file '{ref_path}' missing.")

        # Load feature schema: prefer reference metadata, explicit path, or feature_names.json
        if feature_names_path and os.path.exists(feature_names_path):
            with open(feature_names_path, "r", encoding="utf-8") as f:
                self.expected_features = json.load(f).get("features", [])
        elif "features" in self.reference:
            self.expected_features = self.reference["features"]
        elif os.path.exists(os.path.join(model_dir, "training_metadata.json")):
            with open(os.path.join(model_dir, "training_metadata.json"), "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.expected_features = meta.get("features", [])
        elif os.path.exists("data/processed/sample/feature_names.json"):
            with open("data/processed/sample/feature_names.json", "r", encoding="utf-8") as f:
                self.expected_features = json.load(f).get("features", [])

        if len(self.expected_features) != 17:
            logger.warning(f"Expected 17 features, but found {len(self.expected_features)}")

        logger.info(
            f"Loaded Isolation Forest model successfully with threshold={self.threshold:.4f}, "
            f"features={len(self.expected_features)}"
        )

    def _prepare_matrix(self, features: Union[pd.DataFrame, np.ndarray, List[Dict[str, Any]], Dict[str, Any]]) -> np.ndarray:
        """Validates input features for dimension, schema alignment, missingness, NaNs, and infinities."""
        if self.model is None:
            raise RuntimeError("Model has not been loaded. Call load_model() first.")

        if isinstance(features, dict):
            df = pd.DataFrame([features])
        elif isinstance(features, list) and len(features) > 0 and isinstance(features[0], dict):
            df = pd.DataFrame(features)
        elif isinstance(features, pd.DataFrame):
            df = features.copy()
        elif isinstance(features, np.ndarray):
            if features.ndim == 1:
                features = features.reshape(1, -1)
            if features.shape[1] != len(self.expected_features):
                raise ValueError(
                    f"Invalid feature dimension: array has {features.shape[1]} features, "
                    f"expected {len(self.expected_features)} ({self.expected_features})"
                )
            df = pd.DataFrame(features, columns=self.expected_features)
        else:
            raise TypeError(f"Unsupported features type: {type(features)}")

        missing_features = [f for f in self.expected_features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Input features missing required columns: {missing_features}")

        X_df = df[self.expected_features]

        if X_df.isna().any().any():
            raise ValueError("Input feature matrix contains NaN values. Sanitization required.")

        arr = X_df.values.astype(np.float64)
        if np.isinf(arr).any():
            raise ValueError("Input feature matrix contains Infinite values. Sanitization required.")

        return arr

    def raw_decision_function(self, features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """
        Returns the raw sklearn decision_function output.
        Positive = inlier / normal baseline. Negative = outlier / anomalous.
        """
        arr = self._prepare_matrix(features)
        return self.model.decision_function(arr)

    def score_samples(self, features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """Returns the raw sklearn score_samples output (opposite of anomaly score)."""
        arr = self._prepare_matrix(features)
        return self.model.score_samples(arr)

    def anomaly_score(self, features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """
        Transforms raw decision function into a normalized anomaly score in [0.0, 1.0].
        0.0 = deep normal baseline
        1.0 = highly anomalous / severe behavioral deviation

        Transformation:
            anomaly_score = clip((s_high - s) / (s_high - s_low), 0.0, 1.0)
        where s_high and s_low are derived strictly from the training benign distribution.
        """
        raw_s = self.raw_decision_function(features)
        denom = self.s_high - self.s_low
        if denom == 0:
            denom = 1.0
        normalized = (self.s_high - raw_s) / denom
        return np.clip(normalized, 0.0, 1.0)

    def is_anomalous(self, features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]) -> List[bool]:
        """
        Evaluates whether each observation exceeds the anomaly threshold.
        Threshold is established from training benign percentiles without attack labels.
        """
        scores = self.anomaly_score(features)
        return [bool(score >= self.threshold) for score in scores]

    def predict_decision(
        self,
        features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]],
        timestamp: Optional[Union[str, List[str]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Builds Phase 4 DecisionObjects populated with genuine anomaly detection telemetry.
        Fields requiring Phase 5 (risk_score, time_to_impact_seconds) remain null.
        """
        scores = self.anomaly_score(features)
        flags = self.is_anomalous(features)
        num_samples = len(scores)

        if timestamp is None:
            ts_list = [datetime.datetime.now(datetime.timezone.utc).isoformat()] * num_samples
        elif isinstance(timestamp, str):
            ts_list = [timestamp] * num_samples
        else:
            ts_list = list(timestamp)

        decisions = []
        for i in range(num_samples):
            decisions.append({
                "timestamp": ts_list[i],
                "predicted_class": None,
                "class_probabilities": None,
                "classification_confidence": None,
                "anomaly_score": float(round(float(scores[i]), 4)),
                "is_anomalous": bool(flags[i]),
                "risk_score": None,
                "time_to_impact_seconds": None,
                "forecast_available": False,
                "explanation": None,
            })

        return decisions
