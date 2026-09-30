"""
SENTRANET — Incident Manager Module (Phase 6)
Deterministic, in-memory alert deduplication, incident lifecycle correlation,
cooldown suppression, and resolution tracking.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import datetime
import pandas as pd

from backend.replay.replay_event import AlertEvent

@dataclass
class Incident:
    incident_id: str
    created_at: str
    updated_at: str
    status: str                         # ACTIVE, RESOLVED
    attack_class: str
    severity: str                       # HIGH, MEDIUM, etc.
    first_risk_score: float
    current_risk_score: float
    peak_risk_score: float
    max_anomaly_score: float
    forecast_triggered: bool
    estimated_eta_seconds: Optional[int]
    confidence: float
    event_count: int = 1
    timestamps: List[str] = field(default_factory=list)
    resolution_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class IncidentManager:
    """
    Correlates continuous security alerts into distinct, deterministic incidents.
    Suppresses minute-by-minute alert spam, enforces cooldowns, and tracks resolution.
    """

    def __init__(
        self,
        resolution_consecutive_windows: int = 2,
        cooldown_seconds: float = 120.0,
    ):
        self.resolution_consecutive_windows = resolution_consecutive_windows
        self.cooldown_seconds = cooldown_seconds

        self.active_incident: Optional[Incident] = None
        self.incidents: List[Incident] = []
        self.incident_counter: int = 0
        self.alert_event_counter: int = 0

        self.consecutive_non_alert_windows: int = 0
        self.last_resolved_time: Optional[datetime.datetime] = None
        self.last_resolved_class: Optional[str] = None

    def reset(self) -> None:
        self.active_incident = None
        self.incidents = []
        self.incident_counter = 0
        self.alert_event_counter = 0
        self.consecutive_non_alert_windows = 0
        self.last_resolved_time = None
        self.last_resolved_class = None

    def _next_alert_event_id(self) -> str:
        self.alert_event_counter += 1
        return f"ALT-{self.alert_event_counter:04d}"

    def _generate_incident_id(self, timestamp: str, attack_class: str) -> str:
        self.incident_counter += 1
        dt = pd.to_datetime(timestamp)
        date_str = dt.strftime("%Y%m%d")
        time_str = dt.strftime("%H%M%S")
        prefix = attack_class[:4].upper()
        return f"INC-{date_str}-{time_str}-{prefix}-{self.incident_counter:03d}"

    def process_window(
        self,
        timestamp: str,
        alert_state: str,
        attack_class: str,
        severity: str,
        risk_score: float,
        anomaly_score: float,
        reasons: List[str],
        forecast_active: bool,
        estimated_eta_seconds: Optional[int],
        confidence: float,
    ) -> List[AlertEvent]:
        """
        Evaluates current window security state and returns list of emitted AlertEvents.
        """
        curr_dt = pd.to_datetime(timestamp).to_pydatetime()
        emitted_events: List[AlertEvent] = []

        if alert_state == "ALERT":
            self.consecutive_non_alert_windows = 0

            # Case A: An incident is already active
            if self.active_incident is not None:
                # Same attack class: deduplicate & update active incident
                if self.active_incident.attack_class == attack_class:
                    inc = self.active_incident
                    inc.updated_at = timestamp
                    inc.event_count += 1
                    inc.timestamps.append(timestamp)
                    inc.current_risk_score = risk_score
                    inc.peak_risk_score = max(inc.peak_risk_score, risk_score)
                    inc.max_anomaly_score = max(inc.max_anomaly_score, anomaly_score)
                    if forecast_active:
                        inc.forecast_triggered = True
                        inc.estimated_eta_seconds = estimated_eta_seconds
                    inc.confidence = confidence

                    # Determine if escalated (significant risk increase)
                    event_type = "ALERT_UPDATED"
                    if risk_score > inc.first_risk_score + 0.15:
                        event_type = "ALERT_ESCALATED"

                    emitted_events.append(AlertEvent(
                        alert_event_id=self._next_alert_event_id(),
                        incident_id=inc.incident_id,
                        event_type=event_type,
                        timestamp=timestamp,
                        attack_class=attack_class,
                        severity=severity,
                        risk_score=risk_score,
                        anomaly_score=anomaly_score,
                        reasons=reasons,
                        forecast_active=forecast_active,
                        estimated_eta_seconds=estimated_eta_seconds,
                        forecast_confidence=confidence,
                    ))
                else:
                    # Different attack class: Resolve previous incident and open new one
                    res_event = self._resolve_active_incident(timestamp)
                    if res_event:
                        emitted_events.append(res_event)
                    new_event = self._create_new_incident(
                        timestamp, attack_class, severity, risk_score,
                        anomaly_score, reasons, forecast_active,
                        estimated_eta_seconds, confidence
                    )
                    emitted_events.append(new_event)

            # Case B: No active incident -> Create new incident (checking cooldown)
            else:
                in_cooldown = False
                if self.last_resolved_time is not None and self.last_resolved_class == attack_class:
                    elapsed = (curr_dt - self.last_resolved_time).total_seconds()
                    if elapsed < self.cooldown_seconds:
                        in_cooldown = True

                if in_cooldown:
                    # Suppress new incident during cooldown window; emit update on last incident if applicable
                    pass
                else:
                    new_event = self._create_new_incident(
                        timestamp, attack_class, severity, risk_score,
                        anomaly_score, reasons, forecast_active,
                        estimated_eta_seconds, confidence
                    )
                    emitted_events.append(new_event)

        else:
            # Non-ALERT state (WATCH, NORMAL, RESOLVED)
            if self.active_incident is not None:
                self.consecutive_non_alert_windows += 1
                if self.consecutive_non_alert_windows >= self.resolution_consecutive_windows:
                    res_event = self._resolve_active_incident(timestamp)
                    if res_event:
                        emitted_events.append(res_event)

        return emitted_events

    def _create_new_incident(
        self,
        timestamp: str,
        attack_class: str,
        severity: str,
        risk_score: float,
        anomaly_score: float,
        reasons: List[str],
        forecast_active: bool,
        estimated_eta_seconds: Optional[int],
        confidence: float,
    ) -> AlertEvent:
        inc_id = self._generate_incident_id(timestamp, attack_class)
        inc = Incident(
            incident_id=inc_id,
            created_at=timestamp,
            updated_at=timestamp,
            status="ACTIVE",
            attack_class=attack_class,
            severity=severity,
            first_risk_score=risk_score,
            current_risk_score=risk_score,
            peak_risk_score=risk_score,
            max_anomaly_score=anomaly_score,
            forecast_triggered=forecast_active,
            estimated_eta_seconds=estimated_eta_seconds,
            confidence=confidence,
            event_count=1,
            timestamps=[timestamp],
        )
        self.active_incident = inc
        self.incidents.append(inc)

        return AlertEvent(
            alert_event_id=self._next_alert_event_id(),
            incident_id=inc_id,
            event_type="ALERT_CREATED",
            timestamp=timestamp,
            attack_class=attack_class,
            severity=severity,
            risk_score=risk_score,
            anomaly_score=anomaly_score,
            reasons=reasons,
            forecast_active=forecast_active,
            estimated_eta_seconds=estimated_eta_seconds,
            forecast_confidence=confidence,
        )

    def _resolve_active_incident(self, timestamp: str) -> Optional[AlertEvent]:
        if self.active_incident is None:
            return None

        inc = self.active_incident
        inc.status = "RESOLVED"
        inc.resolution_timestamp = timestamp
        self.last_resolved_time = pd.to_datetime(timestamp).to_pydatetime()
        self.last_resolved_class = inc.attack_class
        self.active_incident = None

        return AlertEvent(
            alert_event_id=self._next_alert_event_id(),
            incident_id=inc.incident_id,
            event_type="ALERT_RESOLVED",
            timestamp=timestamp,
            attack_class=inc.attack_class,
            severity="INFO",
            risk_score=inc.current_risk_score,
            anomaly_score=inc.max_anomaly_score,
            reasons=[f"Incident resolved after {self.resolution_consecutive_windows} consecutive recovery windows"],
            forecast_active=False,
            estimated_eta_seconds=None,
            forecast_confidence=inc.confidence,
        )

    def force_resolve_all(self, final_timestamp: str) -> List[AlertEvent]:
        """Resolves any remaining active incident at the end of stream replay."""
        events = []
        if self.active_incident is not None:
            ev = self._resolve_active_incident(final_timestamp)
            if ev:
                events.append(ev)
        return events
