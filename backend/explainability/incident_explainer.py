"""
SENTRANET — Incident Explainer (Phase 11)
Enhances raw Incident objects with narrative summaries and duration metrics.
"""

import datetime
import pandas as pd
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class IncidentTimelineEvent(BaseModel):
    timestamp: str
    event_type: str
    risk: float
    anomaly: float
    attack_class: str
    explanation: str


class IncidentExplanation(BaseModel):
    incident_id: str
    start_time: str
    end_time: str
    duration: str = Field(..., description="Duration string e.g. 4m 12s")
    highest_risk: float
    highest_anomaly: float
    attack_classes_observed: List[str]
    alert_count: int
    forecast_signals: int
    risk_trajectory_summary: str
    explanation_summary: str
    timeline: List[IncidentTimelineEvent]


def build_incident_explanation(
    incident: Any,
    alert_events: List[Any],
) -> IncidentExplanation:
    """
    Builds a deterministic IncidentExplanation from an Incident object and its associated alerts.
    """
    start_time = incident.created_at
    end_time = incident.resolution_timestamp or incident.updated_at

    try:
        dt_start = pd.to_datetime(start_time)
        dt_end = pd.to_datetime(end_time)
        seconds = int((dt_end - dt_start).total_seconds())
        minutes = seconds // 60
        secs = seconds % 60
        duration = f"{minutes}m {secs}s" if minutes > 0 else f"{secs}s"
    except Exception:
        duration = "Unknown"

    # Filter alerts to this incident
    incident_alerts = [a for a in alert_events if a.incident_id == incident.incident_id]
    forecast_signals = sum(1 for a in incident_alerts if a.event_type == "FORECAST_TRIGGERED")

    # Timeline construction
    timeline = []
    for a in incident_alerts:
        # Generate short explanation for the timeline event based on state transition or forecast
        if a.event_type == "FORECAST_TRIGGERED":
            expl = f"Forecast triggered for {a.attack_class}."
        elif a.event_type == "WATCH_STARTED":
            expl = f"Risk elevated into WATCH state ({a.risk_score:.2f})."
        elif a.event_type == "ALERT_CREATED":
            expl = f"Risk crossed HIGH threshold ({a.risk_score:.2f})."
        elif a.event_type == "ALERT_RESOLVED":
            expl = f"Incident resolved as risk fell."
        else:
            expl = f"{a.event_type.replace('_', ' ').capitalize()}."

        timeline.append(IncidentTimelineEvent(
            timestamp=str(a.timestamp),
            event_type=a.event_type,
            risk=round(a.risk_score, 4),
            anomaly=round(a.anomaly_score, 4),
            attack_class=a.attack_class,
            explanation=expl,
        ))

    # Sort timeline
    timeline.sort(key=lambda x: x.timestamp)

    # Narrative summary
    classes_str = ", ".join([incident.attack_class])
    risk_trajectory_summary = f"Peak risk: {incident.peak_risk_score:.2f}. "
    if incident.status == "RESOLVED":
        risk_trajectory_summary += "Trajectory resolved."
    else:
        risk_trajectory_summary += "Currently ACTIVE."

    explanation_summary = (
        f"Incident {incident.incident_id} detected {classes_str} activity. "
        f"Reached peak risk of {incident.peak_risk_score:.2f} and peak anomaly of {incident.max_anomaly_score:.2f}. "
        f"Forecast was {'active' if incident.forecast_triggered else 'not active'}."
    )

    return IncidentExplanation(
        incident_id=incident.incident_id,
        start_time=str(start_time),
        end_time=str(end_time),
        duration=duration,
        highest_risk=round(incident.peak_risk_score, 4),
        highest_anomaly=round(incident.max_anomaly_score, 4),
        attack_classes_observed=[incident.attack_class],
        alert_count=len(incident_alerts),
        forecast_signals=forecast_signals,
        risk_trajectory_summary=risk_trajectory_summary,
        explanation_summary=explanation_summary,
        timeline=timeline,
    )
