"""
SENTRANET — Incidents Routes (Phase 6 Auth-Aware)
"""

from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas.incidents import IncidentItemResponse, IncidentDetailResponse
from backend.explainability.incident_explainer import IncidentExplanation, build_incident_explanation
from backend.api.services.sentranet_service import SentranetService
from backend.api.dependencies import get_sentranet_service
from backend.api.database import get_db
from backend.api.database import get_db
from backend.api.repositories.incident_repository import IncidentRepository
from datetime import datetime, timezone
from datetime import datetime, timezone

router = APIRouter(tags=["Incidents"])

@router.get(
    "/incidents",
    response_model=List[IncidentItemResponse],
    summary="Get incident history",
    description="Returns summaries of all security incidents for the authenticated workspace."
)
def get_incidents(
    db: Session = Depends(get_db)
) -> List[IncidentItemResponse]:
    repo = IncidentRepository(db)
    db_incidents = repo.get_incidents_all()
    
    return [
        IncidentItemResponse(
            incident_id=inc.id,
            status=inc.status,
            attack_class=inc.attack_class,
            severity=inc.severity,
            created_at=inc.created_at.isoformat(),
            updated_at=inc.updated_at.isoformat(),
            resolved_at=inc.resolved_at.isoformat() if inc.resolved_at else None,
            peak_risk=inc.peak_risk_score,
            max_anomaly=inc.max_anomaly_score,
            forecast_triggered=inc.forecast_triggered,
            event_count=len(inc.alerts)
        )
        for inc in db_incidents
    ]

@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentDetailResponse,
    summary="Get single incident details",
    description="Returns comprehensive timeline, metrics, and event log for a specific incident."
)
def get_incident(
    incident_id: str = Path(..., description="Unique incident identifier"),
    db: Session = Depends(get_db)
) -> IncidentDetailResponse:
    repo = IncidentRepository(db)
    inc = repo.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")
        
    return IncidentDetailResponse(
        incident_id=inc.id,
        status=inc.status,
        attack_class=inc.attack_class,
        severity=inc.severity,
        created_at=inc.created_at.isoformat(),
        updated_at=inc.updated_at.isoformat(),
        resolution_timestamp=inc.resolved_at.isoformat() if inc.resolved_at else None,
        first_risk_score=inc.first_risk_score,
        current_risk_score=inc.current_risk_score,
        peak_risk_score=inc.peak_risk_score,
        max_anomaly_score=inc.max_anomaly_score,
        forecast_triggered=inc.forecast_triggered,
        estimated_eta_seconds=inc.estimated_eta_seconds
    )

@router.get(
    "/incidents/{incident_id}/explanation",
    response_model=IncidentExplanation,
    summary="Get incident-level explanation",
    description="Returns an explanation and timeline for a specific incident."
)
def get_incident_explanation(
    incident_id: str = Path(..., description="Unique incident identifier"),
    db: Session = Depends(get_db)
) -> IncidentExplanation:
    repo = IncidentRepository(db)
    inc = repo.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")
        
    alerts = repo.get_incident_alerts(incident_id)
    domain_inc = repo.to_domain_incident(inc, alerts)
    
    return build_incident_explanation(domain_inc, domain_inc.alerts)

@router.post(
    "/incidents/{incident_id}/resolve",
    response_model=IncidentDetailResponse,
    summary="Resolve an incident",
    description="Marks the incident as RESOLVED. Requires ANALYST or OWNER role."
)
def resolve_incident(
    incident_id: str = Path(..., description="Unique incident identifier"),
    db: Session = Depends(get_db)
) -> IncidentDetailResponse:
    repo = IncidentRepository(db)
    inc = repo.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")
    
    inc.status = "RESOLVED"
    inc.resolved_at = datetime.now(timezone.utc)
    db.commit()

    return IncidentDetailResponse(
        incident_id=inc.id,
        status=inc.status,
        attack_class=inc.attack_class,
        severity=inc.severity,
        created_at=inc.created_at.isoformat(),
        updated_at=inc.updated_at.isoformat(),
        resolution_timestamp=inc.resolved_at.isoformat() if inc.resolved_at else None,
        first_risk_score=inc.first_risk_score,
        current_risk_score=inc.current_risk_score,
        peak_risk_score=inc.peak_risk_score,
        max_anomaly_score=inc.max_anomaly_score,
        forecast_triggered=inc.forecast_triggered,
        estimated_eta_seconds=inc.estimated_eta_seconds
    )
