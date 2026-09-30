"""
SENTRANET — Synthetic Stream Service (Phase 9)
Manages the background execution, pacing, and thread lifecycle of the
synthetic telemetry flow generator feeding the StreamProcessor.
"""

from typing import Optional, Dict, Any
import time
import threading
import logging

from backend.telemetry.synthetic_source import SyntheticFlowSource, VALID_PROFILES
from backend.telemetry.stream_processor import StreamProcessor
from backend.api.errors import ConflictException, BadRequestException

logger = logging.getLogger("sentranet.telemetry.synthetic_service")


class SyntheticStreamService:
    """
    Thread-safe runner for high-performance synthetic flow generation.
    Feeds generated FlowRecords directly to StreamProcessor without HTTP overhead.
    """

    _instance: Optional["SyntheticStreamService"] = None
    _init_lock = threading.Lock()

    def __init__(self, stream_processor: Optional[StreamProcessor] = None):
        self.stream_processor = stream_processor or StreamProcessor.get_instance()
        self._lock = threading.Lock()

        self.state: str = "idle"  # idle | running | paused | stopped
        self.speed: float = 10.0
        self.seed: int = 42
        self.profile: str = "scenario_1"
        self.duration_seconds: Optional[int] = None

        self.flows_generated: int = 0
        self.windows_generated: int = 0

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._generator: Optional[SyntheticFlowSource] = None

    @classmethod
    def get_instance(cls) -> "SyntheticStreamService":
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start(
        self,
        speed: float = 10.0,
        seed: int = 42,
        profile: str = "scenario_1",
        duration_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Starts the synthetic flow stream."""
        # Validation
        if speed <= 0:
            raise BadRequestException(
                code="INVALID_SPEED",
                message=f"Speed multiplier must be positive (got {speed}).",
            )
        if profile not in VALID_PROFILES:
            raise BadRequestException(
                code="INVALID_PROFILE",
                message=f"Unknown profile '{profile}'. Allowed profiles: {sorted(list(VALID_PROFILES))}.",
            )

        with self._lock:
            if self.state in ["running", "paused"]:
                raise ConflictException(
                    code="STREAM_ALREADY_RUNNING",
                    message="A synthetic stream is already actively running or paused.",
                )

            self.speed = float(speed)
            self.seed = int(seed)
            self.profile = profile
            self.duration_seconds = duration_seconds
            self.flows_generated = 0
            self.windows_generated = 0

            self._stop_event.clear()
            self._pause_event.clear()
            self.state = "running"

            self._generator = SyntheticFlowSource(
                seed=self.seed,
                profile=self.profile,
            )

            # Mark stream processor source type
            self.stream_processor.source_type = "synthetic"

            self._thread = threading.Thread(
                target=self._run_loop,
                daemon=True,
                name="sentranet-synthetic-stream",
            )
            self._thread.start()
            logger.info(
                f"[SyntheticStreamService] Started synthetic stream with seed={self.seed}, "
                f"profile='{self.profile}', speed={self.speed}x."
            )

        return self.get_status()

    def pause(self) -> Dict[str, Any]:
        """Pauses an actively running stream."""
        with self._lock:
            if self.state != "running":
                if self.state in ["idle", "stopped"]:
                    raise ConflictException(
                        code="STREAM_NOT_RUNNING",
                        message="Cannot pause: synthetic stream is not currently running.",
                    )
                elif self.state == "paused":
                    return self.get_status()

            self._pause_event.set()
            self.state = "paused"
            logger.info("[SyntheticStreamService] Paused synthetic stream.")

        return self.get_status()

    def resume(self) -> Dict[str, Any]:
        """Resumes a paused stream."""
        with self._lock:
            if self.state != "paused":
                raise ConflictException(
                    code="STREAM_NOT_PAUSED",
                    message="Cannot resume: synthetic stream is not currently paused.",
                )

            self._pause_event.clear()
            self.state = "running"
            logger.info("[SyntheticStreamService] Resumed synthetic stream.")

        return self.get_status()

    def stop(self) -> Dict[str, Any]:
        """Stops an active or paused stream."""
        with self._lock:
            if self.state in ["idle", "stopped"]:
                raise ConflictException(
                    code="STREAM_NOT_RUNNING",
                    message="Cannot stop: synthetic stream is not running.",
                )

            self._stop_event.set()
            self._pause_event.clear()
            self.state = "stopped"
            logger.info("[SyntheticStreamService] Stopped synthetic stream.")

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        # Flush any remaining partial window upon stop
        self.stream_processor.flush()

        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Returns synthetic stream status."""
        with self._lock:
            return {
                "running": self.state == "running",
                "status": self.state,
                "speed": self.speed,
                "seed": self.seed,
                "profile": self.profile,
                "flows_generated": self.flows_generated,
                "windows_generated": self.windows_generated,
                "duration_seconds": self.duration_seconds,
            }

    def _run_loop(self) -> None:
        """Internal generator loop running in background daemon thread."""
        start_real_time = time.time()

        try:
            while not self._stop_event.is_set():
                # Check Pause
                while self._pause_event.is_set() and not self._stop_event.is_set():
                    time.sleep(0.05)

                if self._stop_event.is_set():
                    break

                # Check duration limit
                if self.duration_seconds is not None:
                    elapsed_real = time.time() - start_real_time
                    if elapsed_real * self.speed >= self.duration_seconds:
                        logger.info(
                            f"[SyntheticStreamService] Reached requested duration of {self.duration_seconds}s."
                        )
                        break

                # Read next FlowRecord from generator
                flow = self._generator.read()
                if flow is None:
                    break

                with self._lock:
                    self.flows_generated += 1

                # Ingest flow into processor
                res = self.stream_processor.ingest_flow(flow, source_type="synthetic")
                if res.get("window_complete", False):
                    with self._lock:
                        self.windows_generated += 1

                # Sleep interval scaled by speed factor
                # Base simulated inter-flow time: ~0.05s / speed, minimum sleep 0.001s
                sleep_sec = max(0.001, 0.05 / self.speed)
                time.sleep(sleep_sec)

        except Exception as e:
            logger.error(f"[SyntheticStreamService] Error in generator loop: {e}", exc_info=True)
        finally:
            with self._lock:
                self.state = "stopped"
                logger.info(
                    f"[SyntheticStreamService] Generator completed. Total flows: {self.flows_generated}, "
                    f"windows: {self.windows_generated}."
                )
