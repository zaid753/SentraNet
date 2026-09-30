"""
SENTRANET — Replay Schemas (Phase 7)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ReplayStartRequest(BaseModel):
    mode: str = Field(default="batch", description="Replay mode: batch, realtime, or step")
    speed: float = Field(default=10.0, ge=0.1, description="Speed multiplier for realtime simulation")
    dataset: str = Field(default="validation", description="Dataset identifier: validation, train, test, or full")

class ReplayStatusResponse(BaseModel):
    running: bool
    paused: bool
    mode: str
    speed: float
    dataset: Optional[str] = None
    current_timestamp: Optional[str] = None
    windows_processed: int
    total_windows: int
    progress: float

class ReplayActionResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
