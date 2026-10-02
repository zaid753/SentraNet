import logging
from backend.api.events.bus import event_bus
from backend.api.events.models import EventEnvelope, EventTypes
from backend.api.database import SessionLocal
from backend.api.models import Incident, Alert
import asyncio

logger = logging.getLogger(__name__)

# Basic persistence for Phase 6
# Listens to domain events and persists them to SQLite



def handle_incident_created(event: EventEnvelope):
    payload = event.payload
    incident_id = payload.get("incident_id")
    if not incident_id:
        return

    with SessionLocal() as db:
        # Check if exists
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            inc = Incident(
                id=incident_id,
                status=payload.get("status", "ACTIVE"),
                attack_class=payload.get("attack_class", "UNKNOWN"),
                severity=payload.get("severity", "LOW"),
                first_risk_score=payload.get("first_risk", 0.0),
                current_risk_score=payload.get("current_risk", 0.0),
                peak_risk_score=payload.get("peak_risk", 0.0),
                max_anomaly_score=payload.get("max_anomaly", 0.0)
            )
            db.add(inc)
            db.commit()

def handle_incident_updated(event: EventEnvelope):
    payload = event.payload
    incident_id = payload.get("incident_id")
    if not incident_id:
        return

    with SessionLocal() as db:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if inc:
            if "status" in payload: inc.status = payload["status"]
            if "current_risk" in payload: inc.current_risk_score = payload["current_risk"]
            if "peak_risk" in payload: inc.peak_risk_score = max(inc.peak_risk_score, payload["peak_risk"])
            if "max_anomaly" in payload: inc.max_anomaly_score = max(inc.max_anomaly_score, payload["max_anomaly"])
            if "forecast_triggered" in payload: inc.forecast_triggered = payload["forecast_triggered"]
            if "estimated_eta_seconds" in payload: inc.estimated_eta_seconds = payload["estimated_eta_seconds"]
            
            db.commit()

def handle_incident_resolved(event: EventEnvelope):
    payload = event.payload
    incident_id = payload.get("incident_id")
    if not incident_id:
        return

    with SessionLocal() as db:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if inc:
            inc.status = "RESOLVED"
            # resolved_at is not currently in payload, just update status for Phase 6.
            db.commit()

def handle_alert_created(event: EventEnvelope):
    payload = event.payload
    alert_id = payload.get("alert_id")
    incident_id = payload.get("incident_id")
    if not alert_id or not incident_id:
        return
        
    with SessionLocal() as db:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            alert = Alert(
                id=alert_id,
                incident_id=incident_id,
                alert_type=payload.get("alert_type", "ANOMALY"),
                status=payload.get("status", "NEW"),
                risk_score=payload.get("risk_score"),
                anomaly_score=payload.get("anomaly_score")
            )
            db.add(alert)
            db.commit()

def setup_persistence_subscriptions():
    event_bus.subscribe(EventTypes.INCIDENT_CREATED, handle_incident_created)
    event_bus.subscribe(EventTypes.INCIDENT_UPDATED, handle_incident_updated)
    event_bus.subscribe(EventTypes.INCIDENT_RESOLVED, handle_incident_resolved)
    event_bus.subscribe(EventTypes.ALERT_CREATED, handle_alert_created)
    logger.info("Persistence subscribers attached to EventBus.")
