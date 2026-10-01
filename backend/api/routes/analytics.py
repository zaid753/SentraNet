"""
SENTRANET — Analytics Routes (Phase 7)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.api.database import get_db
from backend.api.auth import get_current_workspace
from backend.api.models import Workspace
from backend.api.analytics.analytics_service import AnalyticsService
from backend.api.analytics.schemas import AnalyticsOverviewResponse, SystemHealthResponse

router = APIRouter(tags=["Analytics", "Health"])

@router.get(
    "/analytics/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get analytics overview",
    description="Returns aggregate detection, threat, and risk metrics over a specified time window."
)
def get_analytics_overview(
    time_range: str = Query("all", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace)
) -> AnalyticsOverviewResponse:
    service = AnalyticsService(db)
    data = service.get_overview(workspace.id, time_range)
    return AnalyticsOverviewResponse(**data)

@router.get(
    "/system/health",
    response_model=SystemHealthResponse,
    summary="Get detailed system and model health",
    description="Returns real-time health checks for DB, APIs, WebSockets, and ML components."
)
def get_system_health(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_current_workspace)
) -> SystemHealthResponse:
    service = AnalyticsService(db)
    data = service.get_system_health()
    return SystemHealthResponse(**data)
