"""
SENTRANET — Decision and Event Serializers (Phase 7)
Converts internal numpy/dataclass models into JSON-safe API response payloads.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from backend.api.schemas.inference import AnalyzeResponse, AlertEventSummary
from backend.api.schemas.alerts import AlertItemResponse, CurrentAlertResponse
from backend.api.schemas.incidents import IncidentItemResponse, IncidentDetailResponse
from backend.api.schemas.timeline import TimelinePointResponse
from backend.replay.replay_event import AlertEvent
from backend.replay.incident_manager import Incident

def serialize_analyze_response(
    decision: Dict[str, Any],
    alert_state: str,
    incident_id: Optional[str] = None,
    emitted_alerts: Optional[List[AlertEvent]] = None,
) -> AnalyzeResponse:
    """Safely converts DecisionObject and Alert status into AnalyzeResponse."""
    p_benign = float(decision["class_probabilities"].get("BENIGN", 0.0))
    attack_likelihood = float(round(max(0.0, 1.0 - p_benign), 4))

    alert_summary = None
    if emitted_alerts and len(emitted_alerts) > 0:
        first_alert = emitted_alerts[0]
        alert_summary = AlertEventSummary(
            event_type=first_alert.event_type,
            incident_id=first_alert.incident_id,
            severity=first_alert.severity,
        )

    return AnalyzeResponse(
        timestamp=str(decision["timestamp"]),
        attack_class=str(decision["predicted_class"]),
        class_probability=float(round(float(decision["classification_confidence"]), 4)),
        attack_likelihood=attack_likelihood,
        anomaly_score=float(round(float(decision["anomaly_score"]), 4)),
        is_anomalous=bool(decision["is_anomalous"]),
        risk_score=float(round(float(decision["risk_score"]), 4)),
        risk_state=str(decision["risk_state"]),
        risk_velocity=float(round(float(decision["risk_velocity"]), 4)) if decision.get("risk_velocity") is not None else None,
        risk_acceleration=float(round(float(decision["risk_acceleration"]), 4)) if decision.get("risk_acceleration") is not None else None,
        risk_trend=str(decision.get("risk_trend", "STABLE")),
        emergence_detected=bool(decision.get("forecast_available", False)),
        forecast_active=bool(decision.get("forecast_available", False)),
        forecast_class=str(decision["forecast_class"]) if decision.get("forecast_class") else None,
        estimated_eta_seconds=int(decision["time_to_impact_seconds"]) if decision.get("time_to_impact_seconds") is not None else None,
        forecast_confidence=float(round(float(decision["forecast_confidence"]), 4)) if decision.get("forecast_confidence") is not None else None,
        alert_state=alert_state,
        incident_id=incident_id,
        reasons=decision.get("forecast_reason") or [],
        alert_event=alert_summary,
        simulation=True,
    )

def serialize_alert_event(event: AlertEvent) -> AlertItemResponse:
    return AlertItemResponse(
        alert_event_id=event.alert_event_id,
        incident_id=event.incident_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        attack_class=event.attack_class,
        severity=event.severity,
        risk_score=float(round(event.risk_score, 4)),
        anomaly_score=float(round(event.anomaly_score, 4)),
        reasons=event.reasons,
        forecast_active=event.forecast_active,
        estimated_eta_seconds=event.estimated_eta_seconds,
        forecast_confidence=float(round(event.forecast_confidence, 4)) if event.forecast_confidence is not None else None,
    )

def serialize_incident_summary(inc: Incident) -> IncidentItemResponse:
    return IncidentItemResponse(
        incident_id=inc.incident_id,
        status=inc.status,
        attack_class=inc.attack_class,
        severity=inc.severity,
        created_at=inc.created_at,
        updated_at=inc.updated_at,
        resolved_at=inc.resolution_timestamp,
        peak_risk=float(round(inc.peak_risk_score, 4)),
        max_anomaly=float(round(inc.max_anomaly_score, 4)),
        forecast_triggered=inc.forecast_triggered,
        event_count=inc.event_count,
    )

def serialize_incident_detail(inc: Incident) -> IncidentDetailResponse:
    return IncidentDetailResponse(
        incident_id=inc.incident_id,
        status=inc.status,
        attack_class=inc.attack_class,
        severity=inc.severity,
        created_at=inc.created_at,
        updated_at=inc.updated_at,
        resolution_timestamp=inc.resolution_timestamp,
        first_risk_score=float(round(inc.first_risk_score, 4)),
        current_risk_score=float(round(inc.current_risk_score, 4)),
        peak_risk_score=float(round(inc.peak_risk_score, 4)),
        max_anomaly_score=float(round(inc.max_anomaly_score, 4)),
        forecast_triggered=inc.forecast_triggered,
        estimated_eta_seconds=inc.estimated_eta_seconds,
        confidence=float(round(inc.confidence, 4)),
        event_count=inc.event_count,
        timestamps=inc.timestamps,
    )
