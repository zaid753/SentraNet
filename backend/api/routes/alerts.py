"""
SENTRANET — Alerts Routes (Phase 7)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from backend.api.schemas.alerts import CurrentAlertResponse, AlertItemResponse
from backend.api.services.sentranet_service import SentranetService
from backend.api.dependencies import get_sentranet_service

router = APIRouter(tags=["Alerts"])

@router.get(
    "/alerts/current",
    response_model=CurrentAlertResponse,
    summary="Get current alert status",
    description="Returns active alert state, active incident details, and forecasted attack properties."
)
def get_current_alert(
    service: SentranetService = Depends(get_sentranet_service)
) -> CurrentAlertResponse:
    return service.get_current_alert()

@router.get(
    "/alerts",
    response_model=List[AlertItemResponse],
    summary="Get alert event history",
    description="Returns chronological alert state machine transitions and incident lifecycle events."
)
def get_alerts(
    limit: int = Query(default=20, ge=1, le=100, description="Max alerts to retrieve"),
    severity: Optional[str] = Query(default=None, description="Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)"),
    attack_class: Optional[str] = Query(default=None, description="Filter by attack class"),
    service: SentranetService = Depends(get_sentranet_service),
) -> List[AlertItemResponse]:
    return service.get_alerts(limit=limit, severity=severity, attack_class=attack_class)
