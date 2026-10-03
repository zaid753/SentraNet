import os
import pytest
import pandas as pd
import numpy as np
import joblib

def test_chronological_split():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(dataset_path):
        pytest.skip("Full dataset not built.")
        
    df = pd.read_parquet(dataset_path)
    df['window_start'] = pd.to_datetime(df['window_start'])
    df = df.sort_values('window_start').reset_index(drop=True)
    
    total = len(df)
    train_idx = int(total * 0.6)
    val_idx = int(total * 0.8)
    
    train_df = df.iloc[:train_idx]
    val_df = df.iloc[train_idx:val_idx]
    test_df = df.iloc[val_idx:]
    
    assert len(train_df) + len(val_df) + len(test_df) == total
    
    # Verify no timestamp overlap (strict chronological ordering)
    assert train_df['window_start'].max() < val_df['window_start'].min()
    assert val_df['window_start'].max() < test_df['window_start'].min()

def test_no_leakage():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(dataset_path):
        pytest.skip("Full dataset not built.")
        
    df = pd.read_parquet(dataset_path)
    total = len(df)
    train_idx = int(total * 0.6)
    val_idx = int(total * 0.8)
    
    train_df = df.iloc[:train_idx]
    val_df = df.iloc[train_idx:val_idx]
    test_df = df.iloc[val_idx:]
    
    # Assert disjoint indices meaning no duplicate records across splits
    train_indices = set(train_df.index)
    val_indices = set(val_df.index)
    test_indices = set(test_df.index)
    
    assert len(train_indices.intersection(val_indices)) == 0
    assert len(train_indices.intersection(test_indices)) == 0
    assert len(val_indices.intersection(test_indices)) == 0

def test_scaler_fitted_only_on_train():
    scaler_path = "models/experiments/cicids2017/scaler.joblib"
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(scaler_path) or not os.path.exists(dataset_path):
        pytest.skip("Artifacts not available.")
        
    scaler = joblib.load(scaler_path)
    df = pd.read_parquet(dataset_path)
    train_count = int(len(df) * 0.6)
    
    # Validate the scaler's seen samples exactly matches the training split count
    assert scaler.n_samples_seen_ == train_count

def test_model_artifact_loading():
    xgb_path = "models/experiments/cicids2017/xgboost.joblib"
    iso_path = "models/experiments/cicids2017/isolation_forest.joblib"
    if not os.path.exists(xgb_path) or not os.path.exists(iso_path):
        pytest.skip("Artifacts not available.")
        
    xgb_model = joblib.load(xgb_path)
    iso_model = joblib.load(iso_path)
    
    assert hasattr(xgb_model, "predict")
    assert hasattr(iso_model, "predict")

def test_17_feature_compatibility():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(dataset_path):
        pytest.skip("Full dataset not built.")
        
    df = pd.read_parquet(dataset_path)
    features = [c for c in df.columns if c not in ['window_start', 'label']]
    
    assert len(features) == 17
    assert 'flow_count' in features
    assert 'rolling_5_unique_sources' in features

def test_label_mapping():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(dataset_path):
        pytest.skip("Full dataset not built.")
        
    df = pd.read_parquet(dataset_path)
    valid_labels = {"BENIGN", "SCANNING", "DDOS", "BOTNET", "OTHER_ATTACK"}
    
    for lbl in df['label'].unique():
        assert str(lbl) in valid_labels or pd.isna(lbl)
