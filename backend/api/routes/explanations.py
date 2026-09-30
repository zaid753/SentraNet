"""
SENTRANET — Explainability Routes (Phase 11)
Endpoints for retrieving explainability objects.
"""

from fastapi import APIRouter, HTTPException
from backend.api.services.sentranet_service import SentranetService
from backend.explainability.schemas import ExplanationResponse
from backend.explainability.explainer import get_cached_explanation

router = APIRouter(prefix="/explanations", tags=["explainability"])
sentranet = SentranetService.get_instance()


@router.get("/current", response_model=ExplanationResponse)
async def get_current_explanation():
    """Returns the ExplanationObject for the most recent processed window."""
    try:
        explanation = sentranet.get_current_explanation()
        if not explanation:
            raise HTTPException(status_code=404, detail="No explanation available.")
        return explanation
    except Exception as e:
        # Avoid 500s for expected state exceptions
        if "NO_CURRENT_STATE" in str(e):
            raise HTTPException(status_code=404, detail="No current telemetry state available.")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/window/{window_id}", response_model=ExplanationResponse)
async def get_window_explanation(window_id: str):
    """
    Returns a cached explanation for a specific window timestamp.
    Useful for retrieving explanations for recent past windows.
    """
    explanation = get_cached_explanation(window_id)
    if not explanation:
        raise HTTPException(
            status_code=404, 
            detail=f"Explanation for window '{window_id}' not found or evicted from cache."
        )
    return explanation
