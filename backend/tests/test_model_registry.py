import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.services.sentranet_service import SentranetService

client = TestClient(app)

def test_registry_loading():
    # Verify baseline model loading
    response = client.get("/api/models/")
    assert response.status_code == 200
    models = response.json()
    assert len(models) == 2
    ids = [m["model_id"] for m in models]
    assert "sentranet_synthetic_v1" in ids
    assert "sentranet_cicids2017_v1" in ids

def test_active_model_default():
    # Should default to synthetic
    response = client.get("/api/models/active")
    assert response.status_code == 200
    assert response.json()["model_id"] == "sentranet_synthetic_v1"

def test_model_selection():
    # Switch to experimental
    response = client.post("/api/models/active", json={"model_id": "sentranet_cicids2017_v1"})
    assert response.status_code == 200
    
    response = client.get("/api/models/active")
    assert response.json()["model_id"] == "sentranet_cicids2017_v1"
    
    # Switch back
    response = client.post("/api/models/active", json={"model_id": "sentranet_synthetic_v1"})
    assert response.status_code == 200

def test_invalid_model_handling():
    # Try invalid model
    response = client.post("/api/models/active", json={"model_id": "invalid_model_123"})
    assert response.status_code == 404
    
    # Verify we stayed on baseline
    response = client.get("/api/models/active")
    assert response.json()["model_id"] == "sentranet_synthetic_v1"
