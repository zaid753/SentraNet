"""
SENTRANET — Replay & Alert Event Schemas (Phase 6)
Defines structured telemetry representations for replayed temporal windows and alert transitions.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class ReplayEvent:
    """
    Presentation/transport event wrapping the Phase 5 DecisionObject during stream replay.
    """
    event_id: str
    timestamp: str
    window_id: str
    attack_class: str
    class_probability: float
    attack_likelihood: float
    anomaly_score: float
    is_anomalous: bool
    risk_score: float
    risk_state: str
    risk_velocity: float
    risk_acceleration: float
    risk_trend: str
    emergence_detected: bool
    forecast_active: bool
    forecast_class: Optional[str]
    estimated_eta_seconds: Optional[int]
    forecast_confidence: Optional[float]
    reasons: List[str] = field(default_factory=list)
    alert_state: str = "NORMAL"
    severity: str = "INFO"
    replay_mode: str = "batch"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AlertEvent:
    """
    State transition event emitted by the Alert State Machine & Incident Manager.
    Event Types:
      - ALERT_CREATED
      - ALERT_UPDATED
      - ALERT_ESCALATED
      - ALERT_RESOLVED
      - WATCH_STARTED
      - WATCH_UPDATED
      - FORECAST_TRIGGERED
    """
    alert_event_id: str
    incident_id: Optional[str]
    event_type: str
    timestamp: str
    attack_class: str
    severity: str
    risk_score: float
    anomaly_score: float
    reasons: List[str] = field(default_factory=list)
    forecast_active: bool = False
    estimated_eta_seconds: Optional[int] = None
    forecast_confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
