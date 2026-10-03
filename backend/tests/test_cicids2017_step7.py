import os
import json
import pytest
import pandas as pd
from datetime import datetime

def test_known_and_novel_class_filtering():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(dataset_path):
        pytest.skip("Full dataset not built.")
        
    df = pd.read_parquet(dataset_path)
    df = df.sort_values('window_start').reset_index(drop=True)
    
    train_idx = int(len(df) * 0.6)
    val_idx = int(len(df) * 0.8)
    
    train_df = df.iloc[:train_idx]
    test_df = df.iloc[val_idx:]
    
    known_classes = set(train_df['label'].unique())
    
    known_mask = test_df['label'].isin(known_classes)
    known_df = test_df[known_mask]
    
    novel_mask = ~test_df['label'].isin(known_classes) & (test_df['label'] != 'BENIGN')
    novel_df = test_df[novel_mask]
    
    assert len(known_df) > 0
    assert len(novel_df) > 0
    
    for lbl in novel_df['label'].unique():
        assert lbl not in known_classes
        assert lbl != 'BENIGN'

def test_attack_episode_reconstruction():
    report_path = "reports/cicids2017_step7_evaluation.json"
    if not os.path.exists(report_path):
        pytest.skip("Step 7 report not generated.")
        
    with open(report_path, "r") as f:
        data = json.load(f)
        
    episodes = data.get("attack_episodes", [])
    assert len(episodes) > 0
    
    for ep in episodes:
        assert "start" in ep
        assert "end" in ep
        assert ep["windows"] > 0
        assert ep["duration_seconds"] >= 0
        
        # start <= end
        start_ts = pd.to_datetime(ep["start"])
        end_ts = pd.to_datetime(ep["end"])
        assert start_ts <= end_ts

def test_forecast_classification_and_early_definition():
    report_path = "reports/cicids2017_step7_evaluation.json"
    if not os.path.exists(report_path):
        pytest.skip("Step 7 report not generated.")
        
    with open(report_path, "r") as f:
        data = json.load(f)
        
    metrics = data.get("forecast_metrics", {})
    assert "EARLY" in metrics
    assert "ONSET" in metrics
    assert "POST_ONSET" in metrics
    assert "FALSE" in metrics
    
    # Check that if EARLY is > 0, lead times are calculated
    if metrics["EARLY"] > 0:
        assert metrics["mean_early_lead"] is not None
        assert metrics["mean_early_lead"] > 0
    else:
        assert metrics["mean_early_lead"] is None

def test_forecast_csv_exists_if_forecasts_generated():
    report_path = "reports/cicids2017_step7_evaluation.json"
    csv_path = "reports/cicids2017_forecast_events.csv"
    
    if not os.path.exists(report_path):
        pytest.skip("Step 7 report not generated.")
        
    with open(report_path, "r") as f:
        data = json.load(f)
        
    if data["forecast_metrics"]["total_forecasts"] > 0:
        assert os.path.exists(csv_path)
        
        df = pd.read_csv(csv_path)
        assert len(df) == data["forecast_metrics"]["total_forecasts"]
        
        required_cols = [
            "forecast_timestamp", "predicted_class", "forecast_state", 
            "actual_attack_onset", "actual_attack_class", 
            "classification", "lead_time_seconds"
        ]
        for col in required_cols:
            assert col in df.columns
