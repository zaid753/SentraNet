"""
SENTRANET — Phase 3 Inference, Schema, and Robustness Tests
Covers Dataset loading, Feature schema, DecisionObject contract, and Invalid input handling.
"""

import os
import json
import numpy as np
import pandas as pd
import pytest
from ml.models.xgboost_classifier import XGBoostClassifier

MODEL_PATH = "models/xgboost/sentranet_xgboost.json"
CLASS_MAPPING_PATH = "models/xgboost/class_mapping.json"
TEST_DATA_PATH = "data/processed/sample/test.parquet"
FEATURE_NAMES_PATH = "data/processed/sample/feature_names.json"

@pytest.fixture
def classifier():
    return XGBoostClassifier(model_path=MODEL_PATH)

@pytest.fixture
def test_df():
    return pd.read_parquet(TEST_DATA_PATH)

def test_dataset_loading_and_features(test_df):
    """Test 1 & 2: Dataset loading and feature schema."""
    assert len(test_df) == 31
    with open(FEATURE_NAMES_PATH, "r", encoding="utf-8") as f:
        features = json.load(f)["features"]
    assert len(features) == 17
    for feat in features:
        assert feat in test_df.columns
        assert not test_df[feat].isna().any()

def test_label_mapping_integrity(classifier):
    """Test 3: Label mapping has 5 canonical classes."""
    expected_classes = {"BENIGN", "BOTNET", "DDOS", "OTHER_ATTACK", "SCANNING"}
    assert set(classifier.classes) == expected_classes
    assert len(classifier.class_to_idx) == 5
    for cls in expected_classes:
        assert cls in classifier.class_to_idx
        idx = classifier.class_to_idx[cls]
        assert classifier.idx_to_class[idx] == cls

def test_probability_and_prediction_output(classifier, test_df):
    """Test 4, 5, 6, 7: Model loading, probability output, prediction, normalization."""
    proba = classifier.predict_proba(test_df)
    preds = classifier.predict(test_df)

    assert proba.shape == (len(test_df), 5)
    assert len(preds) == len(test_df)

    # Probabilities must be in [0, 1] and sum to 1.0
    assert np.all(proba >= 0.0)
    assert np.all(proba <= 1.0)
    np.testing.assert_allclose(proba.sum(axis=1), np.ones(len(test_df)), rtol=1e-4)

    # Prediction matches argmax
    for i, pred in enumerate(preds):
        best_idx = np.argmax(proba[i])
        assert pred == classifier.idx_to_class[best_idx]

def test_decision_object_contract(classifier, test_df):
    """Test 8: DecisionObject generation adhering to Phase 1 contract."""
    sample = test_df.iloc[[0]]
    decisions = classifier.predict_decision(sample, timestamp="2026-09-30T10:53:00.000000")

    assert len(decisions) == 1
    d = decisions[0]

    # Required contract keys
    expected_keys = {
        "timestamp",
        "predicted_class",
        "class_probabilities",
        "classification_confidence",
        "anomaly_score",
        "risk_score",
        "time_to_impact_seconds",
        "forecast_available",
        "explanation",
    }
    assert set(d.keys()) == expected_keys

    assert d["timestamp"] == "2026-09-30T10:53:00.000000"
    assert d["predicted_class"] in classifier.classes
    assert len(d["class_probabilities"]) == 5
    assert set(d["class_probabilities"].keys()) == set(classifier.classes)
    assert 0.0 <= d["classification_confidence"] <= 1.0

    # Fields that belong to future phases must remain None/False
    assert d["anomaly_score"] is None
    assert d["risk_score"] is None
    assert d["time_to_impact_seconds"] is None
    assert d["forecast_available"] is False
    assert d["explanation"] is None

def test_invalid_feature_count_raises(classifier):
    """Test 10a: Wrong feature count raises ValueError."""
    bad_features_16 = np.zeros((1, 16))
    with pytest.raises(ValueError, match="Invalid feature dimension"):
        classifier.predict_proba(bad_features_16)

    bad_features_18 = np.zeros((1, 18))
    with pytest.raises(ValueError, match="Invalid feature dimension"):
        classifier.predict_proba(bad_features_18)

def test_missing_feature_column_raises(classifier, test_df):
    """Test 10b: Missing expected feature column raises ValueError."""
    bad_df = test_df.drop(columns=["flow_count"])
    with pytest.raises(ValueError, match="missing required columns"):
        classifier.predict_proba(bad_df)

def test_nan_features_raise(classifier, test_df):
    """Test 10c: NaN features in input raise ValueError."""
    bad_df = test_df.copy()
    bad_df.loc[0, "flow_count"] = np.nan
    with pytest.raises(ValueError, match="contains NaN"):
        classifier.predict_proba(bad_df)

def test_infinite_features_raise(classifier, test_df):
    """Test 10d: Infinite features in input raise ValueError."""
    bad_df = test_df.copy()
    bad_df.loc[0, "total_bytes"] = np.inf
    with pytest.raises(ValueError, match="contains Infinite"):
        classifier.predict_proba(bad_df)
