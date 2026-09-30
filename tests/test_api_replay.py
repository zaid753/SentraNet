"""
SENTRANET — API Replay Service Tests (Phase 7)
"""

import time
import pytest
from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_replay_state():
    client.post("/api/replay/stop")
    client.post("/api/stream/reset")
    yield
    client.post("/api/replay/stop")
    client.post("/api/stream/reset")

def test_replay_idle_status():
    resp = client.get("/api/replay/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["running"] is False
    assert data["paused"] is False
    assert data["progress"] == 0.0

def test_replay_batch_execution():
    resp = client.post(
        "/api/replay/start",
        json={"mode": "batch", "dataset": "validation"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"

    status_resp = client.get("/api/replay/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["running"] is False
    assert status_data["windows_processed"] > 0
    assert status_data["progress"] == 1.0

def test_replay_realtime_lifecycle():
    # Start realtime at high speed (1000x for instant tests)
    start_resp = client.post(
        "/api/replay/start",
        json={"mode": "realtime", "speed": 1000.0, "dataset": "validation"}
    )
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "started"

    # Concurrency test: starting another replay must return 409
    dup_resp = client.post(
        "/api/replay/start",
        json={"mode": "batch", "dataset": "validation"}
    )
    assert dup_resp.status_code == 409
    assert dup_resp.json()["error"]["code"] == "REPLAY_ALREADY_RUNNING"

    # Reset stream while replay active should return 409
    reset_resp = client.post("/api/stream/reset")
    assert reset_resp.status_code == 409
    assert reset_resp.json()["error"]["code"] == "STREAM_REPLAY_ACTIVE"

    # Pause
    pause_resp = client.post("/api/replay/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    # Resume
    resume_resp = client.post("/api/replay/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "resumed"

    # Stop
    stop_resp = client.post("/api/replay/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "stopped"

    # Verify status is now not running
    status_resp = client.get("/api/replay/status")
    assert status_resp.json()["running"] is False

def test_replay_step_execution():
    step_resp = client.post("/api/replay/step")
    assert step_resp.status_code == 200
    data = step_resp.json()
    assert data["status"] == "stepped"
    assert data["details"]["windows_processed"] == 1

def test_replay_events_endpoint():
    # Run batch on validation
    client.post("/api/replay/start", json={"mode": "batch", "dataset": "validation"})

    resp = client.get("/api/replay/events?limit=10")
    assert resp.status_code == 200
    events = resp.json()
    assert isinstance(events, list)
    assert len(events) <= 10
    if events:
        assert "timestamp" in events[0]
        assert "risk_score" in events[0]
