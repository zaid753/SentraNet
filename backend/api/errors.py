"""
SENTRANET — API Exception Definitions (Phase 7)
"""

from typing import Dict, Any, Optional

class APIException(Exception):
    def __init__(
        self,
        status_code: int = 400,
        code: str = "BAD_REQUEST",
        message: str = "Invalid request",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

class BadRequestException(APIException):
    def __init__(self, code: str = "BAD_REQUEST", message: str = "Invalid request", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, code=code, message=message, details=details)

class ResourceNotFoundException(APIException):
    def __init__(self, code: str = "RESOURCE_NOT_FOUND", message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, code=code, message=message, details=details)

class ConflictException(APIException):
    def __init__(self, code: str = "CONFLICT", message: str = "State conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, code=code, message=message, details=details)

class ServiceUnavailableException(APIException):
    def __init__(self, code: str = "SERVICE_UNAVAILABLE", message: str = "Service or models unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=503, code=code, message=message, details=details)
