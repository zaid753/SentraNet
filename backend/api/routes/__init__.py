"""
SENTRANET — API Routers Aggregation (Phase 7)
"""

from fastapi import APIRouter
from backend.api.routes.health import router as health_router
from backend.api.routes.system import router as system_router
from backend.api.routes.inference import router as inference_router
from backend.api.routes.alerts import router as alerts_router
from backend.api.routes.incidents import router as incidents_router
from backend.api.routes.timeline import router as timeline_router
from backend.api.routes.replay import router as replay_router
from backend.api.routes.telemetry import router as telemetry_router
from backend.api.routes.evaluation import router as evaluation_router
from backend.api.routes.explanations import router as explanations_router
from backend.api.routes.analytics import router as analytics_router
from backend.api.routes.auth import router as auth_router
from backend.api.auth import get_current_workspace
from fastapi import Depends

api_router = APIRouter()

auth_deps = [Depends(get_current_workspace)]

api_router.include_router(health_router, dependencies=auth_deps)
api_router.include_router(system_router, dependencies=auth_deps)
api_router.include_router(inference_router, dependencies=auth_deps)
api_router.include_router(alerts_router, dependencies=auth_deps)
# Incidents router already uses Depends explicitly in the file
api_router.include_router(incidents_router, dependencies=auth_deps)
api_router.include_router(timeline_router, dependencies=auth_deps)
api_router.include_router(replay_router, dependencies=auth_deps)
api_router.include_router(telemetry_router, dependencies=auth_deps)
api_router.include_router(evaluation_router, dependencies=auth_deps)
api_router.include_router(explanations_router, dependencies=auth_deps)
api_router.include_router(analytics_router, dependencies=auth_deps)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

__all__ = ["api_router"]
