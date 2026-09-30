from fastapi import APIRouter
from app.models.health import HealthResponse
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def check_health():
    return HealthResponse(
        status="healthy",
        service="sentranet-backend",
        version=settings.APP_VERSION
    )
