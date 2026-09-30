"""
SENTRANET — API Inference & Stream Tests (Phase 7)
"""

import math
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

def test_current_risk_no_state():
    resp = client.get("/api/risk/current")
    assert resp.status_code == 404
    data = resp.json()
    assert data["error"]["code"] == "NO_CURRENT_STATE"

def test_analyze_valid_request():
    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": SAMPLE_FEATURES
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["timestamp"] == "2026-09-30T10:00:00"
    assert "attack_class" in data
    assert "risk_score" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert "anomaly_score" in data
    assert 0.0 <= data["anomaly_score"] <= 1.0
    assert data["alert_state"] in ["NORMAL", "WATCH", "ALERT", "RESOLVED"]
    assert data["simulation"] is True

    # Current risk endpoint should now return 200
    curr_resp = client.get("/api/risk/current")
    assert curr_resp.status_code == 200
    curr_data = curr_resp.json()
    assert curr_data["timestamp"] == "2026-09-30T10:00:00"
    assert curr_data["risk_score"] == data["risk_score"]

def test_analyze_duplicate_timestamp_rejection():
    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": SAMPLE_FEATURES
    }
    resp1 = client.post("/api/analyze", json=payload)
    assert resp1.status_code == 200

    resp2 = client.post("/api/analyze", json=payload)
    assert resp2.status_code == 409
    data = resp2.json()
    assert data["error"]["code"] == "DUPLICATE_TIMESTAMP"

def test_analyze_out_of_order_timestamp_rejection():
    payload1 = {
        "timestamp": "2026-09-30T10:02:00",
        "features": SAMPLE_FEATURES
    }
    resp1 = client.post("/api/analyze", json=payload1)
    assert resp1.status_code == 200

    payload2 = {
        "timestamp": "2026-09-30T10:01:00",
        "features": SAMPLE_FEATURES
    }
    resp2 = client.post("/api/analyze", json=payload2)
    assert resp2.status_code == 409
    data = resp2.json()
    assert data["error"]["code"] == "OUT_OF_ORDER_TIMESTAMP"

def test_analyze_rejects_nan_features():
    import json
    bad_features = dict(SAMPLE_FEATURES)
    bad_features["flow_count"] = float("nan")

    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": bad_features
    }
    raw = json.dumps(payload, allow_nan=True)
    resp = client.post("/api/analyze", content=raw, headers={"Content-Type": "application/json"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_analyze_rejects_inf_features():
    import json
    bad_features = dict(SAMPLE_FEATURES)
    bad_features["total_bytes"] = float("inf")

    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": bad_features
    }
    raw = json.dumps(payload, allow_nan=True)
    resp = client.post("/api/analyze", content=raw, headers={"Content-Type": "application/json"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_analyze_rejects_missing_feature():
    bad_features = dict(SAMPLE_FEATURES)
    del bad_features["rolling_5_avg_byte_rate"]

    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": bad_features
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_analyze_rejects_extra_features():
    bad_features = dict(SAMPLE_FEATURES)
    bad_features["unauthorized_column"] = 42.0

    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": bad_features
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_feature_ordering_safety():
    # Pass reversed dictionary keys
    reversed_features = {k: SAMPLE_FEATURES[k] for k in reversed(list(SAMPLE_FEATURES.keys()))}

    payload = {
        "timestamp": "2026-09-30T10:00:00",
        "features": reversed_features
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["attack_class"] is not None
