from fastapi import Request
from fastapi.responses import JSONResponse

class SentranetException(Exception):
    def __init__(self, message: str, error_code: str = "InternalServerError", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

async def sentranet_exception_handler(request: Request, exc: SentranetException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "Unexpected server error"},
    )
