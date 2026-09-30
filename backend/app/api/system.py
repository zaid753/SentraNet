from fastapi import APIRouter
from app.models.system import SystemStatus, ComponentStatus

router = APIRouter()

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    return SystemStatus(
        backend=ComponentStatus(status="online"),
        database=ComponentStatus(status="not_configured"),
        ml_models=ComponentStatus(status="not_loaded"),
        replay_engine=ComponentStatus(status="not_initialized"),
        websocket=ComponentStatus(status="not_initialized")
    )
