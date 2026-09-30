"""
SENTRANET — Risk Timeline Route (Phase 7)
"""

from fastapi import APIRouter, Depends, Query
from backend.api.schemas.timeline import TimelineResponse
from backend.api.services.sentranet_service import SentranetService
from backend.api.dependencies import get_sentranet_service

router = APIRouter(tags=["Timeline"])

@router.get(
    "/timeline",
    response_model=TimelineResponse,
    summary="Get risk trajectory timeline",
    description="Returns chronological sequence of risk and anomaly metrics for plotting trends in the Phase 8 dashboard."
)
def get_timeline(
    limit: int = Query(default=50, ge=1, le=200, description="Number of recent points to retrieve"),
    service: SentranetService = Depends(get_sentranet_service),
) -> TimelineResponse:
    return service.get_timeline(limit=limit)
