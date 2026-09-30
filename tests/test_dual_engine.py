"""
SENTRANET — Phase 4 Dual AI Engine Integration Test
Proves that XGBoost (Supervised Classifier) and Isolation Forest (Unsupervised Anomaly Detector)
operate concurrently on the exact same 17-feature vector to build the complete Phase 4 DecisionObject.
"""

import os
import json
import numpy as np
import pandas as pd
import pytest
from ml.models.xgboost_classifier import XGBoostClassifier
from ml.models.isolation_forest_detector import IsolationForestDetector

XGB_MODEL_PATH = "models/xgboost/sentranet_xgboost.json"
IF_MODEL_PATH = "models/isolation_forest/sentranet_isolation_forest.joblib"
IF_REF_PATH = "models/isolation_forest/anomaly_reference.json"
TEST_DATA_PATH = "data/processed/sample/test.parquet"

@pytest.fixture
def dual_engine():
    xgb = XGBoostClassifier(model_path=XGB_MODEL_PATH)
    iso = IsolationForestDetector(model_path=IF_MODEL_PATH, reference_path=IF_REF_PATH)
    return xgb, iso

@pytest.fixture
def test_df():
    return pd.read_parquet(TEST_DATA_PATH)

def test_dual_engine_feature_space_consistency(dual_engine):
    xgb, iso = dual_engine
    assert len(xgb.expected_features) == 17
    assert len(iso.expected_features) == 17
    assert xgb.expected_features == iso.expected_features

def test_dual_engine_concurrent_inference(dual_engine, test_df):
    xgb, iso = dual_engine
    features = xgb.expected_features

    for i in range(len(test_df)):
        sample = test_df.iloc[[i]]

        # 1. Supervised classification
        xgb_preds = xgb.predict_decision(sample)
        assert len(xgb_preds) == 1
        xgb_res = xgb_preds[0]

        # 2. Unsupervised anomaly detection
        ano_score = float(iso.anomaly_score(sample)[0])
        is_ano = bool(iso.is_anomalous(sample)[0])

        # 3. DecisionObject Construction
        decision = {
            "timestamp": xgb_res["timestamp"],
            "predicted_class": xgb_res["predicted_class"],
            "class_probabilities": xgb_res["class_probabilities"],
            "classification_confidence": xgb_res["classification_confidence"],
            "anomaly_score": round(ano_score, 4),
            "is_anomalous": is_ano,
            "risk_score": None,
            "time_to_impact_seconds": None,
            "forecast_available": False,
            "explanation": None,
        }

        # Contract assertions
        assert decision["predicted_class"] in {"BENIGN", "BOTNET", "DDOS", "OTHER_ATTACK", "SCANNING"}
        assert len(decision["class_probabilities"]) == 5
        assert 0.0 <= decision["classification_confidence"] <= 1.0
        assert 0.0 <= decision["anomaly_score"] <= 1.0
        assert isinstance(decision["is_anomalous"], bool)

        # Prohibited Phase 5 telemetry
        assert decision["risk_score"] is None
        assert decision["time_to_impact_seconds"] is None
        assert decision["forecast_available"] is False
