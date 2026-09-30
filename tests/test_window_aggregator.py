"""
SENTRANET — Window Aggregator Unit Tests (Phase 9)
Tests 60-second deterministic temporal boundaries, aggregation calculations,
out-of-order flow rejection, and rolling 5 history.
"""

import pytest
from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.window_aggregator import (
    WindowAggregator,
    OutOfOrderFlowException,
    CANONICAL_17_FEATURES,
)


def make_flow(ts: str, src_ip="10.0.0.1", dst_ip="10.0.0.2", port=80, pkts=10, bytes_val=1000.0, dur=1.0, flags="SYN,ACK"):
    return FlowRecord(
        timestamp=ts,
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=10000,
        dst_port=port,
        protocol="TCP",
        duration_seconds=dur,
        packets=pkts,
        bytes=bytes_val,
        tcp_flags=flags,
    )


def test_window_boundaries():
    aggregator = WindowAggregator(window_size_seconds=60)
    # First flow initializes window [08:42:00, 08:43:00)
    comp, ts, feats = aggregator.add_flow(make_flow("2026-09-30T08:42:15Z"))
    assert not comp
    assert aggregator.current_window_start.strftime("%H:%M:%S") == "08:42:00"
    assert aggregator.current_window_end.strftime("%H:%M:%S") == "08:43:00"

    # Second flow within window
    comp, ts, feats = aggregator.add_flow(make_flow("2026-09-30T08:42:55Z"))
    assert not comp
    assert len(aggregator.flows_in_window) == 2

    # Third flow in next window [08:43:00, 08:44:00) -> triggers emission of first window
    comp, ts, feats = aggregator.add_flow(make_flow("2026-09-30T08:43:05Z"))
    assert comp
    assert ts.startswith("2026-09-30T08:42:00")
    assert feats["flow_count"] == 2.0
    assert feats["total_packets"] == 20.0
    assert feats["total_bytes"] == 2000.0


def test_reject_out_of_order_flow():
    aggregator = WindowAggregator(window_size_seconds=60)
    aggregator.add_flow(make_flow("2026-09-30T08:42:15Z"))
    aggregator.add_flow(make_flow("2026-09-30T08:43:05Z"))  # advances to 08:43:00

    # Flow from 08:41:00 or 08:42:30 (before current window start 08:43:00) must be rejected
    with pytest.raises(OutOfOrderFlowException):
        aggregator.add_flow(make_flow("2026-09-30T08:42:30Z"))


def test_aggregation_calculations():
    aggregator = WindowAggregator(window_size_seconds=60)
    flows = [
        make_flow("2026-09-30T08:42:05Z", src_ip="10.0.0.1", dst_ip="10.0.0.5", port=80, pkts=10, bytes_val=1000.0, dur=1.0, flags="SYN"),
        make_flow("2026-09-30T08:42:25Z", src_ip="10.0.0.2", dst_ip="10.0.0.5", port=443, pkts=20, bytes_val=4000.0, dur=2.0, flags="ACK"),
        make_flow("2026-09-30T08:42:45Z", src_ip="10.0.0.3", dst_ip="10.0.0.6", port=8080, pkts=10, bytes_val=2000.0, dur=1.0, flags="SYN,ACK"),
    ]
    feats = aggregator.compute_window_features(flows)

    assert feats["flow_count"] == 3.0
    assert feats["total_packets"] == 40.0
    assert feats["total_bytes"] == 7000.0
    assert feats["unique_sources"] == 3.0
    assert feats["unique_destinations"] == 2.0
    assert feats["syn_flag_count"] == 2.0
    assert feats["ack_flag_count"] == 2.0
    # Privileged ports: 80 and 443 are < 1024; 8080 is not. Ratio: 2 / 3
    assert abs(feats["privileged_port_ratio"] - (2.0 / 3.0)) < 1e-5

    # Rates:
    # flow 1: 10/1 = 10 pkt/s, 1000 byte/s, 1000/10 = 100 bytes/pkt
    # flow 2: 20/2 = 10 pkt/s, 2000 byte/s, 4000/20 = 200 bytes/pkt
    # flow 3: 10/1 = 10 pkt/s, 2000 byte/s, 2000/10 = 200 bytes/pkt
    assert abs(feats["avg_packet_rate"] - 10.0) < 1e-5
    assert abs(feats["avg_byte_rate"] - ((1000.0 + 2000.0 + 2000.0) / 3.0)) < 1e-5
    assert abs(feats["avg_packet_size"] - ((100.0 + 200.0 + 200.0) / 3.0)) < 1e-5


def test_rolling_5_features():
    aggregator = WindowAggregator(window_size_seconds=60, rolling_window_count=5)

    # Window 0
    aggregator.add_flow(make_flow("2026-09-30T08:00:10Z", pkts=10, bytes_val=100.0))
    # Emit W0 by adding flow in W1
    _, _, f0 = aggregator.add_flow(make_flow("2026-09-30T08:01:10Z", pkts=20, bytes_val=200.0))
    assert f0["rolling_5_flow_count"] == 1.0
    assert f0["rolling_5_total_packets"] == 10.0

    # Emit W1 by adding flow in W2
    _, _, f1 = aggregator.add_flow(make_flow("2026-09-30T08:02:10Z", pkts=30, bytes_val=300.0))
    assert f1["rolling_5_flow_count"] == 1.0
    # Mean of packets in W0 (10) and W1 (20) = 15.0
    assert f1["rolling_5_total_packets"] == 15.0
    assert f1["rolling_5_total_bytes"] == 150.0


def test_reset():
    aggregator = WindowAggregator(window_size_seconds=60)
    aggregator.add_flow(make_flow("2026-09-30T08:00:10Z"))
    assert len(aggregator.flows_in_window) == 1
    aggregator.reset()
    assert aggregator.current_window_start is None
    assert len(aggregator.flows_in_window) == 0
    assert len(aggregator.rolling_history) == 0
