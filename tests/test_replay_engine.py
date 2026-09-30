"""
SENTRANET — Phase 6 Replay Engine Unit Tests
Verifies chronological ordering, causality, determinism, replay modes, schema, and leakage safety.
"""

import pytest
import pandas as pd
import numpy as np
from backend.replay.replay_engine import ReplayEngine
from backend.replay.replay_clock import ReplayClock
from backend.replay.replay_config import ReplayConfig

TEST_DATA_PATH = "data/processed/sample/validation.parquet"

@pytest.fixture
def test_df():
    return pd.read_parquet(TEST_DATA_PATH)

def test_chronological_ordering_enforced(test_df):
    engine = ReplayEngine(mode="batch")

    # Intentionally shuffle the rows
    shuffled_df = test_df.sample(frac=1.0, random_state=42)
    assert not shuffled_df["window_start"].is_monotonic_increasing

    # Stream should re-sort and yield strictly in ascending chronological order
    timestamps = []
    for event, _ in engine.replay_stream(shuffled_df, max_windows=10):
        timestamps.append(event.timestamp)

    assert len(timestamps) == 10
    assert timestamps == sorted(timestamps)

def test_replay_determinism(test_df):
    # Run 1
    engine1 = ReplayEngine(mode="batch")
    events1 = [e.to_dict() for e, _ in engine1.replay_stream(test_df, max_windows=10)]

    # Run 2
    engine2 = ReplayEngine(mode="batch")
    events2 = [e.to_dict() for e, _ in engine2.replay_stream(test_df, max_windows=10)]

    assert len(events1) == 10
    assert len(events2) == 10
    assert events1 == events2

def test_no_future_leakage(test_df):
    """
    Verifies that the prediction at window 2 is identical whether we pass 3 windows or 30 windows.
    """
    engine_short = ReplayEngine(mode="batch")
    short_events = [e.to_dict() for e, _ in engine_short.replay_stream(test_df, max_windows=3)]

    engine_long = ReplayEngine(mode="batch")
    long_events = [e.to_dict() for e, _ in engine_long.replay_stream(test_df, max_windows=15)]

    # Window index 2 must be identical in all runtime telemetry
    assert short_events[2]["risk_score"] == long_events[2]["risk_score"]
    assert short_events[2]["attack_class"] == long_events[2]["attack_class"]
    assert short_events[2]["alert_state"] == long_events[2]["alert_state"]
    assert short_events[2]["forecast_active"] == long_events[2]["forecast_active"]

def test_replay_event_schema_completeness(test_df):
    engine = ReplayEngine(mode="batch")
    first_event, _ = next(engine.replay_stream(test_df, max_windows=1))

    required_keys = {
        "event_id",
        "timestamp",
        "window_id",
        "attack_class",
        "class_probability",
        "attack_likelihood",
        "anomaly_score",
        "is_anomalous",
        "risk_score",
        "risk_state",
        "risk_velocity",
        "risk_acceleration",
        "risk_trend",
        "emergence_detected",
        "forecast_active",
        "forecast_class",
        "estimated_eta_seconds",
        "forecast_confidence",
        "reasons",
        "alert_state",
        "severity",
        "replay_mode",
    }
    event_dict = first_event.to_dict()
    assert set(event_dict.keys()) == required_keys
    assert event_dict["alert_state"] in {"NORMAL", "WATCH", "ALERT", "RESOLVED"}
    assert event_dict["severity"] in {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

def test_replay_modes_configuration():
    # Batch mode
    clk_batch = ReplayClock(mode="batch")
    assert clk_batch.mode == "batch"
    dt = clk_batch.tick("2026-09-30T08:00:00")
    assert dt == 0.0

    # Realtime mode configuration
    clk_rt = ReplayClock(mode="realtime", speed_multiplier=100.0)
    assert clk_rt.mode == "realtime"
    assert clk_rt.speed_multiplier == 100.0

    # Step mode with mock prompt callback
    step_calls = []
    def mock_prompt(msg):
        step_calls.append(msg)
        return True

    clk_step = ReplayClock(mode="step", step_prompt_fn=mock_prompt)
    clk_step.tick("2026-09-30T08:00:00")
    clk_step.tick("2026-09-30T08:01:00")
    assert len(step_calls) == 2
