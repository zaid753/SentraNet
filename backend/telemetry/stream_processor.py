"""
SENTRANET — Stream Processor (Phase 9)
Coordinates real-time flow ingestion, validation, normalization,
60-second window aggregation, rolling history, and SENTRANET AI inference.
"""

from typing import Dict, Any, Optional, Union, Tuple, List
from collections import deque
import threading
import logging

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.flow_validator import validate_flow_record
from backend.telemetry.flow_normalizer import normalize_flow
from backend.telemetry.window_aggregator import WindowAggregator
from backend.telemetry.ai_adapter import AIAdapter
from backend.api.schemas.inference import AnalyzeResponse

logger = logging.getLogger("sentranet.telemetry.processor")


class StreamProcessor:
    """
    Thread-safe Central Telemetry Stream Processor.
    Accepts flow records, accumulates 60-second temporal windows,
    triggers AI inference upon window completion, and tracks stream metrics.
    """

    _instance: Optional["StreamProcessor"] = None
    _init_lock = threading.Lock()

    def __init__(
        self,
        window_size_seconds: int = 60,
        rolling_window_count: int = 5,
        max_recent_windows: int = 100,
        ai_adapter: Optional[AIAdapter] = None,
    ):
        self.window_aggregator = WindowAggregator(
            window_size_seconds=window_size_seconds,
            rolling_window_count=rolling_window_count,
        )
        self.ai_adapter = ai_adapter or AIAdapter()
        self.max_recent_windows = max_recent_windows

        self._lock = threading.Lock()

        # Stream State
        self.source_type: str = "idle"
        self.windows_processed: int = 0
        self.flows_processed: int = 0
        self.latest_timestamp: Optional[str] = None
        self.latest_decision: Optional[AnalyzeResponse] = None
        self.latest_features: Optional[Dict[str, float]] = None
        self.recent_windows: deque = deque(maxlen=max_recent_windows)

    @classmethod
    def get_instance(cls) -> "StreamProcessor":
        """Singleton accessor for thread-safe shared processor across FastAPI routes."""
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def ingest_flow(
        self,
        flow_data: Union[FlowRecord, Dict[str, Any]],
        source_type: str = "live",
    ) -> Dict[str, Any]:
        """
        Ingests a single network flow record.
        Validates, normalizes, assigns to the 60-second window, and executes AI inference
        if a window is completed.
        """
        # Step 1: Validate
        flow = validate_flow_record(flow_data)

        # Step 2: Normalize
        norm_flow = normalize_flow(flow)

        with self._lock:
            self.flows_processed += 1
            if self.source_type == "idle":
                self.source_type = source_type

            # Step 3 & 4: Add to Window Aggregator
            completed, window_ts, features = self.window_aggregator.add_flow(norm_flow)

            active_window_start = (
                self.window_aggregator.current_window_start.isoformat()
                if self.window_aggregator.current_window_start
                else None
            )
            flows_in_window = len(self.window_aggregator.flows_in_window)

            if not completed:
                return {
                    "accepted": True,
                    "window": active_window_start,
                    "window_complete": False,
                    "flows_in_window": flows_in_window,
                    "source_type": self.source_type,
                }

            # Step 5: Window Completed -> Run AI Inference
            decision = self.ai_adapter.analyze_window(window_ts, features)

            self.windows_processed += 1
            self.latest_timestamp = window_ts
            self.latest_decision = decision
            self.latest_features = features

            window_record = {
                "window": window_ts,
                "features": features,
                "decision": decision.model_dump(),
            }
            self.recent_windows.append(window_record)

            logger.info(
                f"[StreamProcessor] Completed window '{window_ts}' with {features.get('flow_count', 0)} flows. "
                f"Prediction: {decision.attack_class} (Risk: {decision.risk_score:.3f})"
            )

            return {
                "accepted": True,
                "window": window_ts,
                "window_complete": True,
                "flows_in_window": flows_in_window,
                "source_type": self.source_type,
                "features": features,
                "decision": decision.model_dump(),
            }

    def flush(self) -> Dict[str, Any]:
        """
        Forces immediate emission of the active accumulation window.
        Executes AI inference on the completed window.
        """
        with self._lock:
            completed, window_ts, features = self.window_aggregator.flush()

            if not completed or features is None:
                return {
                    "flushed": False,
                    "message": "No active window or flows to flush.",
                    "window": None,
                }

            decision = self.ai_adapter.analyze_window(window_ts, features)

            self.windows_processed += 1
            self.latest_timestamp = window_ts
            self.latest_decision = decision
            self.latest_features = features

            window_record = {
                "window": window_ts,
                "features": features,
                "decision": decision.model_dump(),
            }
            self.recent_windows.append(window_record)

            logger.info(
                f"[StreamProcessor] Flushed window '{window_ts}' ({features.get('flow_count', 0)} flows). "
                f"Attack: {decision.attack_class} (Risk: {decision.risk_score:.3f})"
            )

            return {
                "flushed": True,
                "window": window_ts,
                "features": features,
                "decision": decision.model_dump(),
            }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and telemetry health metrics."""
        with self._lock:
            flows_in_win = len(self.window_aggregator.flows_in_window)
            is_active = self.source_type != "idle" or flows_in_win > 0 or self.windows_processed > 0

            latest_risk = (
                float(self.latest_decision.risk_score)
                if self.latest_decision is not None
                else None
            )

            return {
                "active": is_active,
                "source_type": self.source_type,
                "current_window_start": (
                    self.window_aggregator.current_window_start.isoformat()
                    if self.window_aggregator.current_window_start
                    else None
                ),
                "current_window_end": (
                    self.window_aggregator.current_window_end.isoformat()
                    if self.window_aggregator.current_window_end
                    else None
                ),
                "flows_in_window": flows_in_win,
                "windows_processed": self.windows_processed,
                "flows_processed": self.flows_processed,
                "latest_timestamp": self.latest_timestamp,
                "latest_risk": latest_risk,
                "latest_decision": (
                    self.latest_decision.model_dump()
                    if self.latest_decision is not None
                    else None
                ),
            }

    def reset(self) -> None:
        """
        Clears all in-memory aggregation buffers, rolling history, decisions, and counters.
        Strictly preserves model artifacts, configuration, and datasets.
        """
        with self._lock:
            self.window_aggregator.reset()
            try:
                self.ai_adapter.service.reset_stream()
            except Exception as e:
                logger.warning(f"[StreamProcessor] reset_stream on service had warning: {e}")
            self.source_type = "idle"
            self.windows_processed = 0
            self.flows_processed = 0
            self.latest_timestamp = None
            self.latest_decision = None
            self.latest_features = None
            self.recent_windows.clear()
            logger.info("[StreamProcessor] Telemetry stream state successfully reset.")
