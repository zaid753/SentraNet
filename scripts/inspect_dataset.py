#!/usr/bin/env python3
"""
SENTRANET — Dataset Inspection Tool
Usage:
    python scripts/inspect_dataset.py --dataset cicids2017 [--input data/raw/cicids2017]
"""

import sys
import os
import argparse

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.evaluation.dataset_report import DatasetInspector
from ml.data.registry import DatasetRegistry

def main():
    parser = argparse.ArgumentParser(description="Inspect raw or sample network security datasets for SENTRANET.")
    parser.add_argument("--dataset", type=str, default="cicids2017", help="Dataset identifier (e.g. cicids2017, unsw_nb15, cic_ddos2019, sample)")
    parser.add_argument("--input", type=str, default=None, help="Path to raw dataset folder or file")
    parser.add_argument("--max-rows", type=int, default=100000, help="Max sample rows to read for inspection")

    args = parser.parse_args()

    # Determine default path if not explicitly provided
    input_path = args.input
    if not input_path:
        if args.dataset.lower() == "sample":
            input_path = "data/samples/sample_network_traffic.csv"
        else:
            input_path = f"data/raw/{args.dataset.lower()}"

    inspector = DatasetInspector(args.dataset, input_path)
    report = inspector.inspect(max_sample_rows=args.max_rows)
    print(DatasetInspector.format_human_readable(report))

if __name__ == "__main__":
    main()
