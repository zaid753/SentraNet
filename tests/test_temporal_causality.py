"""
SENTRANET — Temporal Causality and Data Leakage Tests (Phase 9)
Verifies strict temporal causality:
- Window t calculations reference only past and present records (<= t).
- Decision at t1 does not change when future window t2 is processed.
"""

import pytest
import copy
from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.stream_processor import StreamProcessor


def make_flow(ts: str, pkts: int = 10, bytes_val: float = 1000.0, port: int = 80):
    return FlowRecord(
        timestamp=ts,
        src_ip="192.168.1.100",
        dst_ip="10.0.0.50",
        src_port=54321,
        dst_port=port,
        protocol="TCP",
        duration_seconds=1.0,
        packets=pkts,
        bytes=bytes_val,
        tcp_flags="SYN,ACK",
    )


def test_temporal_causality_and_no_future_leakage():
    """
    Processes windows t0, t1, t2 sequentially.
    Captures features and AI decision at t1.
    Processes t2.
    Asserts decision(t1) is immutable and unaffected by t2.
    """
    processor = StreamProcessor()
    processor.reset()

    # Window 0: 08:00:00 to 08:01:00
    processor.ingest_flow(make_flow("2026-09-30T08:00:10Z", pkts=5, bytes_val=500.0))
    res0 = processor.ingest_flow(make_flow("2026-09-30T08:01:10Z", pkts=10, bytes_val=1000.0))
    assert res0["window_complete"]
    w0_feats = copy.deepcopy(res0["features"])
    w0_decision = copy.deepcopy(res0["decision"])

    # Window 1: 08:01:00 to 08:02:00
    res1 = processor.ingest_flow(make_flow("2026-09-30T08:02:10Z", pkts=20, bytes_val=2000.0))
    assert res1["window_complete"]
    w1_feats = copy.deepcopy(res1["features"])
    w1_decision = copy.deepcopy(res1["decision"])

    # Window 2: 08:02:00 to 08:03:00 (Heavy spike / future activity)
    res2 = processor.ingest_flow(make_flow("2026-09-30T08:03:10Z", pkts=2000, bytes_val=500000.0, port=22))
    assert res2["window_complete"]

    # Verify w1 historical features and decision are unchanged
    # Historical stored windows in processor:
    recorded_w0 = processor.recent_windows[0]
    recorded_w1 = processor.recent_windows[1]

    # Features at t0 and t1 must be identical to what was emitted originally
    assert recorded_w0["features"] == w0_feats
    assert recorded_w1["features"] == w1_feats

    # AI decision at t0 and t1 must remain immutable
    assert recorded_w0["decision"]["attack_class"] == w0_decision["attack_class"]
    assert recorded_w0["decision"]["risk_score"] == w0_decision["risk_score"]

    assert recorded_w1["decision"]["attack_class"] == w1_decision["attack_class"]
    assert recorded_w1["decision"]["risk_score"] == w1_decision["risk_score"]
    assert recorded_w1["decision"]["anomaly_score"] == w1_decision["anomaly_score"]
