"""
SENTRANET — Alert State Machine (Phase 6)
Deterministic state transitions across NORMAL, WATCH, ALERT, and RESOLVED.
Maps risk states, emits WATCH/FORECAST events, and coordinates with IncidentManager.
"""

from typing import Dict, Any, List, Optional, Tuple
from backend.replay.replay_event import AlertEvent
from backend.replay.incident_manager import IncidentManager

class AlertStateMachine:
    """
    State machine managing transition logic:
      NORMAL  <-->  WATCH  <-->  ALERT
        ^                          |
        +------- RESOLVED <--------+
    """

    def __init__(self, incident_manager: Optional[IncidentManager] = None):
        self.incident_manager = incident_manager or IncidentManager()
        self.current_state: str = "NORMAL"
        self.previous_state: str = "NORMAL"
        self.watch_event_counter: int = 0
        self.last_forecast_state: bool = False

    def reset(self) -> None:
        self.current_state = "NORMAL"
        self.previous_state = "NORMAL"
        self.watch_event_counter = 0
        self.last_forecast_state = False
        self.incident_manager.reset()

    def process_decision(self, decision: Dict[str, Any]) -> Tuple[str, str, List[AlertEvent]]:
        """
        Consumes Phase 5 DecisionObject and advances state machine.

        Returns:
            Tuple of:
              - alert_state (NORMAL, WATCH, ALERT, RESOLVED)
              - severity (INFO, MEDIUM, HIGH)
              - list of newly emitted AlertEvents
        """
        timestamp = decision["timestamp"]
        risk_score = decision["risk_score"]
        risk_state = decision["risk_state"]
        anomaly_score = decision["anomaly_score"]
        predicted_class = decision["predicted_class"]
        confidence = decision["classification_confidence"]
        forecast_active = decision.get("forecast_available", False)
        forecast_class = decision.get("forecast_class")
        eta_sec = decision.get("time_to_impact_seconds")
        reasons = decision.get("forecast_reason") or []

        # Map Risk State to Alert State and Severity
        # LOW (0.00-0.24) -> NORMAL (INFO)
        # GUARDED (0.25-0.49) / ELEVATED (0.50-0.74) -> WATCH (MEDIUM)
        # HIGH (0.75-1.00) -> ALERT (HIGH)
        if risk_state == "HIGH":
            target_state = "ALERT"
            severity = "HIGH"
        elif risk_state in {"GUARDED", "ELEVATED"}:
            target_state = "WATCH"
            severity = "MEDIUM"
        else:
            target_state = "NORMAL"
            severity = "INFO"

        self.previous_state = self.current_state
        self.current_state = target_state

        emitted_events: List[AlertEvent] = []

        # 1. Check FORECAST_TRIGGERED event
        # Emitted when forecast turns active, or when active forecast class changes
        if forecast_active and not self.last_forecast_state:
            emitted_events.append(AlertEvent(
                alert_event_id=self.incident_manager._next_alert_event_id(),
                incident_id=self.incident_manager.active_incident.incident_id if self.incident_manager.active_incident else None,
                event_type="FORECAST_TRIGGERED",
                timestamp=timestamp,
                attack_class=forecast_class or predicted_class,
                severity=severity,
                risk_score=risk_score,
                anomaly_score=anomaly_score,
                reasons=[f"Forecast signal triggered for {forecast_class or predicted_class} in ~{eta_sec}s"],
                forecast_active=True,
                estimated_eta_seconds=eta_sec,
                forecast_confidence=decision.get("forecast_confidence"),
            ))
        self.last_forecast_state = forecast_active

        # 2. WATCH Events
        if self.current_state == "WATCH":
            event_type = "WATCH_STARTED" if self.previous_state != "WATCH" else "WATCH_UPDATED"
            watch_reasons = reasons if reasons else [f"Risk elevated into {risk_state} state ({risk_score:.2f})"]
            self.watch_event_counter += 1
            emitted_events.append(AlertEvent(
                alert_event_id=self.incident_manager._next_alert_event_id(),
                incident_id=None,
                event_type=event_type,
                timestamp=timestamp,
                attack_class=predicted_class,
                severity="MEDIUM",
                risk_score=risk_score,
                anomaly_score=anomaly_score,
                reasons=watch_reasons,
                forecast_active=forecast_active,
                estimated_eta_seconds=eta_sec,
                forecast_confidence=decision.get("forecast_confidence"),
            ))

        # 3. ALERT / Incident Processing
        # (IncidentManager handles ALERT_CREATED, ALERT_UPDATED, ALERT_ESCALATED, ALERT_RESOLVED)
        incident_events = self.incident_manager.process_window(
            timestamp=timestamp,
            alert_state=self.current_state,
            attack_class=predicted_class,
            severity=severity,
            risk_score=risk_score,
            anomaly_score=anomaly_score,
            reasons=reasons if reasons else [f"Security risk reached critical HIGH state ({risk_score:.2f})"],
            forecast_active=forecast_active,
            estimated_eta_seconds=eta_sec,
            confidence=confidence,
        )
        emitted_events.extend(incident_events)

        return self.current_state, severity, emitted_events
