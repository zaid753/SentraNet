"""
SENTRANET — API Health & System Status Tests (Phase 7)
"""

from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sentranet-api"
    assert "version" in data
    assert data["simulation"] is True

def test_api_system_status_endpoint():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "SENTRANET"
    assert data["status"] == "ready"
    assert data["simulation"] is True
    assert data["feature_count"] == 17
    assert data["models"]["xgboost"] == "loaded"
    assert data["models"]["isolation_forest"] == "loaded"
    assert data["pipeline"]["risk_fusion"] == "ready"
    assert data["pipeline"]["forecast_engine"] == "ready"

def test_openapi_availability():
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200

    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    schema = openapi_resp.json()
    assert schema["info"]["title"] == "SENTRANET API"
    assert "0.7.0" in schema["info"]["version"]

def test_cors_headers():
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
