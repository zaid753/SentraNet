"""
SENTRANET — Inference & Stream Routes (Phase 7)
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from backend.api.schemas.inference import AnalyzeRequest, AnalyzeResponse
from backend.api.services.sentranet_service import SentranetService
from backend.api.services.replay_service import ReplayService
from backend.api.dependencies import get_sentranet_service, get_replay_service

router = APIRouter(tags=["Inference"])

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a network telemetry window",
    description=(
        "Runs one chronological telemetry window through the SENTRANET "
        "detection, anomaly, risk, forecasting, and alerting pipeline."
    )
)
def analyze(
    request: AnalyzeRequest,
    service: SentranetService = Depends(get_sentranet_service),
) -> AnalyzeResponse:
    return service.analyze(request)

@router.post(
    "/stream/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset temporal stream state",
    description="Resets in-memory trajectory history, forecast context, and active alerts for a fresh simulation run."
)
def reset_stream(
    service: SentranetService = Depends(get_sentranet_service),
    replay_service: ReplayService = Depends(get_replay_service),
) -> Dict[str, Any]:
    res = service.reset_stream(is_replay_active_check=replay_service.is_active)
    replay_service.reset()
    return res

@router.get(
    "/risk/current",
    response_model=AnalyzeResponse,
    summary="Get current risk state",
    description="Returns the latest computed risk, anomaly score, and forecast prediction from the active temporal stream."
)
def get_current_risk(
    service: SentranetService = Depends(get_sentranet_service),
) -> AnalyzeResponse:
    return service.get_current_risk()
