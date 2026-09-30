"""Comprehensive tests for SENTRANET Phase 2 Data Pipeline."""

import os
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from ml.preprocessing.schema import CANONICAL_SCHEMA, get_canonical_fields, MODEL_BASE_NUMERIC_FEATURES
from ml.preprocessing.cleaner import DataCleaner, DatasetQualityReport
from ml.preprocessing.labels import normalize_label, TARGET_CLASSES, CICIDS2017_LABEL_MAP
from ml.preprocessing.features import FeatureEngineer, FeatureRegistry
from ml.preprocessing.windowing import TemporalWindowAggregator
from ml.preprocessing.scaler import SafeFeatureScaler
from ml.preprocessing.pipeline import PreprocessingPipeline
from ml.data.registry import DatasetRegistry
from ml.data.cicids_loader import CICIDS2017Loader
from ml.data.unsw_loader import UNSWNB15Loader
from ml.data.cic_ddos_loader import CICDDoS2019Loader

# 1. Schema Validation
def test_canonical_schema_definitions():
    assert "timestamp" in CANONICAL_SCHEMA
    assert "flow_duration" in CANONICAL_SCHEMA
    assert "label" in CANONICAL_SCHEMA
    available = get_canonical_fields("AVAILABLE")
    assert len(available) > 0
    assert len(MODEL_BASE_NUMERIC_FEATURES) > 10

# 2. Column Normalization & Cleaner
def test_cleaner_column_normalization():
    cleaner = DataCleaner("test")
    raw_col = "  Flow Duration / s - total. "
    normalized = cleaner.normalize_column_name(raw_col)
    assert normalized == "flow_duration_s_total"

# 3. Missing & Infinity Value Handling
def test_cleaner_handles_nans_and_infinities():
    cleaner = DataCleaner("test")
    df = pd.DataFrame({
        "timestamp": ["2026-09-30 08:00:00", "2026-09-30 08:01:00", "2026-09-30 08:02:00"],
        "flow_duration": [100.0, np.inf, -np.inf],
        "total_packets": [10, np.nan, 20],
        "label": ["BENIGN", "DDoS", "BENIGN"],
    })

    cleaned, report = cleaner.clean(df)
    assert report.infinite_value_count == 2
    assert report.missing_value_count >= 1
    # Check no infinities remain in cleaned dataframe
    assert not np.isinf(cleaned["flow_duration"]).any()
    assert not cleaned["total_packets"].isna().any()

# 4. Duplicate Record Handling
def test_cleaner_duplicate_handling():
    cleaner = DataCleaner("test")
    row = {"timestamp": "2026-09-30 08:00:00", "flow_duration": 100.0, "label": "BENIGN"}
    df = pd.DataFrame([row, row, row])
    cleaned, report = cleaner.clean(df)
    assert report.duplicate_count == 2
    assert len(cleaned) == 1

# 5. Label Normalization (Strict mapping & no silent mapping to BENIGN)
def test_label_normalization():
    # Standard mappings
    assert normalize_label("BENIGN", "cicids2017") == "BENIGN"
    assert normalize_label("DDoS", "cicids2017") == "DDOS"
    assert normalize_label("PortScan", "cicids2017") == "SCANNING"
    assert normalize_label("Bot", "cicids2017") == "BOTNET"
    assert normalize_label("FTP-Patator", "cicids2017") == "OTHER_ATTACK"

    # UNSW-NB15 mappings
    assert normalize_label("Normal", "unsw_nb15") == "BENIGN"
    assert normalize_label("Reconnaissance", "unsw_nb15") == "SCANNING"
    assert normalize_label("Exploits", "unsw_nb15") == "OTHER_ATTACK"

    # Strict rule: Unknown labels MUST NOT default to BENIGN
    assert normalize_label("unknown_novel_zero_day_threat") == "OTHER_ATTACK"

# 6. Feature Engineering & Zero-Division Protection
def test_feature_engineering_safe_division():
    engineer = FeatureEngineer()
    df = pd.DataFrame({
        "flow_duration": [0.0, 100.0],
        "forward_packet_count": [0, 5],
        "backward_packet_count": [0, 5],
        "forward_bytes": [0.0, 500.0],
        "backward_bytes": [0.0, 500.0],
        "destination_port": [80, 50000],
    })

    engineered, features = engineer.engineer_features(df)
    # Check that division by zero duration does not produce inf
    assert not np.isinf(engineered["packet_rate"]).any()
    assert not np.isinf(engineered["byte_rate"]).any()
    assert engineered["is_privileged_port"].tolist() == [1, 0]
    assert "total_packet_count" in engineered.columns

# 7. Temporal Windowing & Causal Aggregation
def test_temporal_windowing_and_causality():
    base_time = datetime(2026, 9, 30, 8, 0, 0)
    # Create 3 minutes of traffic (180 seconds)
    timestamps = [base_time + timedelta(seconds=i) for i in range(180)]
    df = pd.DataFrame({
        "timestamp": timestamps,
        "total_packet_count": np.ones(180) * 10,
        "total_bytes": np.ones(180) * 1000,
        "packet_rate": np.ones(180) * 5,
        "byte_rate": np.ones(180) * 500,
        "flow_duration": np.ones(180) * 2,
        "source_ip": ["10.0.0.1"] * 180,
        "destination_ip": ["10.0.0.2"] * 180,
        "is_privileged_port": [1] * 180,
        "label": ["BENIGN"] * 120 + ["DDoS"] * 60,
    })

    aggregator = TemporalWindowAggregator(window_size_seconds=60, rolling_window_count=2)
    windows = aggregator.aggregate_windows(df)

    assert len(windows) == 3
    assert "window_id" in windows.columns
    # Check window labels: first 2 are BENIGN, 3rd is DDOS
    assert windows["label"].iloc[0] == "BENIGN"
    assert windows["label"].iloc[1] == "BENIGN"
    assert windows["label"].iloc[2] == "DDOS"
    # Check causal rolling features
    assert "rolling_2_flow_count" in windows.columns
    # Window 0 rolling count should be 60, Window 1 should be 60
    assert windows["rolling_2_flow_count"].iloc[0] == 60

# 8. Data Leakage Prevention: Scaler fitted ONLY on train
def test_scaler_leakage_protection():
    scaler = SafeFeatureScaler(scaler_type="standard")
    train_df = pd.DataFrame({"feat_a": [10.0, 20.0, 30.0], "feat_b": [1.0, 2.0, 3.0]})
    test_df = pd.DataFrame({"feat_a": [100.0, 200.0], "feat_b": [10.0, 20.0]})

    scaler.fit(train_df, ["feat_a", "feat_b"])
    # Mean of train_df["feat_a"] is 20.0
    assert np.isclose(scaler.scaler.mean_[0], 20.0)

    # Test transform uses train mean
    transformed_test = scaler.transform(test_df)
    # The test values must be normalized using train mean (20.0) and std, NOT test mean
    assert transformed_test["feat_a"].iloc[0] > 0

# 9. Dataset Registry
def test_dataset_registry():
    registered = DatasetRegistry.list_registered()
    assert "cicids2017" in registered
    assert "unsw_nb15" in registered
    assert "cic_ddos2019" in registered

    loader = DatasetRegistry.get_loader("cicids2017")
    assert isinstance(loader, CICIDS2017Loader)
    loader_unsw = DatasetRegistry.get_loader("unsw_nb15")
    assert isinstance(loader_unsw, UNSWNB15Loader)
    loader_ddos = DatasetRegistry.get_loader("cic_ddos2019")
    assert isinstance(loader_ddos, CICDDoS2019Loader)

# 10. End-to-End Pipeline Execution on Sample Data
def test_end_to_end_sample_pipeline(tmp_path):
    sample_file = "data/samples/sample_network_traffic.csv"
    assert os.path.exists(sample_file)

    output_dir = str(tmp_path / "processed_test")
    pipeline = PreprocessingPipeline(
        dataset_name="sample",
        window_size_seconds=60,
        rolling_window_count=3,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
    )

    metadata = pipeline.run(
        input_path=sample_file,
        output_dir=output_dir,
    )

    assert metadata["train_rows"] > 0
    assert metadata["validation_rows"] > 0
    assert metadata["test_rows"] > 0
    assert metadata["feature_count"] > 0
    assert os.path.exists(os.path.join(output_dir, "train.parquet"))
    assert os.path.exists(os.path.join(output_dir, "validation.parquet"))
    assert os.path.exists(os.path.join(output_dir, "test.parquet"))
    assert os.path.exists(os.path.join(output_dir, "artifacts", "scaler.joblib"))
    assert os.path.exists(os.path.join(output_dir, "artifacts", "label_encoder.joblib"))
    assert os.path.exists(os.path.join(output_dir, "quality_report.json"))
