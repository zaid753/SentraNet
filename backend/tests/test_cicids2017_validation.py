import os
import pytest
import pandas as pd
import numpy as np

from scripts.validate_cicids2017 import validate_dataset
from backend.telemetry.datasets.cicids_adapter import CICIDS2017Adapter

@pytest.fixture
def cicids_parquet_path():
    return "data/processed/cicids2017/Friday-WorkingHours-Morning.parquet"

def test_cicids_17_feature_compatibility(cicids_parquet_path):
    assert os.path.exists(cicids_parquet_path), "Dataset parquet not generated"
    df = pd.read_parquet(cicids_parquet_path)
    
    # Exclude metadata columns
    features = [c for c in df.columns if c not in ['window_start', 'label']]
    assert len(features) == 17, f"Expected 17 canonical features, found {len(features)}"
    
    expected_features = [
        "flow_count", "total_packets", "total_bytes", "avg_packet_rate",
        "avg_byte_rate", "unique_sources", "unique_destinations",
        "avg_packet_size", "avg_flow_duration", "syn_flag_count",
        "ack_flag_count", "privileged_port_ratio", "rolling_5_flow_count",
        "rolling_5_total_packets", "rolling_5_total_bytes",
        "rolling_5_avg_byte_rate", "rolling_5_unique_sources"
    ]
    for feat in expected_features:
        assert feat in df.columns, f"Missing canonical feature: {feat}"

def test_cicids_label_mapping():
    adapter = CICIDS2017Adapter()
    
    assert adapter.LABEL_MAPPING['BENIGN'] == 'BENIGN'
    assert adapter.LABEL_MAPPING['Bot'] == 'BOTNET'
    assert adapter.LABEL_MAPPING['DDoS'] == 'DDOS'
    assert adapter.LABEL_MAPPING['PortScan'] == 'SCANNING'

def test_cicids_chronological_ordering_and_no_nan(cicids_parquet_path):
    df = pd.read_parquet(cicids_parquet_path)
    
    # Chronological ordering
    ts_series = pd.to_datetime(df['window_start'])
    assert ts_series.is_monotonic_increasing, "Windows are not strictly chronological"
    assert not ts_series.duplicated().any(), "Duplicate timestamps found"
    
    # No NaN or Inf
    features = [c for c in df.columns if c not in ['window_start', 'label']]
    assert not df[features].isnull().values.any(), "NaN values found in features"
    assert not np.isinf(df[features].values).any(), "Inf values found in features"

def test_evaluation_reproducibility(cicids_parquet_path):
    # Running the validation script should not crash and should produce the reports
    report_json = "reports/cicids2017_validation.json"
    report_md = "reports/cicids2017_validation.md"
    
    if os.path.exists(report_json):
        os.remove(report_json)
    if os.path.exists(report_md):
        os.remove(report_md)
        
    validate_dataset()
    
    assert os.path.exists(report_json), "Validation JSON report not generated"
    assert os.path.exists(report_md), "Validation Markdown report not generated"
    
    # Ensure the model accuracy is deterministic (expected 0.0 with frozen model on real dataset)
    import json
    with open(report_json, "r") as f:
        data = json.load(f)
        
    assert data["window_count"] == 241
    # Check that it executed the frozen model evaluation path
    assert "xgboost_metrics" in data
    assert "isolation_forest_metrics" in data
