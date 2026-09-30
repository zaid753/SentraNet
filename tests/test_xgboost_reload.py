"""
SENTRANET — Phase 3 Model Reload Verification Test
Verifies serialization fidelity, memory destruction, reloading, and numerical consistency.
"""

import os
import json
import numpy as np
import pandas as pd
import pytest
import xgboost as xgb
from ml.models.xgboost_classifier import XGBoostClassifier

MODEL_PATH = "models/xgboost/sentranet_xgboost.json"
CLASS_MAPPING_PATH = "models/xgboost/class_mapping.json"
TEST_DATA_PATH = "data/processed/sample/test.parquet"
FEATURE_NAMES_PATH = "data/processed/sample/feature_names.json"

@pytest.fixture
def test_dataset():
    assert os.path.exists(TEST_DATA_PATH), f"Missing {TEST_DATA_PATH}"
    df = pd.read_parquet(TEST_DATA_PATH)
    with open(FEATURE_NAMES_PATH, "r", encoding="utf-8") as f:
        feature_names = json.load(f)["features"]
    return df, feature_names

def test_model_reload_integrity(test_dataset):
    df, feature_names = test_dataset
    X_test = df[feature_names]

    # 1. Load baseline model
    assert os.path.exists(MODEL_PATH)
    classifier_1 = XGBoostClassifier(model_path=MODEL_PATH)
    proba_1 = classifier_1.predict_proba(X_test)
    preds_1 = classifier_1.predict(X_test)

    # 2. Destroy model object from memory
    del classifier_1

    # 3. Reload cleanly from disk artifact
    classifier_2 = XGBoostClassifier(model_path=MODEL_PATH)

    # 4. Verify model properties
    assert classifier_2.booster is not None
    assert len(classifier_2.expected_features) == 17
    assert len(classifier_2.classes) == 5
    assert set(classifier_2.classes) == {"BENIGN", "BOTNET", "DDOS", "OTHER_ATTACK", "SCANNING"}

    # 5. Run inference on test data
    proba_2 = classifier_2.predict_proba(X_test)
    preds_2 = classifier_2.predict(X_test)

    # 6. Verify predictions are numerically identical
    np.testing.assert_allclose(proba_1, proba_2, rtol=1e-5, atol=1e-5)
    assert preds_1 == preds_2

    # 7. Verify output shape, probability bounds, and sum to ~1.0
    assert proba_2.shape == (len(X_test), 5)
    assert np.all(proba_2 >= 0.0)
    assert np.all(proba_2 <= 1.0)
    row_sums = proba_2.sum(axis=1)
    np.testing.assert_allclose(row_sums, np.ones(len(X_test)), rtol=1e-4)

    # 8. Verify predicted classes belong to canonical class set
    valid_classes = set(classifier_2.classes)
    for p in preds_2:
        assert p in valid_classes
