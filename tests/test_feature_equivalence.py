"""
SENTRANET — Streaming vs Offline Feature Equivalence Test (Phase 9)
MANDATORY TEST: Proves that the new streaming WindowAggregator produces
the exact same 17 canonical features as the Phase 2 offline preprocessing pipeline
(TemporalWindowAggregator + FeatureEngineer) for the same sequence of flow records.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.window_aggregator import WindowAggregator, CANONICAL_17_FEATURES
from ml.preprocessing.features import FeatureEngineer
from ml.preprocessing.windowing import TemporalWindowAggregator


def test_offline_streaming_feature_equivalence():
    """
    Feeds an identical sequence of flow records to:
    1. Offline preprocessing (FeatureEngineer -> TemporalWindowAggregator)
    2. Streaming telemetry aggregator (WindowAggregator)
    Validates that all 17 canonical features match within floating-point tolerance.
    """
    base_time = pd.Timestamp("2026-09-30 08:00:00")
    raw_flows = []
    flow_records = []

    # Create 6 distinct 60-second windows with diverse flow characteristics
    # Windows: 08:00, 08:01, 08:02, 08:03, 08:04, 08:05
    for minute in range(6):
        window_start = base_time + pd.Timedelta(minutes=minute)
        # 4 flows per window
        for f_idx in range(4):
            flow_ts = window_start + pd.Timedelta(seconds=5 + f_idx * 12)
            src_ip = f"192.168.1.{10 + f_idx}"
            dst_ip = f"10.0.0.{20 + (f_idx % 2)}"
            src_port = 50000 + f_idx
            dst_port = 80 if f_idx < 2 else 8080  # 2 privileged, 2 unprivileged
            duration = float(0.5 + f_idx * 0.25)
            packets = int(10 + f_idx * 5)
            bytes_val = float(packets * (100 + f_idx * 50))
            syn = 1 if f_idx in [0, 2] else 0
            ack = 1 if f_idx in [1, 2] else 0
            flags = []
            if syn:
                flags.append("SYN")
            if ack:
                flags.append("ACK")
            flag_str = ",".join(flags) if flags else None

            # Raw flow for offline pipeline
            raw_flows.append({
                "timestamp": flow_ts,
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "source_port": src_port,
                "destination_port": dst_port,
                "protocol": "TCP",
                "flow_duration": duration,
                "forward_packet_count": packets // 2,
                "backward_packet_count": packets - (packets // 2),
                "forward_bytes": bytes_val / 2.0,
                "backward_bytes": bytes_val / 2.0,
                "syn_flag_count": syn,
                "ack_flag_count": ack,
                "label": "BENIGN",
            })

            # FlowRecord for streaming aggregator
            flow_records.append(
                FlowRecord(
                    timestamp=flow_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    src_port=src_port,
                    dst_port=dst_port,
                    protocol="TCP",
                    duration_seconds=duration,
                    packets=packets,
                    bytes=bytes_val,
                    tcp_flags=flag_str,
                )
            )

    # -------------------------------------------------------------
    # 1. OFFLINE PIPELINE EXECUTION
    # -------------------------------------------------------------
    raw_df = pd.DataFrame(raw_flows)
    engineer = FeatureEngineer()
    engineered_df, _ = engineer.engineer_features(raw_df)
    offline_aggregator = TemporalWindowAggregator(window_size_seconds=60, rolling_window_count=5)
    offline_window_df = offline_aggregator.aggregate_windows(engineered_df)

    assert len(offline_window_df) == 6, f"Expected 6 windows, got {len(offline_window_df)}"

    # -------------------------------------------------------------
    # 2. STREAMING AGGREGATOR EXECUTION
    # -------------------------------------------------------------
    streaming_aggregator = WindowAggregator(window_size_seconds=60, rolling_window_count=5)
    streaming_windows = []

    for flow in flow_records:
        comp, win_ts, feats = streaming_aggregator.add_flow(flow)
        if comp and feats:
            streaming_windows.append((win_ts, feats))

    # Flush final partial/active window
    comp, win_ts, feats = streaming_aggregator.flush()
    if comp and feats:
        streaming_windows.append((win_ts, feats))

    assert len(streaming_windows) == 6, f"Expected 6 streaming windows, got {len(streaming_windows)}"

    # -------------------------------------------------------------
    # 3. STATISTICAL & EQUIVALENCE VALIDATION ACROSS ALL 17 FEATURES
    # -------------------------------------------------------------
    for i in range(6):
        offline_row = offline_window_df.iloc[i]
        stream_ts, stream_feats = streaming_windows[i]

        for feature in CANONICAL_17_FEATURES:
            offline_val = float(offline_row[feature])
            stream_val = float(stream_feats[feature])

            # Check floating-point equivalence within 1e-4 tolerance
            diff = abs(offline_val - stream_val)
            assert diff < 1e-4, (
                f"Feature equivalence mismatch on window {i} for feature '{feature}': "
                f"Offline={offline_val}, Streaming={stream_val}, diff={diff}"
            )
