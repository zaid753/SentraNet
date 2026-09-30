"""
SENTRANET — Flow Validator (Phase 9)
Enforces strict validation on incoming flow metadata dictionaries or objects.
"""

from typing import Dict, Any, Union
from backend.telemetry.flow_schema import FlowRecord
from backend.api.errors import BadRequestException

class InvalidFlowException(BadRequestException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(code="INVALID_FLOW", message=message, details=details or {})

def validate_flow_record(flow_data: Union[Dict[str, Any], FlowRecord]) -> FlowRecord:
    """
    Validates that a raw dictionary or FlowRecord strictly conforms to canonical schema.
    Raises InvalidFlowException on failure.
    """
    if isinstance(flow_data, FlowRecord):
        return flow_data

    if not isinstance(flow_data, dict):
        raise InvalidFlowException(
            message=f"Flow payload must be a JSON object, got {type(flow_data).__name__}."
        )

    try:
        return FlowRecord(**flow_data)
    except Exception as e:
        raise InvalidFlowException(
            message=f"Flow record validation failed: {str(e)}",
            details={"error": str(e)}
        )
