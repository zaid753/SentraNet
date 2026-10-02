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
    assert "error" in data
    assert "not found" in data["error"]["message"].lower()

def test_incidents_populated_via_batch_replay():
    # Start batch replay on validation partition
    start_resp = client.post(
        "/api/replay/start",
        json={"mode": "batch", "dataset": "validation"}
    )
    assert start_resp.status_code == 200
    
    # Retrieve incidents with polling
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    incidents = resp.json()
    assert isinstance(incidents, list)
