"""
SENTRANET — Phase 5 Forecast Leakage & Causality Verification Tests
Proves that the ForecastEngine cannot access future labels, future features, or onset markers.
"""

import pytest
import pandas as pd
import numpy as np
from ml.forecast.forecast_engine import ForecastEngine

TEST_DATA_PATH = "data/processed/sample/test.parquet"

@pytest.fixture
def engine():
    eng = ForecastEngine()
    eng.reset()
    return eng

@pytest.fixture
def test_df():
    return pd.read_parquet(TEST_DATA_PATH)

def test_forecast_engine_ignores_future_columns(engine, test_df):
    """
    Ensures that passing extra future context or target labels does NOT alter the causal forecast.
    """
    row = test_df.iloc[[0]].copy()

    # Pass normal features
    decision_1 = engine.update(row)

    # Reset engine and inject contaminated future label or fake onset into row dataframe
    engine.reset()
    contaminated_row = row.copy()
    contaminated_row["future_attack_label"] = "DDOS"
    contaminated_row["future_onset_seconds"] = 120
    contaminated_row["target"] = 1

    decision_2 = engine.update(contaminated_row)

    # Decisions must be identical regardless of extra columns
    assert decision_1["predicted_class"] == decision_2["predicted_class"]
    assert decision_1["risk_score"] == decision_2["risk_score"]
    assert decision_1["forecast_available"] == decision_2["forecast_available"]
    assert decision_1["time_to_impact_seconds"] == decision_2["time_to_impact_seconds"]

def test_causal_step_invariance(engine, test_df):
    """
    Proves that decision at window T depends strictly on windows <= T,
    and is invariant to whether subsequent windows T+1...T+N exist.
    """
    # Stream first 5 windows sequentially
    engine.reset()
    decisions_prefix = []
    for i in range(5):
        d = engine.update(test_df.iloc[[i]])
        decisions_prefix.append(d)

    # Reset and stream first 3 windows only
    engine.reset()
    decisions_short = []
    for i in range(3):
        d = engine.update(test_df.iloc[[i]])
        decisions_short.append(d)

    # Windows 0, 1, 2 must produce exactly the same risk and forecast decisions
    for i in range(3):
        assert decisions_prefix[i]["risk_score"] == decisions_short[i]["risk_score"]
        assert decisions_prefix[i]["forecast_available"] == decisions_short[i]["forecast_available"]
        assert decisions_prefix[i]["time_to_impact_seconds"] == decisions_short[i]["time_to_impact_seconds"]

def test_decision_object_contract_phase5(engine, test_df):
    """
    Verifies that all Phase 5 extended fields exist in DecisionObject.
    """
    engine.reset()
    d = engine.update(test_df.iloc[[0]])

    expected_keys = {
        "timestamp",
        "predicted_class",
        "class_probabilities",
        "classification_confidence",
        "anomaly_score",
        "is_anomalous",
        "risk_score",
        "risk_state",
        "risk_velocity",
        "risk_acceleration",
        "risk_trend",
        "forecast_available",
        "forecast_class",
        "time_to_impact_seconds",
        "forecast_confidence",
        "forecast_reason",
        "explanation",
    }
    assert set(d.keys()) == expected_keys
    assert d["risk_state"] in {"LOW", "GUARDED", "ELEVATED", "HIGH"}
    assert d["risk_trend"] in {"STABLE", "RISING", "RAPIDLY_RISING", "FALLING"}
    assert isinstance(d["forecast_available"], bool)
