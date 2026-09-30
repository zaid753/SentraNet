"""
SENTRANET — Temporal Risk Trajectory Engine (Phase 5)
Maintains causal history of risk scores, computes first and second temporal derivatives
(risk velocity and acceleration), and classifies trajectory trends.
"""

from typing import Dict, Any, List, Optional
import os
import yaml
import datetime
import pandas as pd

DEFAULT_CONFIG_PATH = "config/risk.yaml"

class RiskTrajectoryTracker:
    """
    Maintains a strictly causal rolling buffer of risk evaluations.
    Computes risk_delta, risk_velocity (per min), risk_acceleration (per min^2),
    and classifies trend into STABLE, RISING, RAPIDLY_RISING, FALLING.
    """

    def __init__(self, config_path: Optional[str] = None, max_history: int = 20):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.max_history = max_history

        # Default trend thresholds
        self.rising_velocity = 0.02
        self.rapid_velocity = 0.05
        self.rapid_acceleration = 0.01

        self._load_config()
        self.history: List[Dict[str, Any]] = []

    def _load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "risk" in cfg and "trend" in cfg["risk"]:
                        t_cfg = cfg["risk"]["trend"]
                        self.rising_velocity = float(t_cfg.get("rising_velocity", 0.02))
                        self.rapid_velocity = float(t_cfg.get("rapid_velocity", 0.05))
                        self.rapid_acceleration = float(t_cfg.get("rapid_acceleration", 0.01))
            except Exception:
                pass

    def reset(self) -> None:
        """Clears trajectory buffer."""
        self.history = []

    def _parse_timestamp(self, ts: Any) -> datetime.datetime:
        if isinstance(ts, datetime.datetime):
            return ts
        if isinstance(ts, (pd.Timestamp, np_datetime)):
            return ts.to_pydatetime()
        # Parse ISO string
        return pd.to_datetime(ts).to_pydatetime()

    def update(
        self,
        timestamp: Any,
        risk_score: float,
        predicted_class: str,
        classification_confidence: float,
        anomaly_score: float,
        is_anomalous: bool,
    ) -> Dict[str, Any]:
        """
        Appends current window observation and calculates causal derivatives.

        Returns:
            Dict containing current trajectory telemetry:
            {
                "timestamp": str,
                "risk_score": float,
                "risk_delta": float,
                "risk_velocity": float,
                "risk_acceleration": float,
                "risk_trend": str,
                ...
            }
        """
        curr_dt = pd.to_datetime(timestamp)

        # Derivatives
        if len(self.history) == 0:
            delta = 0.0
            velocity = 0.0
            acceleration = 0.0
        else:
            prev = self.history[-1]
            prev_dt = pd.to_datetime(prev["timestamp"])
            time_diff_min = max(0.01, (curr_dt - prev_dt).total_seconds() / 60.0)

            delta = risk_score - prev["risk_score"]
            velocity = delta / time_diff_min

            prev_velocity = prev.get("risk_velocity", 0.0)
            acceleration = (velocity - prev_velocity) / time_diff_min

        # Trend classification
        trend = self._classify_trend(velocity, acceleration)

        record = {
            "timestamp": curr_dt.isoformat(),
            "risk_score": float(round(risk_score, 4)),
            "risk_delta": float(round(delta, 4)),
            "risk_velocity": float(round(velocity, 4)),
            "risk_acceleration": float(round(acceleration, 4)),
            "risk_trend": trend,
            "predicted_class": predicted_class,
            "classification_confidence": float(round(classification_confidence, 4)),
            "anomaly_score": float(round(anomaly_score, 4)),
            "is_anomalous": is_anomalous,
        }

        self.history.append(record)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return record

    def _classify_trend(self, velocity: float, acceleration: float) -> str:
        if velocity >= self.rapid_velocity and acceleration >= self.rapid_acceleration:
            return "RAPIDLY_RISING"
        elif velocity >= self.rising_velocity:
            return "RISING"
        elif velocity <= -self.rising_velocity:
            return "FALLING"
        else:
            return "STABLE"

    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """Returns the most recent N causal history records."""
        return self.history[-count:]
