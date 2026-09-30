"""
SENTRANET — Telemetry API Schemas (Phase 9)
Request and Response models for network flow ingestion and synthetic streaming.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.telemetry.flow_schema import FlowRecord


class FlowIngestRequest(FlowRecord):
    """Network flow ingestion request directly adhering to canonical FlowRecord schema."""
    pass


class FlowIngestResponse(BaseModel):
    accepted: bool
    window: Optional[str] = None
    window_complete: bool
    flows_in_window: int
    source_type: str
    decision: Optional[Dict[str, Any]] = None


class FlowFlushResponse(BaseModel):
    flushed: bool
    window: Optional[str] = None
    features: Optional[Dict[str, float]] = None
    decision: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class TelemetryStatusResponse(BaseModel):
    active: bool
    source_type: str
    current_window_start: Optional[str] = None
    current_window_end: Optional[str] = None
    flows_in_window: int
    windows_processed: int
    flows_processed: int
    latest_timestamp: Optional[str] = None
    latest_risk: Optional[float] = None
    latest_decision: Optional[Dict[str, Any]] = None


class SyntheticStartRequest(BaseModel):
    speed: float = Field(default=10.0, gt=0.0, description="Speed multiplier (> 0)")
    seed: int = Field(default=42, description="Fixed random seed for deterministic generation")
    profile: str = Field(
        default="scenario_1",
        description="Profile: BASELINE, SCANNING, DDOS, BOTNET, scenario_1",
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        gt=0,
        description="Optional limit on total simulation duration in seconds",
    )


class SyntheticStatusResponse(BaseModel):
    running: bool
    status: str
    speed: float
    seed: int
    profile: str
    flows_generated: int
    windows_generated: int
    duration_seconds: Optional[int] = None


class TelemetryActionResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
