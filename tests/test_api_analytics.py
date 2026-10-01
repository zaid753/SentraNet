import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
import time

client = TestClient(app)

def test_analytics_overview():
    # 1. Reset
    client.post("/api/stream/reset")
    
    # 2. Replay
    client.post(
        "/api/replay/start",
        json={"mode": "batch", "dataset": "validation"}
    )
    
    # Wait for EventBus to persist
    time.sleep(1.0)
    
    # 3. Check Analytics
    resp = client.get("/api/analytics/overview?time_range=all")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["total_incidents"] >= 0
    assert data["total_alerts"] >= 0
    assert "threat_distribution" in data
    assert isinstance(data["threat_distribution"], dict)
    
    # Verify arrays exist
    assert isinstance(data["incident_trend"], list)
    assert isinstance(data["alert_trend"], list)
    assert isinstance(data["risk_trend"], list)

def test_system_health():
    resp = client.get("/api/system/health")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["status"] in ["Operational", "Degraded"]
    assert data["api"] == "Operational"
    assert data["database"] == "Operational"
    
    # ML components
    assert "xgboost" in data
    assert "isolation_forest" in data
    assert "forecast_engine" in data
    
    assert data["xgboost"]["status"] in ["Available", "Unavailable", "Unknown"]
