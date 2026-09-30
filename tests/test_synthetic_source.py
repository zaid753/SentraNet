"""
SENTRANET — Synthetic Flow Source Tests (Phase 9)
Tests deterministic pseudo-random flow generation, seed reproducibility,
profile behavioral characteristics, and source tagging.
"""

import pytest
from backend.telemetry.synthetic_source import SyntheticFlowSource
from backend.telemetry.flow_sources import LiveFlowSource


def test_synthetic_source_type_and_determinism():
    gen1 = SyntheticFlowSource(seed=42, profile="scenario_1")
    assert gen1.source_type == "synthetic"

    gen2 = SyntheticFlowSource(seed=42, profile="scenario_1")
    assert gen2.source_type == "synthetic"

    # Same seed must produce identical flow sequence
    flows1 = [gen1.read() for _ in range(20)]
    flows2 = [gen2.read() for _ in range(20)]

    for f1, f2 in zip(flows1, flows2):
        assert f1.timestamp == f2.timestamp
        assert f1.src_ip == f2.src_ip
        assert f1.dst_ip == f2.dst_ip
        assert f1.src_port == f2.src_port
        assert f1.dst_port == f2.dst_port
        assert f1.protocol == f2.protocol
        assert f1.packets == f2.packets
        assert f1.bytes == f2.bytes
        assert f1.tcp_flags == f2.tcp_flags


def test_synthetic_different_seed_produces_variance():
    gen1 = SyntheticFlowSource(seed=42, profile="BASELINE")
    gen2 = SyntheticFlowSource(seed=999, profile="BASELINE")

    flows1 = [gen1.read() for _ in range(20)]
    flows2 = [gen2.read() for _ in range(20)]

    # At least some ports/IPs/timestamps must differ
    different_ports = any(f1.src_port != f2.src_port for f1, f2 in zip(flows1, flows2))
    assert different_ports


def test_profiles_metadata_validity():
    for prof in ["BASELINE", "SCANNING", "DDOS", "BOTNET"]:
        gen = SyntheticFlowSource(seed=123, profile=prof)
        for _ in range(10):
            flow = gen.read()
            assert flow.duration_seconds >= 0.0
            assert flow.packets > 0
            assert flow.bytes > 0.0
            assert 0 <= flow.src_port <= 65535
            assert 0 <= flow.dst_port <= 65535
            assert flow.protocol in ["TCP", "UDP", "ICMP", "OTHER"]


def test_live_source_placeholder_behavior():
    live = LiveFlowSource()
    assert live.source_type == "live"
    with pytest.raises(NotImplementedError) as exc_info:
        live.read()
    assert "Live telemetry source not configured" in str(exc_info.value)
