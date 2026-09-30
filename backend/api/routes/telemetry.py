"""
SENTRANET — Telemetry API Routes (Phase 9)
Provides REST endpoints for flow ingestion, window flushing, telemetry status,
and synthetic flow generator controls.
"""

from fastapi import APIRouter, Depends, status
from datetime import datetime, timezone

from backend.api.schemas.telemetry import (
    FlowIngestRequest,
    FlowIngestResponse,
    FlowFlushResponse,
    TelemetryStatusResponse,
    SyntheticStartRequest,
    SyntheticStatusResponse,
    TelemetryActionResponse,
)
from backend.api.dependencies import get_stream_processor, get_synthetic_stream_service
from backend.telemetry.stream_processor import StreamProcessor
from backend.telemetry.synthetic_service import SyntheticStreamService
from backend.api.errors import ConflictException

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post(
    "/flow",
    response_model=FlowIngestResponse,
    summary="Ingest a single network flow metadata record",
    description="Accepts a single FlowRecord. Accumulates into 60-second window. Does not run inference until window completes.",
)
async def ingest_flow(
    flow: FlowIngestRequest,
    processor: StreamProcessor = Depends(get_stream_processor),
) -> FlowIngestResponse:
    res = processor.ingest_flow(flow, source_type="live")
    return FlowIngestResponse(
        accepted=res["accepted"],
        window=res.get("window"),
        window_complete=res["window_complete"],
        flows_in_window=res["flows_in_window"],
        source_type=res["source_type"],
        decision=res.get("decision"),
    )


@router.post(
    "/flush",
    response_model=FlowFlushResponse,
    summary="Flush current accumulation window",
    description="Forces emission and AI inference of the currently active flow window.",
)
async def flush_window(
    processor: StreamProcessor = Depends(get_stream_processor),
) -> FlowFlushResponse:
    res = processor.flush()
    return FlowFlushResponse(
        flushed=res["flushed"],
        window=res.get("window"),
        features=res.get("features"),
        decision=res.get("decision"),
        message=res.get("message"),
    )


@router.get(
    "/status",
    response_model=TelemetryStatusResponse,
    summary="Get telemetry stream status",
    description="Returns active telemetry window metrics, current source type, and latest risk.",
)
async def get_telemetry_status(
    processor: StreamProcessor = Depends(get_stream_processor),
) -> TelemetryStatusResponse:
    status_data = processor.get_status()
    return TelemetryStatusResponse(**status_data)


@router.post(
    "/synthetic/start",
    response_model=SyntheticStatusResponse,
    summary="Start synthetic flow generator",
    description="Spawns deterministic background synthetic flow stream feeding StreamProcessor directly.",
)
async def start_synthetic_stream(
    req: SyntheticStartRequest,
    synthetic_svc: SyntheticStreamService = Depends(get_synthetic_stream_service),
) -> SyntheticStatusResponse:
    status_data = synthetic_svc.start(
        speed=req.speed,
        seed=req.seed,
        profile=req.profile,
        duration_seconds=req.duration_seconds,
    )
    return SyntheticStatusResponse(**status_data)


@router.post(
    "/synthetic/stop",
    response_model=SyntheticStatusResponse,
    summary="Stop synthetic flow generator",
    description="Halts synthetic generator and flushes partial accumulated window.",
)
async def stop_synthetic_stream(
    synthetic_svc: SyntheticStreamService = Depends(get_synthetic_stream_service),
) -> SyntheticStatusResponse:
    status_data = synthetic_svc.stop()
    return SyntheticStatusResponse(**status_data)


@router.post(
    "/synthetic/pause",
    response_model=SyntheticStatusResponse,
    summary="Pause synthetic flow generator",
)
async def pause_synthetic_stream(
    synthetic_svc: SyntheticStreamService = Depends(get_synthetic_stream_service),
) -> SyntheticStatusResponse:
    status_data = synthetic_svc.pause()
    return SyntheticStatusResponse(**status_data)


@router.post(
    "/synthetic/resume",
    response_model=SyntheticStatusResponse,
    summary="Resume synthetic flow generator",
)
async def resume_synthetic_stream(
    synthetic_svc: SyntheticStreamService = Depends(get_synthetic_stream_service),
) -> SyntheticStatusResponse:
    status_data = synthetic_svc.resume()
    return SyntheticStatusResponse(**status_data)


@router.get(
    "/synthetic/status",
    response_model=SyntheticStatusResponse,
    summary="Get synthetic flow generator status",
)
async def get_synthetic_status(
    synthetic_svc: SyntheticStreamService = Depends(get_synthetic_stream_service),
) -> SyntheticStatusResponse:
    status_data = synthetic_svc.get_status()
    return SyntheticStatusResponse(**status_data)


@router.post(
    "/reset",
    response_model=TelemetryActionResponse,
    summary="Reset telemetry state",
    description="Resets active accumulation window, rolling history, and telemetry counters. Rejects if synthetic stream is running.",
)
async def reset_telemetry(
    processor: StreamProcessor = Depends(get_stream_processor),
    synthetic_svc: SyntheticStreamService = Depends(get_synthetic_stream_service),
) -> TelemetryActionResponse:
    synth_status = synthetic_svc.get_status()
    if synth_status["status"] in ["running", "paused"]:
        raise ConflictException(
            code="STREAM_ALREADY_RUNNING",
            message="Cannot reset telemetry while synthetic stream is active. Stop the stream first.",
            details={"synthetic_status": synth_status["status"]},
        )

    processor.reset()
    return TelemetryActionResponse(
        status="success",
        message="Telemetry stream state successfully reset.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={"active": False, "source_type": "idle"},
    )
