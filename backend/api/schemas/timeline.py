"""
SENTRANET — Timeline Schemas (Phase 7)
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class TimelinePointResponse(BaseModel):
    timestamp: str
    risk_score: float
    risk_state: str
    anomaly_score: float
    attack_class: str
    forecast_active: bool
    eta_seconds: Optional[int] = None

class TimelineResponse(BaseModel):
    total_points: int
    points: List[TimelinePointResponse] = Field(default_factory=list)
