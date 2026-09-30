"""
SENTRANET — Phase 5 Risk Trajectory Unit Tests
Verifies temporal causality, derivative calculations, and trend classification.
"""

import pytest
import datetime
from ml.risk.risk_trajectory import RiskTrajectoryTracker

def test_initial_window_derivatives():
    tracker = RiskTrajectoryTracker()
    res = tracker.update(
        timestamp="2026-09-30T08:00:00",
        risk_score=0.10,
        predicted_class="BENIGN",
        classification_confidence=0.95,
        anomaly_score=0.05,
        is_anomalous=False
    )
    # First window must have zero delta, velocity, and acceleration
    assert res["risk_delta"] == 0.0
    assert res["risk_velocity"] == 0.0
    assert res["risk_acceleration"] == 0.0
    assert res["risk_trend"] == "STABLE"

def test_causal_velocity_and_acceleration():
    tracker = RiskTrajectoryTracker()

    # T0: 08:00
    tracker.update("2026-09-30T08:00:00", 0.10, "BENIGN", 0.95, 0.05, False)

    # T1: 08:01 (1 min later, risk increases by +0.05 -> velocity = +0.05/min)
    t1 = tracker.update("2026-09-30T08:01:00", 0.15, "BENIGN", 0.90, 0.10, False)
    assert abs(t1["risk_delta"] - 0.05) < 1e-4
    assert abs(t1["risk_velocity"] - 0.05) < 1e-4
    assert abs(t1["risk_acceleration"] - 0.05) < 1e-4

    # T2: 08:02 (1 min later, risk increases by +0.10 -> velocity = +0.10/min, acceleration = +0.05/min^2)
    t2 = tracker.update("2026-09-30T08:02:00", 0.25, "SCANNING", 0.80, 0.30, False)
    assert abs(t2["risk_velocity"] - 0.10) < 1e-4
    assert abs(t2["risk_acceleration"] - 0.05) < 1e-4
    assert t2["risk_trend"] == "RAPIDLY_RISING"

def test_falling_trend_classification():
    tracker = RiskTrajectoryTracker()
    tracker.update("2026-09-30T08:00:00", 0.80, "DDOS", 0.90, 0.80, True)
    t1 = tracker.update("2026-09-30T08:01:00", 0.60, "DDOS", 0.70, 0.50, False)

    assert t1["risk_velocity"] < 0.0
    assert t1["risk_trend"] == "FALLING"

def test_strictly_causal_history():
    tracker = RiskTrajectoryTracker()
    tracker.update("2026-09-30T08:00:00", 0.10, "BENIGN", 0.95, 0.05, False)
    tracker.update("2026-09-30T08:01:00", 0.15, "BENIGN", 0.95, 0.05, False)
    tracker.update("2026-09-30T08:02:00", 0.20, "BENIGN", 0.95, 0.05, False)

    hist = tracker.get_recent_history(count=5)
    assert len(hist) == 3
    # Ensure chronological order
    timestamps = [h["timestamp"] for h in hist]
    assert timestamps == sorted(timestamps)
