"""
SENTRANET — Attack Emergence Detector (Phase 5)
Detects pre-attack emergence signals requiring multi-window evidence:
risk growth, elevated anomaly scores, and persistence of the candidate attack class.
"""

from typing import Dict, Any, List, Tuple, Optional
import os
import yaml

DEFAULT_CONFIG_PATH = "config/risk.yaml"

class AttackEmergenceDetector:
    """
    Evaluates causal multi-window history to determine if an attack pattern
    is emerging rather than reacting to a single noisy spike.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        emergence_threshold: Optional[float] = None,
        minimum_persistence_windows: Optional[int] = None,
    ):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.emergence_threshold = 0.50
        self.minimum_persistence_windows = 2
        self._load_config()

        if emergence_threshold is not None:
            self.emergence_threshold = emergence_threshold
        if minimum_persistence_windows is not None:
            self.minimum_persistence_windows = minimum_persistence_windows

    def _load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "forecast" in cfg:
                        f_cfg = cfg["forecast"]
                        self.emergence_threshold = float(f_cfg.get("emergence_threshold", 0.50))
                        self.minimum_persistence_windows = int(f_cfg.get("minimum_persistence_windows", 2))
            except Exception:
                pass

    def evaluate_emergence(
        self,
        history: List[Dict[str, Any]],
        candidate_class: str,
    ) -> Tuple[bool, List[str]]:
        """
        Evaluates recent history for emerging attack signatures.

        Conditions for emergence:
        1. Minimum history satisfied (>= minimum_persistence_windows + 1).
        2. Current risk >= emergence_threshold (or trending upward into elevated state).
        3. Risk is rising: current risk > previous risk.
        4. Candidate attack class is not BENIGN and has persisted across at least
           minimum_persistence_windows consecutive windows.
        5. Behavioral anomaly score is elevated (>= 0.40) or increasing.

        Returns:
            Tuple of (is_emerging: bool, reasons: List[str])
        """
        required_len = self.minimum_persistence_windows + 1
        if len(history) < required_len:
            return False, ["Insufficient temporal history for emergence evaluation"]

        curr = history[-1]
        prev = history[-2]

        if candidate_class == "BENIGN":
            return False, ["Candidate class is BENIGN; no attack emerging"]

        reasons = []

        # 1. Risk Level and Trend Check
        risk_elevated = curr["risk_score"] >= self.emergence_threshold
        risk_rising = curr["risk_velocity"] > 0.0 or curr["risk_score"] > prev["risk_score"]

        if risk_elevated:
            reasons.append(f"Fused risk ({curr['risk_score']:.2f}) meets emergence threshold ({self.emergence_threshold:.2f})")
        if risk_rising:
            reasons.append(f"Risk velocity is positive (+{curr['risk_velocity']:.4f}/min)")

        # 2. Persistence Check
        recent_windows = history[-self.minimum_persistence_windows:]
        classes = [w.get("predicted_class") for w in recent_windows]
        persistent = all(c == candidate_class for c in classes)
        if persistent:
            reasons.append(f"Candidate attack class '{candidate_class}' persisted across {self.minimum_persistence_windows} consecutive windows")
        else:
            return False, [f"Class instability: recent sequence {classes} does not meet persistence requirement"]

        # 3. Anomaly Score Elevation Check
        ano_elevated = curr.get("anomaly_score", 0.0) >= 0.40 or curr.get("is_anomalous", False)
        if ano_elevated:
            reasons.append(f"Behavioral anomaly score ({curr.get('anomaly_score', 0.0):.2f}) indicates abnormal deviation")

        is_emerging = risk_rising and persistent and (risk_elevated or ano_elevated)
        return is_emerging, reasons
