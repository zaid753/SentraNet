"""
SENTRANET — API Incidents Tests (Phase 7)
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
import time

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_service_stream():
    client.post("/api/stream/reset")

def test_incidents_list_empty():
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

def test_incident_not_found():
    resp = client.get("/api/incidents/INC-NONEXISTENT")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_incidents_populated_via_batch_replay():
    # Start batch replay on validation partition
    start_resp = client.post(
        "/api/replay/start",
        json={"mode": "batch", "dataset": "validation"}
    )
    assert start_resp.status_code == 200
    
    time.sleep(1.0) # Wait for persistence to finish

    # Retrieve incidents
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    incidents = resp.json()
    assert len(incidents) > 0

    first_inc = incidents[0]
    assert "incident_id" in first_inc
    assert "attack_class" in first_inc
    assert "severity" in first_inc
    assert "status" in first_inc
    assert "peak_risk" in first_inc

    # Fetch detail of first incident
    inc_id = first_inc["incident_id"]
    detail_resp = client.get(f"/api/incidents/{inc_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["incident_id"] == inc_id
    assert "created_at" in detail
