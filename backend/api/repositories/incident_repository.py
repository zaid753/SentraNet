from sqlalchemy.orm import Session
from typing import List, Optional
from backend.api.models import Incident, Alert
from backend.replay.incident_manager import Incident as DomainIncident
from backend.replay.replay_event import AlertEvent

class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_incidents_all(self) -> List[Incident]:
        return self.db.query(Incident).order_by(Incident.created_at.desc()).all()

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self.db.query(Incident).filter(Incident.id == incident_id).first()

    def get_incident_alerts(self, incident_id: str) -> List[Alert]:
        return self.db.query(Alert).filter(Alert.incident_id == incident_id).order_by(Alert.created_at.asc()).all()

    def to_domain_incident(self, inc: Incident, alerts: List[Alert]) -> DomainIncident:
        # Reconstruct the DomainIncident from the DB row for explanation builder
        domain_inc = DomainIncident(
            incident_id=inc.id,
            threat_class=inc.attack_class,
            first_risk=inc.first_risk_score,
            creation_time=inc.created_at
        )
        domain_inc.status = inc.status
        domain_inc.severity = inc.severity
        domain_inc.current_risk = inc.current_risk_score
        domain_inc.peak_risk = inc.peak_risk_score
        domain_inc.max_anomaly = inc.max_anomaly_score
        domain_inc.forecast_triggered = inc.forecast_triggered
        domain_inc.estimated_eta_seconds = inc.estimated_eta_seconds
        
        # Add alerts back
        for a in alerts:
            alert_event = AlertEvent(
                alert_id=a.id,
                timestamp=a.created_at.isoformat(),
                incident_id=a.incident_id,
                alert_type=a.alert_type,
                status=a.status,
                risk_score=a.risk_score,
                anomaly_score=a.anomaly_score,
                metrics={}  # We didn't persist metrics, but explanation builder mostly needs scores
            )
            domain_inc.alerts.append(alert_event)
            
        return domain_inc
