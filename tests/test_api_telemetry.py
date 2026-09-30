"""
SENTRANET — Telemetry API Integration Tests (Phase 9)
Tests FastAPI telemetry endpoints:
- Ingestion (/api/telemetry/flow)
- Flush (/api/telemetry/flush)
- Status (/api/telemetry/status)
- Synthetic Stream Control (start, pause, resume, stop, status)
- Reset (/api/telemetry/reset) and conflict states (409)
"""

import pytest
import time
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.telemetry.stream_processor import StreamProcessor
from backend.telemetry.synthetic_service import SyntheticStreamService

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_telemetry_state():
    """Ensure clean processor and synthetic service before and after each test."""
    synth = SyntheticStreamService.get_instance()
    try:
        synth.stop()
    except Exception:
        pass
    proc = StreamProcessor.get_instance()
    proc.reset()
    yield
    try:
        synth.stop()
    except Exception:
        pass
    proc.reset()


def test_ingest_single_flow_does_not_run_inference():
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
    resp = client.post("/api/telemetry/flow", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] is True
    assert data["window_complete"] is False
    assert data["flows_in_window"] == 1
    assert data["decision"] is None


def test_ingest_completing_window_triggers_inference():
    # Flow 1 in window 08:42:00
    f1 = {
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
    r1 = client.post("/api/telemetry/flow", json=f1)
    assert r1.status_code == 200
    assert r1.json()["window_complete"] is False

    # Flow 2 in window 08:43:00 -> completes window 08:42:00
    f2 = {
        "timestamp": "2026-09-30T08:43:05Z",
        "src_ip": "10.0.0.11",
        "dst_ip": "10.0.0.20",
        "src_port": 53123,
        "dst_port": 80,
        "protocol": "TCP",
        "duration_seconds": 1.2,
        "packets": 25,
        "bytes": 20000.0,
        "tcp_flags": "ACK",
    }
    r2 = client.post("/api/telemetry/flow", json=f2)
    assert r2.status_code == 200
    data = r2.json()
    assert data["accepted"] is True
    assert data["window_complete"] is True
    assert data["decision"] is not None
    assert "attack_class" in data["decision"]
    assert "risk_score" in data["decision"]


def test_flush_window():
    # Ingest 1 flow
    client.post("/api/telemetry/flow", json={
        "timestamp": "2026-09-30T08:42:10Z",
        "src_ip": "10.0.0.10",
        "dst_ip": "10.0.0.20",
        "src_port": 53122,
        "dst_port": 443,
        "protocol": "TCP",
        "duration_seconds": 0.5,
        "packets": 10,
        "bytes": 5000.0,
    })

    # Flush
    resp = client.post("/api/telemetry/flush")
    assert resp.status_code == 200
    data = resp.json()
    assert data["flushed"] is True
    assert data["features"]["flow_count"] == 1.0
    assert data["decision"] is not None
    assert "risk_score" in data["decision"]


def test_telemetry_status():
    resp = client.get("/api/telemetry/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "active" in data
    assert "source_type" in data
    assert "windows_processed" in data


def test_synthetic_stream_lifecycle_and_conflicts():
    # 1. Start
    start_resp = client.post("/api/telemetry/synthetic/start", json={
        "speed": 50.0,
        "seed": 42,
        "profile": "scenario_1",
    })
    assert start_resp.status_code == 200
    assert start_resp.json()["running"] is True
    assert start_resp.json()["status"] == "running"

    # 2. Duplicate start -> 409 Conflict
    dup_resp = client.post("/api/telemetry/synthetic/start", json={"speed": 50.0})
    assert dup_resp.status_code == 409

    # 3. Check status while running
    time.sleep(0.1)
    status_resp = client.get("/api/telemetry/synthetic/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["running"] is True

    # 4. Reset while running -> 409 Conflict
    reset_conflict = client.post("/api/telemetry/reset")
    assert reset_conflict.status_code == 409

    # 5. Pause
    pause_resp = client.post("/api/telemetry/synthetic/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    # 6. Resume
    resume_resp = client.post("/api/telemetry/synthetic/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "running"

    # 7. Stop
    stop_resp = client.post("/api/telemetry/synthetic/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "stopped"

    # 8. Stop when already stopped -> 409 Conflict
    dup_stop = client.post("/api/telemetry/synthetic/stop")
    assert dup_stop.status_code == 409

    # 9. Reset when stopped -> 200 Success
    reset_resp = client.post("/api/telemetry/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"
