from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "ok"]
    assert data["service"] in ["sentranet-backend", "sentranet-api"]
    assert "version" in data

def test_get_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data
    assert data["backend"]["status"] == "online"
    assert data["ml_models"]["status"] in ["loaded", "not_loaded"]

