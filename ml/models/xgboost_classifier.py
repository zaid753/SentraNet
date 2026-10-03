"""Reusable, decoupled XGBoost inference service for SENTRANET attack classification."""

from typing import Dict, Any, List, Optional, Union
import os
import json
import datetime
import numpy as np
import pandas as pd
import xgboost as xgb
import logging

logger = logging.getLogger("sentranet.xgboost")

class XGBoostClassifier:
    """
    Inference service for the 5-class SENTRANET supervised attack classifier.
    Exposes predict, predict_proba, and standard DecisionObject builders.
    No web framework dependencies.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        class_mapping_path: Optional[str] = None,
        feature_names_path: Optional[str] = None,
    ):
        self.booster: Optional[xgb.Booster] = None
        self.classes: List[str] = []
        self.class_to_idx: Dict[str, int] = {}
        self.idx_to_class: Dict[int, str] = {}
        self.expected_features: List[str] = []

        if model_path:
            self.load_model(model_path, class_mapping_path, feature_names_path)

    def load_model(
        self,
        model_path: str,
        class_mapping_path: Optional[str] = None,
        feature_names_path: Optional[str] = None,
    ) -> None:
        """Loads serialized XGBoost booster JSON model and feature/class schemas."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file '{model_path}' does not exist.")

        if model_path.endswith('.joblib'):
            import joblib
            model = joblib.load(model_path)
            if hasattr(model, 'get_booster'):
                self.booster = model.get_booster()
            else:
                self.booster = model
        else:
            self.booster = xgb.Booster()
            self.booster.load_model(model_path)

        # Resolve paths if not given explicitly
        model_dir = os.path.dirname(model_path)
        cls_path = class_mapping_path or os.path.join(model_dir, "class_mapping.json")
        feat_path = feature_names_path or os.path.join(model_dir, "feature_importance.json")

        # Load class mapping
        if os.path.exists(cls_path):
            with open(cls_path, "r", encoding="utf-8") as f:
                mapping_data = json.load(f)
                self.classes = mapping_data["classes"]
                self.class_to_idx = mapping_data["class_to_index"]
                self.idx_to_class = {int(v): k for k, v in self.class_to_idx.items()}
        else:
            raise FileNotFoundError(f"Class mapping '{cls_path}' missing.")

        # Load feature names: booster metadata, training_metadata, or feature_names.json
        if feature_names_path and os.path.exists(feature_names_path):
            with open(feature_names_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.expected_features = data.get("features", [])
        elif self.booster.feature_names:
            self.expected_features = list(self.booster.feature_names)
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
            f"Loaded XGBoost model successfully with {len(self.classes)} classes and "
            f"{len(self.expected_features)} expected features."
        )

    def _prepare_dmatrix(self, features: Union[pd.DataFrame, np.ndarray, List[Dict[str, Any]], Dict[str, Any]]) -> xgb.DMatrix:
        """Validates input features for dimension, missingness, NaNs, and infinities."""
        if self.booster is None:
            raise RuntimeError("Model has not been loaded. Call load_model() first.")

        # Convert dict or list of dicts to DataFrame
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

        # Verify all expected features are present
        missing_features = [f for f in self.expected_features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Input features missing required columns: {missing_features}")

        # Reorder to strict expected feature ordering
        X_df = df[self.expected_features]

        # NaN & Infinity Checks
        if X_df.isna().any().any():
            raise ValueError("Input feature matrix contains NaN values. Sanitization required.")

        arr = X_df.values.astype(np.float64)
        if np.isinf(arr).any():
            raise ValueError("Input feature matrix contains Infinite values. Sanitization required.")

        return xgb.DMatrix(arr, feature_names=self.expected_features)

    def predict_proba(self, features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """
        Returns full probability distribution across all 5 classes.
        Output shape: (N, 5), where sum along axis=1 is ~ 1.0.
        """
        dmat = self._prepare_dmatrix(features)
        proba = self.booster.predict(dmat)
        # Handle 1D return if single sample
        if proba.ndim == 1 and len(self.classes) > 1:
            proba = proba.reshape(1, -1)

        # Softmax normalize if necessary to guarantee sum is exactly 1.0
        row_sums = proba.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        normalized_proba = proba / row_sums
        return normalized_proba

    def predict(self, features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]) -> List[str]:
        """Returns the predicted class string name for each input record."""
        proba = self.predict_proba(features)
        pred_indices = np.argmax(proba, axis=1)
        return [self.idx_to_class[idx] for idx in pred_indices]

    def predict_decision(
        self,
        features: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]],
        timestamp: Optional[Union[str, List[str]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Builds standardized Phase 1 DecisionObjects populated with genuine classification telemetry.
        Fields requiring later phases (anomaly_score, risk_score, time_to_impact) remain null.
        """
        proba = self.predict_proba(features)
        pred_classes = self.predict(features)

        num_samples = len(pred_classes)
        if timestamp is None:
            ts_list = [datetime.datetime.now(datetime.timezone.utc).isoformat()] * num_samples
        elif isinstance(timestamp, str):
            ts_list = [timestamp] * num_samples
        else:
            ts_list = list(timestamp)

        decisions = []
        for i in range(num_samples):
            class_probs = {self.classes[c_idx]: float(round(proba[i, c_idx], 4)) for c_idx in range(len(self.classes))}
            confidence = float(round(float(np.max(proba[i])), 4))

            decisions.append({
                "timestamp": ts_list[i],
                "predicted_class": pred_classes[i],
                "class_probabilities": class_probs,
                "classification_confidence": confidence,
                "anomaly_score": None,
                "risk_score": None,
                "time_to_impact_seconds": None,
                "forecast_available": False,
                "explanation": None,
            })

        return decisions
