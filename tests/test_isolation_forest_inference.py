"""
SENTRANET — Phase 4 Isolation Forest Robustness & Input Validation Tests
Verifies robust rejection of wrong feature dimensions, missing columns, NaNs, and infinities.
"""

import os
import json
import numpy as np
import pandas as pd
import pytest
from ml.models.isolation_forest_detector import IsolationForestDetector

MODEL_PATH = "models/isolation_forest/sentranet_isolation_forest.joblib"
REFERENCE_PATH = "models/isolation_forest/anomaly_reference.json"
TEST_DATA_PATH = "data/processed/sample/test.parquet"

@pytest.fixture
def detector():
    return IsolationForestDetector(model_path=MODEL_PATH, reference_path=REFERENCE_PATH)

@pytest.fixture
def test_df():
    return pd.read_parquet(TEST_DATA_PATH)

def test_inference_on_valid_dataframe(detector, test_df):
    scores = detector.anomaly_score(test_df)
    flags = detector.is_anomalous(test_df)
    decisions = detector.predict_decision(test_df)

    assert len(scores) == len(test_df)
    assert len(flags) == len(test_df)
    assert len(decisions) == len(test_df)

    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)

    for d in decisions:
        assert d["anomaly_score"] is not None
        assert 0.0 <= d["anomaly_score"] <= 1.0
        assert isinstance(d["is_anomalous"], bool)
        assert d["risk_score"] is None
        assert d["time_to_impact_seconds"] is None
        assert d["forecast_available"] is False

def test_inference_on_valid_numpy_array(detector, test_df):
    features = detector.expected_features
    X_arr = test_df[features].values.astype(np.float64)
    scores = detector.anomaly_score(X_arr)
    assert len(scores) == len(test_df)
    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)

def test_reject_wrong_feature_count(detector):
    bad_16 = np.zeros((1, 16))
    with pytest.raises(ValueError, match="Invalid feature dimension"):
        detector.anomaly_score(bad_16)

    bad_18 = np.zeros((1, 18))
    with pytest.raises(ValueError, match="Invalid feature dimension"):
        detector.anomaly_score(bad_18)

def test_reject_missing_columns(detector, test_df):
    bad_df = test_df.drop(columns=["flow_count"])
    with pytest.raises(ValueError, match="missing required columns"):
        detector.anomaly_score(bad_df)

def test_reject_nan_features(detector, test_df):
    bad_df = test_df.copy()
    bad_df.loc[0, "flow_count"] = np.nan
    with pytest.raises(ValueError, match="contains NaN"):
        detector.anomaly_score(bad_df)

def test_reject_infinite_features(detector, test_df):
    bad_df = test_df.copy()
    bad_df.loc[0, "total_bytes"] = np.inf
    with pytest.raises(ValueError, match="contains Infinite"):
        detector.anomaly_score(bad_df)

def test_reject_unsupported_type(detector):
    with pytest.raises(TypeError, match="Unsupported features type"):
        detector.anomaly_score("not_a_valid_feature_container")
