"""
SENTRANET — FastAPI Application (Phase 7)
Clean, typed HTTP service exposing the complete SENTRANET detection,
forecasting, and chronological replay pipeline.
"""

from contextlib import asynccontextmanager
import logging
import os
import yaml
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

from backend.api.database import engine, Base
from backend.api.models import Incident, Alert
from backend.api.persistence_subscriber import setup_persistence_subscriptions

from backend.api.routes import api_router
from backend.api.routes.realtime import router as realtime_router
from backend.api.errors import APIException
from backend.api.services.sentranet_service import SentranetService
from backend.api.services.replay_service import ReplayService

logger = logging.getLogger("sentranet.api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def load_api_config():
    cfg_path = "config/api.yaml"
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

API_CONFIG = load_api_config()
API_META = API_CONFIG.get("api", {})

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing SENTRANET API service...")
    try:
        # Initialize Database
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=engine)
        
        setup_persistence_subscriptions()
        
        sentranet_service = SentranetService.get_instance()
        logger.info(f"Model engines loaded successfully (Feature count: 17).")
        ReplayService.get_instance(sentranet_service=sentranet_service)
        logger.info("Replay simulation service initialized.")
    except Exception as e:
        logger.error(f"Error during startup model initialization: {str(e)}", exc_info=True)

    yield

    # Shutdown sequence
    logger.info("Shutting down SENTRANET API service.")
    try:
        replay_service = ReplayService.get_instance()
        if replay_service.running:
            replay_service.stop()
    except Exception:
        pass

def create_app() -> FastAPI:
    cors_origins = API_META.get(
        "cors_origins",
        ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    app = FastAPI(
        title=API_META.get("title", "SENTRANET API"),
        description=API_META.get(
            "description",
            "AI-based network attack detection and forecasting service (Simulation Replay)."
        ),
        version=API_META.get("version", "0.7.0"),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS configuration
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data:; connect-src 'self' ws: wss: http: https:;"
            return response

    app.add_middleware(SecurityHeadersMiddleware)



    # Exception Handlers
    @app.exception_handler(APIException)
    async def handle_api_exception(request: Request, exc: APIException):
        logger.warning(f"APIException [{exc.code}] at {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        logger.warning(f"RequestValidationError at {request.url.path}: {exc.errors()}")
        safe_errors = []
        for err in exc.errors():
            raw_input = err.get("input")
            safe_input = str(raw_input) if raw_input is not None else None
            safe_errors.append({
                "type": err.get("type"),
                "loc": [str(x) for x in err.get("loc", [])],
                "msg": err.get("msg"),
                "input": safe_input,
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request payload validation failed.",
                    "details": safe_errors,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTPException {exc.status_code} at {request.url.path}: {exc.detail}")
        code_map = {
            400: "BAD_REQUEST",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code_map.get(exc.status_code, "HTTP_ERROR"),
                    "message": str(exc.detail),
                    "details": {},
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        logger.error(f"Unhandled exception at {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred.",
                }
            },
        )

    # Mount API router
    app.include_router(api_router, prefix="/api")

    # Mount WebSocket router
    app.include_router(realtime_router, prefix="/ws", tags=["realtime"])

    # Serve React Frontend (Single Page Application)
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            if full_path.startswith("api/") or full_path.startswith("ws/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
                raise StarletteHTTPException(status_code=404, detail="Not found")
            return FileResponse(os.path.join(frontend_dist, "index.html"))

    return app

# Canonical singleton FastAPI app instance
app = create_app()
