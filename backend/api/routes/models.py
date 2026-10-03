from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from backend.api.services.model_registry import ModelRegistry, ModelRegistryEntry
from backend.api.services.sentranet_service import SentranetService
from backend.api.errors import ResourceNotFoundException

router = APIRouter(prefix="/models", tags=["models"])

class SetModelRequest(BaseModel):
    model_id: str

def get_sentranet_service() -> SentranetService:
    return SentranetService.get_instance()

@router.get("/", response_model=List[ModelRegistryEntry])
def list_models():
    """Lists all available SENTRANET models."""
    return ModelRegistry.list_models()

@router.get("/active", response_model=ModelRegistryEntry)
def get_active_model(svc: SentranetService = Depends(get_sentranet_service)):
    """Returns the currently active model metadata."""
    try:
        return ModelRegistry.get_model(svc.active_model_id)
    except ValueError:
        raise ResourceNotFoundException("Active model not found in registry.")

@router.post("/active")
def set_active_model(request: SetModelRequest, svc: SentranetService = Depends(get_sentranet_service)):
    """Sets the active model and reloads the pipeline."""
    try:
        svc.set_active_model(request.model_id)
        return {"status": "success", "active_model_id": request.model_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
