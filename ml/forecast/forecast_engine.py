"""
SENTRANET — Forecast Engine (Phase 5)
Orchestrates XGBoost classification, Isolation Forest anomaly scoring,
Risk Fusion, Temporal Trajectory analysis, and causal ETA estimation.
Constructs the complete Phase 5 DecisionObject.
"""

from typing import Dict, Any, List, Optional, Union
import os
import yaml
import numpy as np
import pandas as pd

from ml.models.xgboost_classifier import XGBoostClassifier
from ml.models.isolation_forest_detector import IsolationForestDetector
from ml.risk.risk_fusion import RiskFusionEngine
from ml.risk.risk_trajectory import RiskTrajectoryTracker
from ml.forecast.emergence import AttackEmergenceDetector

DEFAULT_CONFIG_PATH = "config/risk.yaml"

class ForecastEngine:
    """
    Stateful, causal forecasting engine for SENTRANET.
    Maintains temporal context across consecutive windows to detect attack emergence
    and estimate time-to-impact (ETA) without future data leakage.
    """

    def __init__(
        self,
        xgb_model_path: str = "models/xgboost/sentranet_xgboost.json",
        if_model_path: str = "models/isolation_forest/sentranet_isolation_forest.joblib",
        if_reference_path: str = "models/isolation_forest/anomaly_reference.json",
        config_path: str = DEFAULT_CONFIG_PATH,
    ):
        self.config_path = config_path

        # Core Engines
        self.classifier = XGBoostClassifier(model_path=xgb_model_path)
        self.anomaly_detector = IsolationForestDetector(
            model_path=if_model_path,
            reference_path=if_reference_path
        )
        self.risk_fusion = RiskFusionEngine(config_path=config_path)
        self.trajectory_tracker = RiskTrajectoryTracker(config_path=config_path)
        self.emergence_detector = AttackEmergenceDetector(config_path=config_path)

        # Configurable Parameters
        self.target_risk_threshold = 0.75
        self.conf_cls_weight = 0.4
        self.conf_trend_weight = 0.3
        self.conf_ano_weight = 0.3
        self.minimum_history_windows = 3

        self._load_config()

    def _load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "forecast" in cfg:
                        f_cfg = cfg["forecast"]
                        self.target_risk_threshold = float(f_cfg.get("target_risk_threshold", 0.75))
                        self.minimum_history_windows = int(f_cfg.get("minimum_history_windows", 3))
                        c_cfg = f_cfg.get("confidence", {})
                        self.conf_cls_weight = float(c_cfg.get("classification_weight", 0.4))
                        self.conf_trend_weight = float(c_cfg.get("trend_weight", 0.3))
                        self.conf_ano_weight = float(c_cfg.get("anomaly_weight", 0.3))
            except Exception:
                pass

    def reset(self) -> None:
        """Resets causal state."""
        self.trajectory_tracker.reset()

    def update(
        self,
        window: Union[pd.DataFrame, Dict[str, Any], np.ndarray],
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Processes a single chronological window through all pipeline stages
        and returns the unified Phase 5 DecisionObject.
        """
        # Convert dict or array to single-row DataFrame if needed
        if isinstance(window, dict):
            df = pd.DataFrame([window])
        elif isinstance(window, np.ndarray):
            if window.ndim == 1:
                window = window.reshape(1, -1)
            df = pd.DataFrame(window, columns=self.classifier.expected_features)
        else:
            df = window.copy()

        # Resolve timestamp
        if timestamp:
            curr_ts = str(timestamp)
        elif "window_start" in df.columns:
            curr_ts = str(df["window_start"].values[0])
        elif "timestamp" in df.columns:
            curr_ts = str(df["timestamp"].values[0])
        else:
            curr_ts = pd.Timestamp.now().isoformat()

        # 1. Supervised Classification (XGBoost)
        proba_matrix = self.classifier.predict_proba(df)
        pred_classes = self.classifier.predict(df)
        pred_class = pred_classes[0]
        class_probs = {
            self.classifier.classes[i]: float(round(float(proba_matrix[0, i]), 4))
            for i in range(len(self.classifier.classes))
        }
        cls_confidence = float(round(float(np.max(proba_matrix[0])), 4))

        # 2. Unsupervised Anomaly Scoring (Isolation Forest)
        ano_score = float(round(float(self.anomaly_detector.anomaly_score(df)[0]), 4))
        is_ano = bool(self.anomaly_detector.is_anomalous(df)[0])

        # 3. Risk Fusion
        risk_score, candidate_class, risk_state = self.risk_fusion.calculate(
            class_probabilities=class_probs,
            anomaly_score=ano_score
        )

        # 4. Temporal Trajectory Update
        trajectory = self.trajectory_tracker.update(
            timestamp=curr_ts,
            risk_score=risk_score,
            predicted_class=pred_class,
            classification_confidence=cls_confidence,
            anomaly_score=ano_score,
            is_anomalous=is_ano
        )

        # 5. Emergence & Forecast Evaluation
        recent_history = self.trajectory_tracker.get_recent_history(count=5)
        is_emerging, reasons = self.emergence_detector.evaluate_emergence(
            history=recent_history,
            candidate_class=candidate_class
        )

        # Determine forecasting availability and ETA
        forecast_available = False
        forecast_class = None
        time_to_impact_seconds = None
        forecast_confidence = None
        forecast_reasons = []

        velocity = trajectory["risk_velocity"]
        trend = trajectory["risk_trend"]

        # A forecast is emitted if an attack signature is emerging or rapidly rising
        if is_emerging and velocity > 0.0:
            forecast_available = True
            forecast_class = candidate_class
            forecast_reasons = reasons

            # Trajectory-based ETA estimation:
            # If current risk is already >= target_risk_threshold (e.g. HIGH risk),
            # the attack has arrived at saturation (ETA = 0 seconds)
            if risk_score >= self.target_risk_threshold:
                time_to_impact_seconds = 0
                forecast_reasons.append("Attack has reached critical impact threshold (ETA=0s)")
            else:
                # Minutes remaining = (target_risk - current_risk) / velocity
                minutes_to_target = (self.target_risk_threshold - risk_score) / velocity
                # Clamp to realistic bounds (30s to 15m)
                eta_sec = max(30, int(round(minutes_to_target * 60.0)))
                time_to_impact_seconds = min(900, eta_sec)
                forecast_reasons.append(
                    f"Trajectory extrapolation to critical threshold ({self.target_risk_threshold:.2f}) "
                    f"estimates impact in ~{time_to_impact_seconds}s"
                )

            # Heuristic Forecast Confidence calculation
            # Normalized trend strength: min(1.0, velocity / 0.10)
            norm_trend = float(np.clip(velocity / 0.08, 0.0, 1.0))
            raw_conf = (
                self.conf_cls_weight * cls_confidence
                + self.conf_trend_weight * norm_trend
                + self.conf_ano_weight * ano_score
            )
            forecast_confidence = float(round(float(np.clip(raw_conf, 0.0, 1.0)), 4))

        # 6. Assemble Standardized Extended DecisionObject
        decision_object = {
            "timestamp": curr_ts,
            "predicted_class": pred_class,
            "class_probabilities": class_probs,
            "classification_confidence": cls_confidence,
            "anomaly_score": ano_score,
            "is_anomalous": is_ano,
            "risk_score": risk_score,
            "risk_state": risk_state,
            "risk_velocity": trajectory["risk_velocity"],
            "risk_acceleration": trajectory["risk_acceleration"],
            "risk_trend": trend,
            "forecast_available": forecast_available,
            "forecast_class": forecast_class,
            "time_to_impact_seconds": time_to_impact_seconds,
            "forecast_confidence": forecast_confidence,
            "forecast_reason": forecast_reasons if forecast_available else None,
            "explanation": (
                f"Risk state is {risk_state} ({risk_score:.2f}) with {trend} trajectory."
                + (f" Forecasted {forecast_class} in ~{time_to_impact_seconds}s." if forecast_available else "")
            )
        }

        return decision_object
