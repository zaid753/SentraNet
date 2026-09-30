"""
SENTRANET — Risk Fusion Engine (Phase 5)
Fuses supervised classification probabilities (XGBoost) and unsupervised
behavioral anomaly scores (Isolation Forest) into a calibrated risk score and state.
"""

from typing import Dict, Any, Tuple, Optional
import os
import yaml
import numpy as np

DEFAULT_CONFIG_PATH = "config/risk.yaml"

class RiskFusionEngine:
    """
    Combines supervised attack probability and unsupervised anomaly score
    into a unified behavioral security risk score [0.0, 1.0].
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        classification_weight: Optional[float] = None,
        anomaly_weight: Optional[float] = None,
    ):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.classification_weight = 0.6
        self.anomaly_weight = 0.4

        self.threshold_low = 0.24
        self.threshold_guarded = 0.49
        self.threshold_elevated = 0.74

        self._load_config()

        # Overrides if explicitly provided
        if classification_weight is not None and anomaly_weight is not None:
            self.classification_weight = classification_weight
            self.anomaly_weight = anomaly_weight

        # Validate weights sum to ~1.0
        weight_sum = self.classification_weight + self.anomaly_weight
        if not (0.99 <= weight_sum <= 1.01):
            raise ValueError(f"Risk fusion weights must sum to 1.0 (got {weight_sum})")

    def _load_config(self) -> None:
        """Loads configuration from YAML if available."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "risk" in cfg:
                        fusion_cfg = cfg["risk"].get("fusion", {})
                        self.classification_weight = float(fusion_cfg.get("classification_weight", 0.6))
                        self.anomaly_weight = float(fusion_cfg.get("anomaly_weight", 0.4))

                        thresh_cfg = cfg["risk"].get("thresholds", {})
                        self.threshold_low = float(thresh_cfg.get("low_upper", 0.24))
                        self.threshold_guarded = float(thresh_cfg.get("guarded_upper", 0.49))
                        self.threshold_elevated = float(thresh_cfg.get("elevated_upper", 0.74))
            except Exception as e:
                # Fallback to defaults
                pass

    def calculate(
        self,
        class_probabilities: Dict[str, float],
        anomaly_score: float,
    ) -> Tuple[float, str, str]:
        """
        Calculates fused risk score, candidate attack class, and risk state.

        Formula:
            classification_attack_score = 1.0 - P(BENIGN)
            raw_risk = alpha * classification_attack_score + beta * anomaly_score
            risk_score = clip(raw_risk, 0.0, 1.0)

        Returns:
            Tuple of (risk_score, candidate_attack_class, risk_state)
        """
        p_benign = float(class_probabilities.get("BENIGN", 0.0))
        classification_attack_score = max(0.0, 1.0 - p_benign)

        # Ensure anomaly_score is clamped [0, 1]
        clamped_anomaly = float(np.clip(anomaly_score, 0.0, 1.0))

        # Fused risk
        raw_risk = (
            self.classification_weight * classification_attack_score
            + self.anomaly_weight * clamped_anomaly
        )
        risk_score = float(np.clip(raw_risk, 0.0, 1.0))

        # Identify candidate attack class (highest non-benign probability)
        attack_probs = {k: v for k, v in class_probabilities.items() if k != "BENIGN"}
        if attack_probs and max(attack_probs.values()) > 0.0:
            candidate_attack_class = max(attack_probs.items(), key=lambda item: item[1])[0]
        else:
            candidate_attack_class = "BENIGN"

        risk_state = self.classify_state(risk_score)
        return float(round(risk_score, 4)), candidate_attack_class, risk_state

    def classify_state(self, risk_score: float) -> str:
        """
        Maps numerical risk score to risk state:
            0.00 - 0.24: LOW
            0.25 - 0.49: GUARDED
            0.50 - 0.74: ELEVATED
            0.75 - 1.00: HIGH
        """
        if risk_score <= self.threshold_low:
            return "LOW"
        elif risk_score <= self.threshold_guarded:
            return "GUARDED"
        elif risk_score <= self.threshold_elevated:
            return "ELEVATED"
        else:
            return "HIGH"
