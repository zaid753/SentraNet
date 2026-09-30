"""Tests for Phase 3 schema, feature definitions, and class mapping contracts."""

import os
import json
import pytest
import pandas as pd

def test_feature_schema_count_and_content():
    features_path = "data/processed/sample/feature_names.json"
    assert os.path.exists(features_path)

    with open(features_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data["features"]
    assert len(features) == 17
    assert "flow_count" in features
    assert "total_packets" in features
    assert "total_bytes" in features
    assert "syn_flag_count" in features
    assert "rolling_5_flow_count" in features

def test_parquet_partitions_match_feature_schema():
    features_path = "data/processed/sample/feature_names.json"
    with open(features_path, "r", encoding="utf-8") as f:
        features = json.load(f)["features"]

    for split in ["train", "validation", "test"]:
        p_path = f"data/processed/sample/{split}.parquet"
        assert os.path.exists(p_path)
        df = pd.read_parquet(p_path)
        for feat in features:
            assert feat in df.columns
            # Ensure no NaNs in model inputs
            assert not df[feat].isna().any()

def test_label_encoder_has_five_canonical_classes():
    import joblib
    encoder_path = "data/processed/sample/artifacts/label_encoder.joblib"
    assert os.path.exists(encoder_path)
    encoder = joblib.load(encoder_path)

    expected = {"BENIGN", "DDOS", "SCANNING", "BOTNET", "OTHER_ATTACK"}
    actual = set(encoder.classes_)
    assert expected.issubset(actual)
