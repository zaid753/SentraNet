"""
SENTRANET — Health Route (Phase 7)
"""

import datetime
from fastapi import APIRouter
from backend.api.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns lightweight health indicator without invoking machine learning inference models."
)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="sentranet-api",
        version="0.7.0",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        simulation=True,
    )
