"""
SENTRANET — Phase 4 Isolation Forest Model Reload Verification Test
Verifies serialization fidelity, memory destruction, reloading, and numerical consistency.
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
FEATURE_NAMES_PATH = "data/processed/sample/feature_names.json"

@pytest.fixture
def test_dataset():
    assert os.path.exists(TEST_DATA_PATH), f"Missing {TEST_DATA_PATH}"
    df = pd.read_parquet(TEST_DATA_PATH)
    with open(FEATURE_NAMES_PATH, "r", encoding="utf-8") as f:
        feature_names = json.load(f)["features"]
    return df, feature_names

def test_isolation_forest_reload_integrity(test_dataset):
    df, feature_names = test_dataset
    X_test = df[feature_names]

    # 1. Load initial model
    assert os.path.exists(MODEL_PATH)
    assert os.path.exists(REFERENCE_PATH)
    detector_1 = IsolationForestDetector(model_path=MODEL_PATH, reference_path=REFERENCE_PATH)
    scores_1 = detector_1.anomaly_score(X_test)
    flags_1 = detector_1.is_anomalous(X_test)

    # 2. Destroy model object from memory
    del detector_1

    # 3. Reload cleanly from disk artifact
    detector_2 = IsolationForestDetector(model_path=MODEL_PATH, reference_path=REFERENCE_PATH)

    # 4. Verify model properties
    assert detector_2.model is not None
    assert len(detector_2.expected_features) == 17
    assert detector_2.threshold > 0.0
    assert detector_2.threshold < 1.0

    # 5. Re-run inference on test data
    scores_2 = detector_2.anomaly_score(X_test)
    flags_2 = detector_2.is_anomalous(X_test)

    # 6. Verify numerical equivalence
    np.testing.assert_allclose(scores_1, scores_2, rtol=1e-5, atol=1e-5)
    assert flags_1 == flags_2

    # 7. Verify bounds and constraints: score in [0.0, 1.0]
    assert np.all(scores_2 >= 0.0)
    assert np.all(scores_2 <= 1.0)

    # 8. Verify threshold logic
    for i, score in enumerate(scores_2):
        expected_flag = bool(score >= detector_2.threshold)
        assert flags_2[i] == expected_flag
