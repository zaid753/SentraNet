#!/usr/bin/env python3
"""
SENTRANET — Dataset Preparation and Preprocessing Pipeline Tool
Usage:
    python scripts/prepare_dataset.py --dataset cicids2017 [--input data/raw/cicids2017] [--output data/processed/cicids2017]
"""

import sys
import os
import argparse
import yaml

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing.pipeline import PreprocessingPipeline

def main():
    parser = argparse.ArgumentParser(description="Execute the SENTRANET feature engineering & preprocessing pipeline.")
    parser.add_argument("--dataset", type=str, default="cicids2017", help="Dataset identifier (cicids2017, unsw_nb15, cic_ddos2019, sample)")
    parser.add_argument("--input", type=str, default=None, help="Input directory or file containing raw data")
    parser.add_argument("--output", type=str, default=None, help="Output directory for processed parquet files and artifacts")
    parser.add_argument("--config", type=str, default="configs/data.yaml", help="Path to pipeline configuration YAML")
    parser.add_argument("--window-size", type=int, default=None, help="Temporal window size in seconds (overrides config)")
    parser.add_argument("--max-rows", type=int, default=None, help="Limit number of raw records to process (for quick validation)")
    parser.add_argument("--no-windowing", action="store_true", help="Disable temporal windowing and process raw flow records directly")

    args = parser.parse_args()

    # Load configuration file if present
    cfg = {}
    if os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    dataset = args.dataset or cfg.get("dataset", "cicids2017")
    input_path = args.input or cfg.get("input_path", f"data/raw/{dataset}")
    output_dir = args.output or cfg.get("output_path", f"data/processed/{dataset}")

    # Handle sample shortcut
    if dataset.lower() == "sample":
        input_path = input_path or "data/samples/sample_network_traffic.csv"
        output_dir = output_dir or "data/processed/sample"

    window_cfg = cfg.get("windowing", {})
    window_size = args.window_size or window_cfg.get("window_size_seconds", 60)
    rolling_count = window_cfg.get("rolling_window_count", 5)

    split_cfg = cfg.get("split", {})
    train_ratio = split_cfg.get("train_ratio", 0.70)
    val_ratio = split_cfg.get("validation_ratio", 0.15)
    test_ratio = split_cfg.get("test_ratio", 0.15)
    seed = split_cfg.get("random_seed", 42)

    prep_cfg = cfg.get("preprocessing", {})
    scaler_type = prep_cfg.get("scaler", "standard")

    print(f"============================================================")
    print(f"SENTRANET PREPROCESSING PIPELINE: {dataset.upper()}")
    print(f"============================================================")
    print(f"Input:       {input_path}")
    print(f"Output:      {output_dir}")
    print(f"Window Size: {window_size}s (Rolling: {rolling_count})")
    print(f"Split:       {int(train_ratio*100)}% Train / {int(val_ratio*100)}% Val / {int(test_ratio*100)}% Test")
    print(f"Scaler:      {scaler_type}")
    print(f"============================================================")

    pipeline = PreprocessingPipeline(
        dataset_name=dataset,
        window_size_seconds=window_size,
        rolling_window_count=rolling_count,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        scaler_type=scaler_type,
        random_seed=seed,
    )

    try:
        metadata = pipeline.run(
            input_path=input_path,
            output_dir=output_dir,
            max_rows=args.max_rows,
            enable_windowing=not args.no_windowing,
        )
        print("\n[SUCCESS] Pipeline completed successfully!")
        print(f"  • Train Records:      {metadata['train_rows']:,}")
        print(f"  • Validation Records: {metadata['validation_rows']:,}")
        print(f"  • Test Records:       {metadata['test_rows']:,}")
        print(f"  • Feature Count:      {metadata['feature_count']}")
        print(f"  • Output Classes:     {metadata['classes']}")
        print(f"  • Class Breakdown:    {metadata['class_distribution']}")
        print(f"  • Runtime:            {metadata['runtime_seconds']}s")
        print(f"\nArtifacts written to: {output_dir}")
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
