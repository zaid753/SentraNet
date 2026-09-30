"""
SENTRANET — Temporal Window Aggregator (Phase 9)
Converts individual FlowRecord streams into discrete 60-second temporal windows
and computes the exact 17 canonical features with zero data leakage.
"""

from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.flow_normalizer import normalize_flags, normalize_flow
from backend.api.errors import ConflictException

CANONICAL_17_FEATURES = [
    "flow_count",
    "total_packets",
    "total_bytes",
    "avg_packet_rate",
    "avg_byte_rate",
    "unique_sources",
    "unique_destinations",
    "avg_packet_size",
    "avg_flow_duration",
    "syn_flag_count",
    "ack_flag_count",
    "privileged_port_ratio",
    "rolling_5_flow_count",
    "rolling_5_total_packets",
    "rolling_5_total_bytes",
    "rolling_5_avg_byte_rate",
    "rolling_5_unique_sources",
]

class OutOfOrderFlowException(ConflictException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(code="OUT_OF_ORDER_FLOW", message=message, details=details or {})

class WindowAggregator:
    """
    Streaming 60-second temporal window aggregator.
    Accumulates FlowRecord events into deterministic temporal buckets.
    Emits feature vectors when window time elapses or upon explicit flush.
    """

    def __init__(
        self,
        window_size_seconds: int = 60,
        rolling_window_count: int = 5,
    ):
        self.window_size_seconds = window_size_seconds
        self.rolling_window_count = rolling_window_count

        self.current_window_start: Optional[pd.Timestamp] = None
        self.current_window_end: Optional[pd.Timestamp] = None
        self.flows_in_window: List[FlowRecord] = []

        # History of recent base metrics for rolling window calculation
        # Each entry: {flow_count, total_packets, total_bytes, avg_byte_rate, unique_sources}
        self.rolling_history: List[Dict[str, float]] = []
        self.completed_windows_count: int = 0
        self.latest_emitted_timestamp: Optional[str] = None

    def get_window_boundaries(self, dt: pd.Timestamp) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """Calculates deterministic [start, end) boundaries floored to window_size_seconds."""
        start = dt.floor(f"{self.window_size_seconds}s")
        end = start + pd.Timedelta(seconds=self.window_size_seconds)
        return start, end

    def add_flow(
        self, flow: FlowRecord
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, float]]]:
        """
        Ingests a single FlowRecord.
        
        Returns:
            (window_completed: bool, window_timestamp: Optional[str], features: Optional[Dict[str, float]])
            If window_completed is True, returns the emitted 17 canonical features.
        """
        normalized_flow = normalize_flow(flow)
        flow_ts = pd.to_datetime(normalized_flow.timestamp)

        # 1. Initialize first window if uninitialized
        if self.current_window_start is None:
            self.current_window_start, self.current_window_end = self.get_window_boundaries(flow_ts)
            self.flows_in_window = [normalized_flow]
            return False, None, None

        # 2. Check for Out-of-Order records
        if flow_ts < self.current_window_start:
            raise OutOfOrderFlowException(
                message=(
                    f"Flow timestamp '{normalized_flow.timestamp}' precedes active window start "
                    f"'{self.current_window_start.isoformat()}'. Out-of-order flows into completed "
                    f"windows are rejected to prevent retrospective data modification."
                ),
                details={
                    "flow_timestamp": normalized_flow.timestamp,
                    "active_window_start": self.current_window_start.isoformat(),
                },
            )

        # 3. Check if flow falls into the current active window
        if flow_ts < self.current_window_end:
            self.flows_in_window.append(normalized_flow)
            return False, None, None

        # 4. Flow is beyond current window: Emit current window & open new window
        emitted_ts, emitted_features = self._emit_current_window()

        # Advance to new window corresponding to the new flow
        self.current_window_start, self.current_window_end = self.get_window_boundaries(flow_ts)
        self.flows_in_window = [normalized_flow]

        return True, emitted_ts, emitted_features

    def flush(self) -> Tuple[bool, Optional[str], Optional[Dict[str, float]]]:
        """Forces the current active window to emit features immediately if not empty."""
        if not self.flows_in_window or self.current_window_start is None:
            return False, None, None

        emitted_ts, emitted_features = self._emit_current_window()
        # Reset current window after flush
        self.current_window_start = None
        self.current_window_end = None
        self.flows_in_window = []

        return True, emitted_ts, emitted_features

    def _emit_current_window(self) -> Tuple[str, Dict[str, float]]:
        """Aggregates flows in the active window and computes rolling features."""
        window_start_str = self.current_window_start.isoformat()
        features = self.compute_window_features(self.flows_in_window)

        # Update rolling history (last 5 base metrics)
        base_metrics = {
            "flow_count": features["flow_count"],
            "total_packets": features["total_packets"],
            "total_bytes": features["total_bytes"],
            "avg_byte_rate": features["avg_byte_rate"],
            "unique_sources": features["unique_sources"],
        }
        self.rolling_history.append(base_metrics)
        if len(self.rolling_history) > self.rolling_window_count:
            self.rolling_history = self.rolling_history[-self.rolling_window_count:]

        self.completed_windows_count += 1
        self.latest_emitted_timestamp = window_start_str
        return window_start_str, features

    def compute_window_features(self, flows: List[FlowRecord]) -> Dict[str, float]:
        """
        Computes the exact 17 canonical features using Phase 2 semantics.
        Zero division is strictly protected.
        """
        if not flows:
            return {k: 0.0 for k in CANONICAL_17_FEATURES}

        flow_count = float(len(flows))
        total_packets = float(sum(f.packets for f in flows))
        total_bytes = float(sum(f.bytes for f in flows))

        # Per-flow rates & sizing (safe division)
        packet_rates = [
            float(f.packets / f.duration_seconds) if f.duration_seconds > 0 else 0.0
            for f in flows
        ]
        byte_rates = [
            float(f.bytes / f.duration_seconds) if f.duration_seconds > 0 else 0.0
            for f in flows
        ]
        packet_sizes = [
            float(f.bytes / f.packets) if f.packets > 0 else 0.0
            for f in flows
        ]

        avg_packet_rate = float(np.mean(packet_rates))
        avg_byte_rate = float(np.mean(byte_rates))
        avg_packet_size = float(np.mean(packet_sizes))
        avg_flow_duration = float(np.mean([f.duration_seconds for f in flows]))

        # Cardinalities
        unique_sources = float(len(set(f.src_ip for f in flows)))
        unique_destinations = float(len(set(f.dst_ip for f in flows)))

        # Flags: count of flows with SYN and ACK flags
        syn_flags = 0
        ack_flags = 0
        for f in flows:
            s_cnt, a_cnt, _ = normalize_flags(f.tcp_flags)
            syn_flags += s_cnt
            ack_flags += a_cnt

        # Privileged port ratio (< 1024)
        privileged_ports = sum(1.0 for f in flows if f.dst_port < 1024)
        privileged_port_ratio = float(privileged_ports / flow_count) if flow_count > 0 else 0.0

        # Current window base metrics
        current_base = {
            "flow_count": flow_count,
            "total_packets": total_packets,
            "total_bytes": total_bytes,
            "avg_byte_rate": avg_byte_rate,
            "unique_sources": unique_sources,
        }

        # Causal rolling features (including current window + previous up to K-1 windows)
        all_recent = self.rolling_history + [current_base]
        recent_k = all_recent[-self.rolling_window_count:]

        rolling_flow_count = float(np.mean([item["flow_count"] for item in recent_k]))
        rolling_total_packets = float(np.mean([item["total_packets"] for item in recent_k]))
        rolling_total_bytes = float(np.mean([item["total_bytes"] for item in recent_k]))
        rolling_avg_byte_rate = float(np.mean([item["avg_byte_rate"] for item in recent_k]))
        rolling_unique_sources = float(np.mean([item["unique_sources"] for item in recent_k]))

        features: Dict[str, float] = {
            "flow_count": flow_count,
            "total_packets": total_packets,
            "total_bytes": total_bytes,
            "avg_packet_rate": avg_packet_rate,
            "avg_byte_rate": avg_byte_rate,
            "unique_sources": unique_sources,
            "unique_destinations": unique_destinations,
            "avg_packet_size": avg_packet_size,
            "avg_flow_duration": avg_flow_duration,
            "syn_flag_count": float(syn_flags),
            "ack_flag_count": float(ack_flags),
            "privileged_port_ratio": privileged_port_ratio,
            "rolling_5_flow_count": rolling_flow_count,
            "rolling_5_total_packets": rolling_total_packets,
            "rolling_5_total_bytes": rolling_total_bytes,
            "rolling_5_avg_byte_rate": rolling_avg_byte_rate,
            "rolling_5_unique_sources": rolling_unique_sources,
        }

        return features

    def reset(self) -> None:
        """Resets in-memory accumulation buffers and rolling history."""
        self.current_window_start = None
        self.current_window_end = None
        self.flows_in_window = []
        self.rolling_history = []
        self.completed_windows_count = 0
        self.latest_emitted_timestamp = None
