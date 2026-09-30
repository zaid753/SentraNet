"""
SENTRANET — Health & Status Schemas (Phase 7)
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service health indicator (healthy/ok)")
    service: str = Field(default="sentranet-api", description="Service identifier")
    version: str = Field(default="0.7.0", description="API version")
    timestamp: str = Field(..., description="Current ISO timestamp")
    simulation: bool = Field(default=True, description="Indicates simulation/replay environment")

class ComponentStatus(BaseModel):
    status: str

class SystemStatusResponse(BaseModel):
    service: str = Field(default="SENTRANET")
    status: str = Field(default="ready")
    simulation: bool = Field(default=True)
    models: Dict[str, str] = Field(default_factory=dict)
    pipeline: Dict[str, str] = Field(default_factory=dict)
    feature_count: int = Field(default=17)

    # Backward compatibility with Phase 1 status tests
    backend: Optional[ComponentStatus] = Field(default_factory=lambda: ComponentStatus(status="online"))
    ml_models: Optional[ComponentStatus] = Field(default_factory=lambda: ComponentStatus(status="loaded"))
