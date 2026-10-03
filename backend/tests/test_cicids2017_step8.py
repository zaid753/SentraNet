import os
import pytest
import pandas as pd
import json

def test_experiment_b_impossibility():
    dataset_path = "data/processed/cicids2017/full_dataset.parquet"
    if not os.path.exists(dataset_path):
        pytest.skip("Full dataset not built.")
        
    df = pd.read_parquet(dataset_path)
    df['window_start'] = pd.to_datetime(df['window_start'])
    df = df.sort_values('window_start').reset_index(drop=True)
    
    # Verify that the last class to appear is BOTNET at index > 0
    latest_first_appearance_time = df.groupby('label')['window_start'].min().max()
    
    # Calculate what would be left in TEST if we split here
    test_df = df[df['window_start'] > latest_first_appearance_time]
    test_classes = set(test_df['label'].unique())
    all_classes = set(df['label'].unique())
    
    # It is mathematically impossible for test_classes to equal all_classes
    # because classes like DDOS and OTHER_ATTACK ended before this time.
    assert len(test_classes) < len(all_classes)
    assert "DDOS" not in test_classes
    assert "OTHER_ATTACK" not in test_classes

def test_step8_report_generated():
    report_path = "reports/cicids2017_coverage_evaluation.json"
    if not os.path.exists(report_path):
        pytest.skip("Step 8 report not generated.")
        
    with open(report_path, "r") as f:
        data = json.load(f)
        
    assert data["experiment_a_preserved"] is True
    assert data["experiment_b_feasibility"]["is_impossible"] is True
    assert "STOPPED" in data["conclusion"]
    assert data["model_promotion_status"] == "EXPERIMENTAL MODEL — NOT YET DEFAULT"
