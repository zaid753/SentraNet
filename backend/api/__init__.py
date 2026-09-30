"""
SENTRANET — API Package (Phase 7)
Uses lazy attribute loading to prevent circular import cascades.
"""

from typing import Any

def __getattr__(name: str) -> Any:
    if name == "app":
        from backend.api.app import app
        return app
    elif name == "api_router":
        from backend.api.routes import api_router
        return api_router
    elif name == "SentranetService":
        from backend.api.services.sentranet_service import SentranetService
        return SentranetService
    elif name == "ReplayService":
        from backend.api.services.replay_service import ReplayService
        return ReplayService
    raise AttributeError(f"module 'backend.api' has no attribute '{name}'")

__all__ = ["app", "api_router", "SentranetService", "ReplayService"]
