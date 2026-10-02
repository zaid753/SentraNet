import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.services.live_service import LiveService
from backend.telemetry.flow_sources import LiveFlowSource
from unittest.mock import patch, MagicMock

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_live_service():
    # Reset before each test
    svc = LiveService.get_instance()
    svc.stop()
    svc.packet_count = 0
    svc.flow_count = 0
    svc.start_time = None
    svc.last_packet_time = None
    svc.live_source = None
    yield
    svc.stop()

def test_get_interfaces():
    with patch("backend.api.services.live_service.LiveService.get_interfaces", return_value=[{"name": "en0", "description": "Interface en0"}]):
        response = client.get("/api/telemetry/interfaces")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "en0"

def test_live_status_initial():
    response = client.get("/api/telemetry/live/status")
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "STOPPED"
    assert data["packet_count"] == 0
    assert data["flow_count"] == 0

def test_start_and_stop_live_capture():
    # Mock scapy sniff so we don't actually capture
    with patch("scapy.all.sniff") as mock_sniff:
        # Start
        response = client.post("/api/telemetry/live/start", json={"interface": "lo0"})
        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "STARTING" or data["state"] == "RUNNING"
        
        # Already running
        response2 = client.post("/api/telemetry/live/start", json={"interface": "lo0"})
        assert response2.status_code == 200
        
        # Stop
        stop_response = client.post("/api/telemetry/live/stop")
        assert stop_response.status_code == 200
        stop_data = stop_response.json()
        assert stop_data["state"] == "STOPPED"

def test_stop_while_stopped():
    stop_response = client.post("/api/telemetry/live/stop")
    assert stop_response.status_code == 200
    assert stop_response.json()["state"] == "STOPPED"

def test_start_permission_denied():
    def mock_sniff(*args, **kwargs):
        raise PermissionError("Permission denied")
        
    with patch("scapy.all.sniff", mock_sniff):
        response = client.post("/api/telemetry/live/start", json={"interface": "lo0"})
        assert response.status_code == 200
        
        # Wait a tiny bit for the thread to fail
        import time
        time.sleep(0.5)
        
        status_resp = client.get("/api/telemetry/live/status")
        status_data = status_resp.json()
        assert status_data["state"] == "PERMISSION_DENIED"
        assert "LIVE NETWORK UNAVAILABLE: PACKET CAPTURE PERMISSION REQUIRED" in status_data["error_message"]

def test_start_scapy_import_error():
    # If scapy isn't installed
    with patch.dict("sys.modules", {"scapy.all": None}):
        response = client.post("/api/telemetry/live/start", json={"interface": "lo0"})
        import time
        time.sleep(0.2)
        status_resp = client.get("/api/telemetry/live/status")
        assert status_resp.json()["state"] == "ERROR"

def test_no_synthetic_fallback():
    # Make sure we don't start synthetic if live fails
    def mock_sniff(*args, **kwargs):
        raise PermissionError("Permission denied")
        
    with patch("scapy.all.sniff", mock_sniff):
        client.post("/api/telemetry/live/start", json={"interface": "lo0"})
        
        # Wait for failure
        import time
        time.sleep(0.5)
        
        # Check synthetic stream status
        synth_resp = client.get("/api/telemetry/synthetic/status")
        assert synth_resp.status_code == 200
        assert synth_resp.json()["running"] is False
        assert synth_resp.json()["status"] == "idle"

def test_conflict_with_synthetic():
    # Start synthetic
    client.post("/api/telemetry/synthetic/start", json={"speed": 10.0, "profile": "scenario_1"})
    
    # Try start live
    live_resp = client.post("/api/telemetry/live/start", json={"interface": "lo0"})
    assert live_resp.status_code == 409
    assert live_resp.json()["error"]["code"] == "SYNTHETIC_RUNNING"
    
    # Cleanup
    client.post("/api/telemetry/synthetic/stop")
