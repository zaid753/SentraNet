"""
SENTRANET — Phase 6 Alert State Machine & Incident Manager Tests
Verifies state transitions, deduplication, updates, resolution, cooldown, and forecast events.
"""

import pytest
from backend.replay.alert_state_machine import AlertStateMachine
from backend.replay.incident_manager import IncidentManager

@pytest.fixture
def sm():
    mgr = IncidentManager(resolution_consecutive_windows=2, cooldown_seconds=120)
    return AlertStateMachine(incident_manager=mgr)

def make_decision(ts, risk_state, risk_score, pred_class="SCANNING", forecast=False, eta=None):
    return {
        "timestamp": ts,
        "predicted_class": pred_class,
        "class_probabilities": {"BENIGN": 0.05, pred_class: 0.95},
        "classification_confidence": 0.95,
        "anomaly_score": 0.80,
        "is_anomalous": True,
        "risk_score": risk_score,
        "risk_state": risk_state,
        "risk_velocity": 0.05,
        "risk_acceleration": 0.01,
        "risk_trend": "RISING",
        "forecast_available": forecast,
        "forecast_class": pred_class if forecast else None,
        "time_to_impact_seconds": eta,
        "forecast_confidence": 0.85 if forecast else None,
        "forecast_reason": ["Test reason"] if forecast else [],
    }

def test_normal_to_watch_transition(sm):
    # LOW -> NORMAL
    d0 = make_decision("2026-09-30T08:00:00", "LOW", 0.10, "BENIGN")
    state, sev, events = sm.process_decision(d0)
    assert state == "NORMAL"
    assert sev == "INFO"
    assert len(events) == 0

    # GUARDED -> WATCH
    d1 = make_decision("2026-09-30T08:01:00", "GUARDED", 0.35, "SCANNING")
    state, sev, events = sm.process_decision(d1)
    assert state == "WATCH"
    assert sev == "MEDIUM"
    assert len(events) == 1
    assert events[0].event_type == "WATCH_STARTED"

def test_watch_to_alert_and_direct_normal_to_alert(sm):
    # Direct NORMAL -> ALERT (HIGH)
    d = make_decision("2026-09-30T08:00:00", "HIGH", 0.85, "DDOS")
    state, sev, events = sm.process_decision(d)
    assert state == "ALERT"
    assert sev == "HIGH"
    assert any(e.event_type == "ALERT_CREATED" for e in events)

def test_alert_deduplication_and_updates(sm):
    # First window in HIGH -> ALERT_CREATED
    d1 = make_decision("2026-09-30T08:00:00", "HIGH", 0.80, "SCANNING")
    _, _, ev1 = sm.process_decision(d1)
    assert any(e.event_type == "ALERT_CREATED" for e in ev1)
    inc_id = sm.incident_manager.active_incident.incident_id

    # Second window in HIGH for same class -> ALERT_UPDATED on SAME incident (no duplicate incident)
    d2 = make_decision("2026-09-30T08:01:00", "HIGH", 0.82, "SCANNING")
    _, _, ev2 = sm.process_decision(d2)
    assert len(sm.incident_manager.incidents) == 1
    assert any(e.event_type == "ALERT_UPDATED" and e.incident_id == inc_id for e in ev2)

    # Third window in HIGH -> ALERT_UPDATED
    d3 = make_decision("2026-09-30T08:02:00", "HIGH", 0.83, "SCANNING")
    _, _, ev3 = sm.process_decision(d3)
    assert len(sm.incident_manager.incidents) == 1
    assert sm.incident_manager.active_incident.event_count == 3

def test_incident_resolution_after_consecutive_recovery_windows(sm):
    # Window 1: ALERT
    sm.process_decision(make_decision("2026-09-30T08:00:00", "HIGH", 0.80, "SCANNING"))
    assert sm.incident_manager.active_incident is not None

    # Window 2: Falls to LOW (1st recovery window -> still active)
    sm.process_decision(make_decision("2026-09-30T08:01:00", "LOW", 0.10, "BENIGN"))
    assert sm.incident_manager.active_incident is not None

    # Window 3: Stays LOW (2nd recovery window -> resolves incident)
    _, _, ev = sm.process_decision(make_decision("2026-09-30T08:02:00", "LOW", 0.10, "BENIGN"))
    assert sm.incident_manager.active_incident is None
    assert any(e.event_type == "ALERT_RESOLVED" for e in ev)
    assert len(sm.incident_manager.incidents) == 1
    assert sm.incident_manager.incidents[0].status == "RESOLVED"

def test_cooldown_suppresses_duplicate_immediate_incident(sm):
    # Create and resolve incident
    sm.process_decision(make_decision("2026-09-30T08:00:00", "HIGH", 0.80, "SCANNING"))
    sm.process_decision(make_decision("2026-09-30T08:01:00", "LOW", 0.10, "BENIGN"))
    sm.process_decision(make_decision("2026-09-30T08:02:00", "LOW", 0.10, "BENIGN"))
    assert len(sm.incident_manager.incidents) == 1
    assert sm.incident_manager.active_incident is None

    # Immediate spike 30s later (< 120s cooldown) for same class
    _, _, ev = sm.process_decision(make_decision("2026-09-30T08:02:30", "HIGH", 0.80, "SCANNING"))
    # Duplicate incident creation should be suppressed
    assert len(sm.incident_manager.incidents) == 1

def test_forecast_trigger_event(sm):
    # Forecast off initially
    d1 = make_decision("2026-09-30T08:00:00", "HIGH", 0.80, "SCANNING", forecast=False)
    _, _, ev1 = sm.process_decision(d1)
    assert not any(e.event_type == "FORECAST_TRIGGERED" for e in ev1)

    # Forecast turns on -> FORECAST_TRIGGERED emitted
    d2 = make_decision("2026-09-30T08:01:00", "HIGH", 0.85, "SCANNING", forecast=True, eta=60)
    _, _, ev2 = sm.process_decision(d2)
    assert any(e.event_type == "FORECAST_TRIGGERED" for e in ev2)
