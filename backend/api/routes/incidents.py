"""
SENTRANET — Incidents Routes (Phase 7)
"""

from typing import List
from fastapi import APIRouter, Depends, Path
from backend.api.schemas.incidents import IncidentItemResponse, IncidentDetailResponse
from backend.explainability.incident_explainer import IncidentExplanation, build_incident_explanation
from backend.api.services.sentranet_service import SentranetService
from backend.api.dependencies import get_sentranet_service
from fastapi import HTTPException

router = APIRouter(tags=["Incidents"])

@router.get(
    "/incidents",
    response_model=List[IncidentItemResponse],
    summary="Get incident history",
    description="Returns summaries of all security incidents correlated by the in-memory IncidentManager."
)
def get_incidents(
    service: SentranetService = Depends(get_sentranet_service)
) -> List[IncidentItemResponse]:
    return service.get_incidents()

@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentDetailResponse,
    summary="Get single incident details",
    description="Returns comprehensive timeline, metrics, and event log for a specific incident."
)
def get_incident(
    incident_id: str = Path(..., description="Unique incident identifier (e.g. INC-0001)"),
    service: SentranetService = Depends(get_sentranet_service),
) -> IncidentDetailResponse:
    return service.get_incident(incident_id=incident_id)

@router.get(
    "/incidents/{incident_id}/explanation",
    response_model=IncidentExplanation,
    summary="Get incident-level explanation",
    description="Returns an explanation and timeline for a specific incident."
)
def get_incident_explanation(
    incident_id: str = Path(..., description="Unique incident identifier"),
    service: SentranetService = Depends(get_sentranet_service),
) -> IncidentExplanation:
    with service.lock:
        if not service.incident_manager:
            raise HTTPException(status_code=404, detail="Incident manager not initialized.")
        
        match = next((inc for inc in service.incident_manager.incidents if inc.incident_id == incident_id), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
        
        return build_incident_explanation(match, service.alert_history)
