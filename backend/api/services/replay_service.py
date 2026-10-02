"""
SENTRANET — Replay Service (Phase 7)
Thread-safe background replay orchestrator wrapping Phase 6 ReplayEngine.
Provides batch, realtime, and step playback without external queues or brokers.
"""

from typing import Dict, Any, List, Optional
import os
import threading
import time
import datetime
import pandas as pd

from backend.replay.replay_config import ReplayConfig
from backend.replay.replay_engine import ReplayEngine
from backend.replay.replay_event import ReplayEvent, AlertEvent
from backend.api.services.sentranet_service import SentranetService
from backend.api.schemas.replay import (
    ReplayStartRequest,
    ReplayStatusResponse,
    ReplayActionResponse,
)
from backend.api.errors import BadRequestException, ConflictException, ResourceNotFoundException

DATASET_PRESETS = {
    "full": "full_synthetic_fixture",
    "synthetic": "full_synthetic_fixture",
    "all": "full_synthetic_fixture",
    "validation": "data/processed/sample/validation.parquet",
    "test": "data/processed/sample/test.parquet",
    "train": "data/processed/sample/train.parquet",
    "sample": "data/processed/sample/validation.parquet",
}

class ReplayService:
    """
    Singleton service managing historical replay simulation lifecycle.
    """

    _instance: Optional["ReplayService"] = None
    _singleton_lock = threading.Lock()

    def __init__(self, sentranet_service: Optional[SentranetService] = None):
        self.lock = threading.Lock()
        self.sentranet_service = sentranet_service or SentranetService.get_instance()
        self.config = ReplayConfig.load()

        self.running: bool = False
        self.paused: bool = False
        self.mode: str = "batch"
        self.speed: float = 10.0
        self.dataset_name: Optional[str] = None
        self.current_timestamp: Optional[str] = None
        self.windows_processed: int = 0
        self.windows_processed: int = 0
        self.total_windows: int = 0

        self.replay_events_history: List[ReplayEvent] = []

        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Initially unpaused

        self._worker_thread: Optional[threading.Thread] = None
        self._engine: Optional[ReplayEngine] = None
        self._df: Optional[pd.DataFrame] = None
        self._generator = None

    @classmethod
    def get_instance(cls, sentranet_service: Optional[SentranetService] = None) -> "ReplayService":
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = cls(sentranet_service=sentranet_service)
            return cls._instance

    def is_active(self) -> bool:
        with self.lock:
            return self.running

    def reset(self) -> None:
        with self.lock:
            self.running = False
            self.paused = False
            self.dataset_name = None
            self.current_timestamp = None
            self.windows_processed = 0
            self.total_windows = 0
            self.replay_events_history.clear()
            self._generator = None
            self._engine = None

    def _load_dataset_df(self, identifier: str) -> tuple[pd.DataFrame, str]:
        key = identifier.lower().strip()
        if key not in DATASET_PRESETS:
            valid = list(DATASET_PRESETS.keys())
            raise BadRequestException(
                code="INVALID_DATASET",
                message=f"Dataset identifier '{identifier}' is not recognized. Predefined options: {valid}"
            )

        target = DATASET_PRESETS[key]
        if target == "full_synthetic_fixture":
            p_train = "data/processed/sample/train.parquet"
            p_val = "data/processed/sample/validation.parquet"
            p_test = "data/processed/sample/test.parquet"
            for p in (p_train, p_val, p_test):
                if not os.path.exists(p):
                    raise ResourceNotFoundException(
                        code="DATASET_FILE_NOT_FOUND",
                        message=f"Required parquet partition '{p}' missing from filesystem."
                    )
            df1 = pd.read_parquet(p_train)
            df2 = pd.read_parquet(p_val)
            df3 = pd.read_parquet(p_test)
            df = pd.concat([df1, df2, df3], ignore_index=True)
            name = "full_synthetic_fixture"
        else:
            if not os.path.exists(target):
                raise ResourceNotFoundException(
                    code="DATASET_FILE_NOT_FOUND",
                    message=f"Dataset file '{target}' missing from filesystem."
                )
            df = pd.read_parquet(target)
            name = os.path.basename(target)

        ts_col = "window_start" if "window_start" in df.columns else "timestamp"
        if ts_col not in df.columns:
            raise BadRequestException(
                code="INVALID_DATASET_SCHEMA",
                message=f"Dataset '{name}' lacks required timestamp column ('window_start' or 'timestamp')."
            )

        df_sorted = df.sort_values(ts_col).reset_index(drop=True)
        return df_sorted, name

    def start(self, request: ReplayStartRequest) -> ReplayActionResponse:
        mode = request.mode.lower().strip()
        if mode not in {"batch", "realtime", "step"}:
            raise BadRequestException(
                code="INVALID_REPLAY_MODE",
                message=f"Mode '{request.mode}' invalid. Supported modes: ['batch', 'realtime', 'step']."
            )

        if mode == "realtime" and request.speed <= 0:
            raise BadRequestException(
                code="INVALID_SPEED",
                message="Speed multiplier must be strictly greater than 0 for realtime replay."
            )

        with self.lock:
            if self.running:
                raise ConflictException(
                    code="REPLAY_ALREADY_RUNNING",
                    message="A replay is already in progress. Stop or pause current simulation before starting a new one."
                )

            df_sorted, ds_name = self._load_dataset_df(request.dataset)

            self.mode = mode
            self.speed = float(request.speed)
            self.dataset_name = ds_name
            self.total_windows = len(df_sorted)
            self.windows_processed = 0
            self.current_timestamp = None
            self.paused = False
            self.running = True

            self._stop_event.clear()
            self._pause_event.set()

            # Initialize ReplayEngine sharing SentranetService components
            self._engine = ReplayEngine(
                config=self.config,
                forecast_engine=self.sentranet_service.forecast_engine,
                mode=self.mode,
                speed=self.speed,
                incident_manager=self.sentranet_service.incident_manager,
                state_machine=self.sentranet_service.state_machine,
            )
            # In ReplayEngine, avoid blocking clock sleep inside engine since service manages pacing
            self._engine.clock.mode = "batch"

            self._df = df_sorted
            self._generator = self._engine.replay_stream(df_sorted)

            if mode == "batch":
                self._run_batch()
                return ReplayActionResponse(
                    status="completed",
                    message="Batch replay processed all historical windows.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    details={
                        "mode": "batch",
                        "dataset": ds_name,
                        "windows_processed": self.windows_processed,
                        "total_windows": self.total_windows,
                    }
                )

            elif mode == "realtime":
                self._worker_thread = threading.Thread(target=self._run_realtime_loop, daemon=True)
                self._worker_thread.start()
                return ReplayActionResponse(
                    status="started",
                    message=f"Realtime replay background simulation started at {self.speed}x speed.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    details={
                        "mode": "realtime",
                        "speed": self.speed,
                        "dataset": ds_name,
                        "total_windows": self.total_windows,
                    }
                )

            else:  # mode == "step"
                return ReplayActionResponse(
                    status="started",
                    message="Step mode initialized. Call POST /api/replay/step to advance one window at a time.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    details={
                        "mode": "step",
                        "dataset": ds_name,
                        "total_windows": self.total_windows,
                    }
                )

    def _run_batch(self) -> None:
        """Executes all remaining windows in generator synchronously."""
        try:
            for replay_event, alert_events in self._generator:
                self.current_timestamp = replay_event.timestamp
                self.windows_processed += 1
                self.replay_events_history.append(replay_event)
                if len(self.replay_events_history) > 500:
                    self.replay_events_history.pop(0)

                self.sentranet_service.sync_from_replay(replay_event, alert_events)
        finally:
            self.running = False

    def _run_realtime_loop(self) -> None:
        """Runs background pacing loop for realtime simulation."""
        prev_dt = None

        try:
            for replay_event, alert_events in self._generator:
                if self._stop_event.is_set():
                    break

                # Handle pause
                self._pause_event.wait()
                if self._stop_event.is_set():
                    break

                curr_dt = pd.to_datetime(replay_event.timestamp).to_pydatetime()
                if prev_dt is not None:
                    delta_sec = max(0.0, (curr_dt - prev_dt).total_seconds())
                    sleep_dur = delta_sec / self.speed
                    # Cap sleep to prevent excessive hanging in testing
                    capped_sleep = min(5.0, sleep_dur)
                    if capped_sleep > 0:
                        interrupted = self._stop_event.wait(timeout=capped_sleep)
                        if interrupted:
                            break

                prev_dt = curr_dt

                with self.lock:
                    self.current_timestamp = replay_event.timestamp
                    self.windows_processed += 1
                    self.replay_events_history.append(replay_event)
                    if len(self.replay_events_history) > 500:
                        self.replay_events_history.pop(0)

                self.sentranet_service.sync_from_replay(replay_event, alert_events)

        except Exception:
            pass
        finally:
            with self.lock:
                self.running = False
                self.paused = False

    def stop(self) -> ReplayActionResponse:
        with self.lock:
            if not self.running:
                return ReplayActionResponse(
                    status="stopped",
                    message="No replay is currently active.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    details={"windows_processed": self.windows_processed}
                )

            self._stop_event.set()
            self._pause_event.set()
            self.running = False
            self.paused = False

            # Force resolve any lingering active incident cleanly
            if self.sentranet_service.incident_manager and self.current_timestamp:
                resolves = self.sentranet_service.incident_manager.force_resolve_all(self.current_timestamp)
                self.sentranet_service.alert_history.extend(resolves)

            return ReplayActionResponse(
                status="stopped",
                message="Replay simulation halted successfully.",
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                details={"windows_processed": self.windows_processed}
            )

    def pause(self) -> ReplayActionResponse:
        with self.lock:
            if not self.running:
                raise ConflictException(
                    code="NO_ACTIVE_REPLAY",
                    message="Cannot pause: no replay is currently running."
                )
            if self.paused:
                return ReplayActionResponse(
                    status="paused",
                    message="Replay is already paused.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                )

            self.paused = True
            self._pause_event.clear()

            return ReplayActionResponse(
                status="paused",
                message="Replay simulation paused.",
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                details={"current_timestamp": self.current_timestamp, "windows_processed": self.windows_processed}
            )

    def resume(self) -> ReplayActionResponse:
        with self.lock:
            if not self.running:
                raise ConflictException(
                    code="NO_ACTIVE_REPLAY",
                    message="Cannot resume: no replay is currently running."
                )
            if not self.paused:
                return ReplayActionResponse(
                    status="resumed",
                    message="Replay is already running.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                )

            self.paused = False
            self._pause_event.set()

            return ReplayActionResponse(
                status="resumed",
                message="Replay simulation resumed.",
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                details={"current_timestamp": self.current_timestamp, "windows_processed": self.windows_processed}
            )

    def step(self) -> ReplayActionResponse:
        with self.lock:
            if not self.running or self._generator is None:
                # If step is called while idle, start with default validation dataset
                df_sorted, ds_name = self._load_dataset_df("validation")
                self.mode = "step"
                self.speed = 10.0
                self.dataset_name = ds_name
                self.total_windows = len(df_sorted)
                self.windows_processed = 0
                self.current_timestamp = None
                self.paused = False
                self.running = True

                self._engine = ReplayEngine(
                    config=self.config,
                    forecast_engine=self.sentranet_service.forecast_engine,
                    mode="step",
                    speed=10.0,
                    incident_manager=self.sentranet_service.incident_manager,
                    state_machine=self.sentranet_service.state_machine,
                )
                self._engine.clock.mode = "batch"
                self._generator = self._engine.replay_stream(df_sorted)

            try:
                replay_event, alert_events = next(self._generator)
                self.current_timestamp = replay_event.timestamp
                self.windows_processed += 1
                self.replay_events_history.append(replay_event)
                if len(self.replay_events_history) > 500:
                    self.replay_events_history.pop(0)

                self.sentranet_service.sync_from_replay(replay_event, alert_events)

                return ReplayActionResponse(
                    status="stepped",
                    message="Advanced one temporal window.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    details={
                        "current_timestamp": self.current_timestamp,
                        "windows_processed": self.windows_processed,
                        "total_windows": self.total_windows,
                        "risk_score": replay_event.risk_score,
                        "alert_state": replay_event.alert_state,
                    }
                )
            except StopIteration:
                self.running = False
                return ReplayActionResponse(
                    status="completed",
                    message="Dataset fully processed in step mode.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    details={
                        "windows_processed": self.windows_processed,
                        "total_windows": self.total_windows,
                    }
                )

    def get_status(self) -> ReplayStatusResponse:
        with self.lock:
            prog = (
                float(round(self.windows_processed / self.total_windows, 4))
                if self.total_windows > 0
                else 0.0
            )
            return ReplayStatusResponse(
                running=self.running,
                paused=self.paused,
                mode=self.mode,
                speed=self.speed,
                dataset=self.dataset_name,
                current_timestamp=self.current_timestamp,
                windows_processed=self.windows_processed,
                total_windows=self.total_windows,
                progress=prog,
            )

    def get_events(
        self,
        limit: int = 50,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self.lock:
            events = [e.to_dict() for e in self.replay_events_history]
            if event_type:
                events = [e for e in events if e.get("alert_state", "").lower() == event_type.lower()]
            safe_limit = max(1, min(limit, 100))
            return events[-safe_limit:]
