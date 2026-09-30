"""
SENTRANET — API Alerts Tests (Phase 7)
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

SAMPLE_FEATURES = {
    "flow_count": 1.1870,
    "total_packets": -0.3650,
    "total_bytes": -0.4012,
    "avg_packet_rate": -0.7469,
    "avg_byte_rate": -0.5518,
    "unique_sources": 1.4447,
    "unique_destinations": 1.2823,
    "avg_packet_size": -0.4117,
    "avg_flow_duration": -0.0567,
    "syn_flag_count": -0.1726,
    "ack_flag_count": 1.0638,
    "privileged_port_ratio": 0.0891,
    "rolling_5_flow_count": 0.4933,
    "rolling_5_total_packets": -0.4390,
    "rolling_5_total_bytes": -0.4652,
    "rolling_5_avg_byte_rate": -0.5670,
    "rolling_5_unique_sources": 0.7790,
}

@pytest.fixture(autouse=True)
def reset_service_stream():
    client.post("/api/stream/reset")

def test_current_alert_idle():
    resp = client.get("/api/alerts/current")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active"] is False
    assert data["incident"] is None
    assert data["alert_state"] == "NORMAL"

def test_alerts_history_empty_at_startup():
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_alerts_filtering():
    # Submit telemetry window
    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": SAMPLE_FEATURES
    }
    client.post("/api/analyze", json=payload)

    # Query alerts with limit
    resp = client.get("/api/alerts?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 5
