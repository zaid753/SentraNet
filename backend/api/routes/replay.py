"""
SENTRANET — Replay Routes (Phase 7)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from backend.api.schemas.replay import (
    ReplayStartRequest,
    ReplayStatusResponse,
    ReplayActionResponse,
)
from backend.api.services.replay_service import ReplayService
from backend.api.dependencies import get_replay_service
from backend.api.auth import get_current_workspace
from backend.api.models import Workspace

router = APIRouter(tags=["Replay"])

@router.post(
    "/replay/start",
    response_model=ReplayActionResponse,
    summary="Start historical dataset replay",
    description="Launches batch, realtime, or step replay over historical network telemetry windows."
)
def start_replay(
    request: ReplayStartRequest,
    service: ReplayService = Depends(get_replay_service),
    workspace: Workspace = Depends(get_current_workspace)
) -> ReplayActionResponse:
    with service.lock:
        service.active_workspace_id = workspace.id
    return service.start(request)

@router.post(
    "/replay/stop",
    response_model=ReplayActionResponse,
    summary="Stop historical replay",
    description="Halts any active background or step replay simulation and resolves active incidents."
)
def stop_replay(
    service: ReplayService = Depends(get_replay_service),
) -> ReplayActionResponse:
    return service.stop()

@router.post(
    "/replay/pause",
    response_model=ReplayActionResponse,
    summary="Pause realtime replay",
    description="Pauses execution of the background realtime playback clock."
)
def pause_replay(
    service: ReplayService = Depends(get_replay_service),
) -> ReplayActionResponse:
    return service.pause()

@router.post(
    "/replay/resume",
    response_model=ReplayActionResponse,
    summary="Resume paused replay",
    description="Resumes execution of a paused realtime playback simulation."
)
def resume_replay(
    service: ReplayService = Depends(get_replay_service),
) -> ReplayActionResponse:
    return service.resume()

@router.post(
    "/replay/step",
    response_model=ReplayActionResponse,
    summary="Step single replay window",
    description="Advances the replay simulation exactly one temporal window forward."
)
def step_replay(
    service: ReplayService = Depends(get_replay_service),
) -> ReplayActionResponse:
    return service.step()

@router.get(
    "/replay/status",
    response_model=ReplayStatusResponse,
    summary="Get replay simulation status",
    description="Returns current progress, mode, playback speed, and processed window counts."
)
def get_replay_status(
    service: ReplayService = Depends(get_replay_service),
) -> ReplayStatusResponse:
    return service.get_status()

@router.get(
    "/replay/events",
    response_model=List[Dict[str, Any]],
    summary="Get recent replay events",
    description="Returns telemetry windows and alerts generated during the current or most recent replay."
)
def get_replay_events(
    limit: int = Query(default=50, ge=1, le=100, description="Max replay events to retrieve"),
    event_type: Optional[str] = Query(default=None, description="Optional alert state filter (WATCH, ALERT, NORMAL)"),
    service: ReplayService = Depends(get_replay_service),
) -> List[Dict[str, Any]]:
    return service.get_events(limit=limit, event_type=event_type)
