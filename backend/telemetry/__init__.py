"""
SENTRANET — Telemetry Ingestion and Feature Aggregation Layer (Phase 9)
Provides real-time flow ingestion, validation, normalization, 60-second windowing,
and canonical 17-feature aggregation feeding the SENTRANET AI Core.
"""

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.flow_validator import validate_flow_record, InvalidFlowException
from backend.telemetry.flow_normalizer import (
    normalize_flow,
    normalize_protocol,
    normalize_flags,
    normalize_timestamp_str,
)
from backend.telemetry.window_aggregator import (
    WindowAggregator,
    OutOfOrderFlowException,
    CANONICAL_17_FEATURES,
)
from backend.telemetry.ai_adapter import (
    AIAdapter,
    InvalidFeatureVectorException,
)
from backend.telemetry.flow_sources import (
    FlowSource,
    FileFlowSource,
    ReplayFlowSource,
    LiveFlowSource,
)
from backend.telemetry.synthetic_source import (
    SyntheticFlowSource,
    VALID_PROFILES,
)
from backend.telemetry.stream_processor import StreamProcessor
from backend.telemetry.synthetic_service import SyntheticStreamService

__all__ = [
    "FlowRecord",
    "validate_flow_record",
    "InvalidFlowException",
    "normalize_flow",
    "normalize_protocol",
    "normalize_flags",
    "normalize_timestamp_str",
    "WindowAggregator",
    "OutOfOrderFlowException",
    "CANONICAL_17_FEATURES",
    "AIAdapter",
    "InvalidFeatureVectorException",
    "FlowSource",
    "FileFlowSource",
    "ReplayFlowSource",
    "LiveFlowSource",
    "SyntheticFlowSource",
    "VALID_PROFILES",
    "StreamProcessor",
    "SyntheticStreamService",
]
