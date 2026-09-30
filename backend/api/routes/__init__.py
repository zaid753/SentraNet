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

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(system_router)
api_router.include_router(inference_router)
api_router.include_router(alerts_router)
api_router.include_router(incidents_router)
api_router.include_router(timeline_router)
api_router.include_router(replay_router)
api_router.include_router(telemetry_router)
api_router.include_router(evaluation_router)
api_router.include_router(explanations_router)

__all__ = ["api_router"]
