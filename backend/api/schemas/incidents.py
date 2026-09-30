"""
SENTRANET — Incident Schemas (Phase 7)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class IncidentItemResponse(BaseModel):
    incident_id: str
    status: str
    attack_class: str
    severity: str
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    peak_risk: float
    max_anomaly: float
    forecast_triggered: bool
    event_count: int

class IncidentDetailResponse(BaseModel):
    incident_id: str
    status: str
    attack_class: str
    severity: str
    created_at: str
    updated_at: str
    resolution_timestamp: Optional[str] = None
    first_risk_score: float
    current_risk_score: float
    peak_risk_score: float
    max_anomaly_score: float
    forecast_triggered: bool
    estimated_eta_seconds: Optional[int] = None
    confidence: float
    event_count: int
    timestamps: List[str] = Field(default_factory=list)
