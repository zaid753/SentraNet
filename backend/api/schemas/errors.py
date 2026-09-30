"""
SENTRANET — API Error Schemas (Phase 7)
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or validation details")

class ErrorResponse(BaseModel):
    error: ErrorDetail
