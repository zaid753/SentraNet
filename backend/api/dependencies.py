"""
SENTRANET — FastAPI Dependencies (Phase 7)
Provides dependency providers for service singletons.
"""

from backend.api.services.sentranet_service import SentranetService
from backend.api.services.replay_service import ReplayService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.telemetry.stream_processor import StreamProcessor
    from backend.telemetry.synthetic_service import SyntheticStreamService

def get_sentranet_service() -> SentranetService:
    return SentranetService.get_instance()

def get_replay_service() -> ReplayService:
    sentranet_service = SentranetService.get_instance()
    return ReplayService.get_instance(sentranet_service=sentranet_service)

def get_stream_processor() -> "StreamProcessor":
    from backend.telemetry.stream_processor import StreamProcessor
    return StreamProcessor.get_instance()

def get_synthetic_stream_service() -> "SyntheticStreamService":
    from backend.telemetry.synthetic_service import SyntheticStreamService
    return SyntheticStreamService.get_instance()

def get_live_service():
    from backend.api.services.live_service import LiveService
    return LiveService.get_instance()
