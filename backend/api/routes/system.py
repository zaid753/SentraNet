"""
SENTRANET — System Status Route (Phase 7)
"""

from fastapi import APIRouter, Depends
from backend.api.schemas.status import SystemStatusResponse
from backend.api.services.sentranet_service import SentranetService
from backend.api.dependencies import get_sentranet_service

router = APIRouter(tags=["System"])

@router.get(
    "/system/status",
    response_model=SystemStatusResponse,
    summary="Get system status",
    description="Returns detailed readiness of SENTRANET detection and forecasting engines without exposing secrets."
)
def get_system_status(
    service: SentranetService = Depends(get_sentranet_service)
) -> SystemStatusResponse:
    return service.get_system_status()
