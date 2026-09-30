"""
SENTRANET — End-to-End API Causality & Stream Progression Test (Phase 7)
Critical Integration Test verifying chronological temporal telemetry processing,
risk evolution, alert deduplication, and incident lifecycle via HTTP APIs.
"""

import pandas as pd
from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

def test_end_to_end_chronological_stream_integration():
    # 1. Reset temporal stream to clean slate
    reset_resp = client.post("/api/stream/reset")
    assert reset_resp.status_code == 200

    # Ensure current risk is empty
    empty_risk = client.get("/api/risk/current")
    assert empty_risk.status_code == 404

    # 2. Load historical telemetry features without labels
    df = pd.read_parquet("data/processed/sample/validation.parquet")
    ts_col = "window_start" if "window_start" in df.columns else "timestamp"
    df_sorted = df.sort_values(ts_col).reset_index(drop=True)

    feature_cols = [
        "flow_count", "total_packets", "total_bytes", "avg_packet_rate", "avg_byte_rate",
        "unique_sources", "unique_destinations", "avg_packet_size", "avg_flow_duration",
        "syn_flag_count", "ack_flag_count", "privileged_port_ratio", "rolling_5_flow_count",
        "rolling_5_total_packets", "rolling_5_total_bytes", "rolling_5_avg_byte_rate",
        "rolling_5_unique_sources"
    ]

    # Process first 20 chronological windows sequentially
    num_windows = min(20, len(df_sorted))
    seen_incidents = set()

    for idx in range(num_windows):
        row = df_sorted.iloc[idx]
        ts = str(row[ts_col])
        features_payload = {f: float(row[f]) for f in feature_cols}

        # Submit window strictly with features only (NO label passed)
        req_payload = {
            "timestamp": ts,
            "features": features_payload
        }

        resp = client.post("/api/analyze", json=req_payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["timestamp"] == ts
        assert "risk_score" in data
        assert 0.0 <= data["risk_score"] <= 1.0
        assert data["attack_class"] is not None
        assert data["alert_state"] in ["NORMAL", "WATCH", "ALERT", "RESOLVED"]

        if data.get("incident_id"):
            seen_incidents.add(data["incident_id"])

    # 3. Verify timeline growth
    timeline_resp = client.get(f"/api/timeline?limit={num_windows + 10}")
    assert timeline_resp.status_code == 200
    timeline_data = timeline_resp.json()
    assert timeline_data["total_points"] == num_windows

    # Verify chronological order in timeline points
    points = timeline_data["points"]
    for i in range(1, len(points)):
        assert points[i]["timestamp"] >= points[i - 1]["timestamp"]

    # 4. Verify current risk state matches the 20th window
    current_risk_resp = client.get("/api/risk/current")
    assert current_risk_resp.status_code == 200
    assert current_risk_resp.json()["timestamp"] == str(df_sorted.iloc[num_windows - 1][ts_col])

    # 5. Verify incident manager consistency
    incidents_resp = client.get("/api/incidents")
    assert incidents_resp.status_code == 200
    all_incidents = incidents_resp.json()

    reported_ids = {inc["incident_id"] for inc in all_incidents}
    # All incident IDs emitted during analyze must be tracked in IncidentManager
    for inc_id in seen_incidents:
        assert inc_id in reported_ids
