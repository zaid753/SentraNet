"""
SENTRANET — Alert Schemas (Phase 7)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AlertItemResponse(BaseModel):
    alert_event_id: str
    incident_id: Optional[str] = None
    event_type: str
    timestamp: str
    attack_class: str
    severity: str
    risk_score: float
    anomaly_score: float
    reasons: List[str] = Field(default_factory=list)
    forecast_active: bool = False
    estimated_eta_seconds: Optional[int] = None
    forecast_confidence: Optional[float] = None

class CurrentAlertResponse(BaseModel):
    active: bool
    incident: Optional[Dict[str, Any]] = None
    alert_state: str = "NORMAL"
    severity: str = "INFO"
    attack_class: Optional[str] = None
    risk_score: Optional[float] = None
    anomaly_score: Optional[float] = None
    forecast_active: bool = False
    estimated_eta_seconds: Optional[int] = None
    forecast_confidence: Optional[float] = None
    reasons: List[str] = Field(default_factory=list)
