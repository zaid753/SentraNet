"""
SENTRANET — Flow Schema and Validation Unit Tests (Phase 9)
Tests strict Pydantic validation, boundary checks, and normalization for FlowRecord.
"""

import pytest
import math
from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.flow_validator import validate_flow_record, InvalidFlowException
from backend.telemetry.flow_normalizer import (
    normalize_flow,
    normalize_protocol,
    normalize_flags,
    normalize_timestamp_str,
)


def test_valid_flow_record():
    payload = {
        "timestamp": "2026-09-30T08:42:10Z",
        "src_ip": "10.0.0.10",
        "dst_ip": "10.0.0.20",
        "src_port": 53122,
        "dst_port": 443,
        "protocol": "TCP",
        "duration_seconds": 0.84,
        "packets": 18,
        "bytes": 14200.0,
        "tcp_flags": "SYN,ACK",
    }
    record = validate_flow_record(payload)
    assert record.src_ip == "10.0.0.10"
    assert record.dst_port == 443
    assert record.packets == 18
    assert record.bytes == 14200.0


def test_reject_invalid_src_ip():
    payload = {
        "timestamp": "2026-09-30T08:42:10Z",
        "src_ip": "999.999.999.999",
        "dst_ip": "10.0.0.20",
        "src_port": 1234,
        "dst_port": 80,
        "duration_seconds": 1.0,
        "packets": 5,
        "bytes": 500.0,
    }
    with pytest.raises(InvalidFlowException):
        validate_flow_record(payload)


def test_reject_invalid_port_range():
    # Negative port
    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": -1,
            "dst_port": 80,
            "duration_seconds": 1.0,
            "packets": 5,
            "bytes": 500.0,
        })

    # Port > 65535
    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 80,
            "dst_port": 70000,
            "duration_seconds": 1.0,
            "packets": 5,
            "bytes": 500.0,
        })


def test_reject_negative_packets_and_bytes():
    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 80,
            "dst_port": 443,
            "duration_seconds": 1.0,
            "packets": -5,
            "bytes": 500.0,
        })

    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 80,
            "dst_port": 443,
            "duration_seconds": 1.0,
            "packets": 5,
            "bytes": -50.0,
        })


def test_reject_negative_duration():
    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 80,
            "dst_port": 443,
            "duration_seconds": -0.5,
            "packets": 5,
            "bytes": 50.0,
        })


def test_reject_nan_and_inf():
    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 80,
            "dst_port": 443,
            "duration_seconds": float("nan"),
            "packets": 5,
            "bytes": 50.0,
        })

    with pytest.raises(InvalidFlowException):
        validate_flow_record({
            "timestamp": "2026-09-30T08:42:10Z",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 80,
            "dst_port": 443,
            "duration_seconds": float("inf"),
            "packets": 5,
            "bytes": 50.0,
        })


def test_protocol_normalization():
    assert normalize_protocol("tcp") == "TCP"
    assert normalize_protocol("TCP") == "TCP"
    assert normalize_protocol("Tcp") == "TCP"
    assert normalize_protocol("udp") == "UDP"
    assert normalize_protocol("UDP") == "UDP"
    assert normalize_protocol("icmp") == "ICMP"
    assert normalize_protocol("gre") == "OTHER"
    assert normalize_protocol("") == "OTHER"


def test_tcp_flag_normalization():
    # String tokens
    syn, ack, flags_str = normalize_flags("SYN,ACK")
    assert syn == 1
    assert ack == 1
    assert "SYN" in flags_str and "ACK" in flags_str

    # Only SYN
    syn, ack, _ = normalize_flags("SYN")
    assert syn == 1
    assert ack == 0

    # Bitmask integer: 0x02 = SYN, 0x10 = ACK, 0x12 = SYN+ACK
    syn, ack, flags_str = normalize_flags(0x12)
    assert syn == 1
    assert ack == 1
    assert "SYN" in flags_str and "ACK" in flags_str

    # None
    syn, ack, flags_str = normalize_flags(None)
    assert syn == 0
    assert ack == 0
    assert flags_str == ""


def test_timestamp_normalization():
    ts = normalize_timestamp_str("2026-09-30 08:42:10")
    assert ts == "2026-09-30T08:42:10"
    ts_iso = normalize_timestamp_str("2026-09-30T08:42:10Z")
    assert ts_iso == "2026-09-30T08:42:10Z"
