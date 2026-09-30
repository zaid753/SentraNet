"""
SENTRANET — Application Entry Point (Phase 7 compatibility)
Re-exports the canonical FastAPI application from backend.api.app.
"""

from backend.api.app import app, create_app

__all__ = ["app", "create_app"]
