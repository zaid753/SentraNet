"""
SENTRANET — Inference & Analysis Schemas (Phase 7)
Strict Pydantic models for the canonical 17-feature telemetry window.
"""

from typing import Dict, Any, List, Optional
import math
from pydantic import BaseModel, Field, field_validator

class NetworkFeatures(BaseModel):
    flow_count: float = Field(..., description="Active flow count")
    total_packets: float = Field(..., description="Total packet volume")
    total_bytes: float = Field(..., description="Total byte volume")
    avg_packet_rate: float = Field(..., description="Average packet rate per second")
    avg_byte_rate: float = Field(..., description="Average byte rate per second")
    unique_sources: float = Field(..., description="Distinct source IP count")
    unique_destinations: float = Field(..., description="Distinct destination IP count")
    avg_packet_size: float = Field(..., description="Mean packet size in bytes")
    avg_flow_duration: float = Field(..., description="Mean flow duration in seconds")
    syn_flag_count: float = Field(..., description="TCP SYN flag occurrences")
    ack_flag_count: float = Field(..., description="TCP ACK flag occurrences")
    privileged_port_ratio: float = Field(..., description="Ratio of flows targeting ports 0-1023")
    rolling_5_flow_count: float = Field(..., description="Causal rolling 5-window flow count")
    rolling_5_total_packets: float = Field(..., description="Causal rolling 5-window total packets")
    rolling_5_total_bytes: float = Field(..., description="Causal rolling 5-window total bytes")
    rolling_5_avg_byte_rate: float = Field(..., description="Causal rolling 5-window average byte rate")
    rolling_5_unique_sources: float = Field(..., description="Causal rolling 5-window unique source IPs")

    @field_validator("*")
    @classmethod
    def check_finite_and_not_nan(cls, v: float, info) -> float:
        if math.isnan(v):
            raise ValueError(f"Feature '{info.field_name}' must not be NaN.")
        if math.isinf(v):
            raise ValueError(f"Feature '{info.field_name}' must not be Infinite.")
        return v

    model_config = {
        "extra": "forbid"
    }

class AnalyzeRequest(BaseModel):
    timestamp: str = Field(..., description="ISO-8601 window timestamp (e.g. 2026-09-30T08:42:00)")
    features: NetworkFeatures = Field(..., description="Canonical 17-feature network telemetry payload")

class AlertEventSummary(BaseModel):
    event_type: str
    incident_id: Optional[str] = None
    severity: str

class AnalyzeResponse(BaseModel):
    timestamp: str
    attack_class: str
    class_probability: float
    attack_likelihood: float
    anomaly_score: float
    is_anomalous: bool
    risk_score: float
    risk_state: str
    risk_velocity: Optional[float] = None
    risk_acceleration: Optional[float] = None
    risk_trend: str
    emergence_detected: bool
    forecast_active: bool
    forecast_class: Optional[str] = None
    estimated_eta_seconds: Optional[int] = None
    forecast_confidence: Optional[float] = None
    alert_state: str
    incident_id: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    alert_event: Optional[AlertEventSummary] = None
    simulation: bool = True
