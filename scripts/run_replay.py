#!/usr/bin/env python3
"""
SENTRANET — Phase 6 Historical Dataset Replay & Alerting CLI Tool
Streams chronological temporal windows, runs Phase 3-5 ML pipelines,
and drives the Phase 6 Alert State Machine and Incident Manager.
"""

import os
import sys
import argparse

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.replay.replay_runner import ReplayRunner

def main():
    parser = argparse.ArgumentParser(description="SENTRANET Historical Replay & Incident Alerting Streamer")
    parser.add_argument("--mode", type=str, default="batch", choices=["batch", "realtime", "step"], help="Replay mode (batch, realtime, step)")
    parser.add_argument("--speed", type=float, default=10.0, help="Speed multiplier for realtime simulation (e.g. 10)")
    parser.add_argument("--dataset", type=str, default="data/processed/sample/validation.parquet", help="Path to parquet dataset or 'full'")
    parser.add_argument("--max-windows", type=int, default=None, help="Maximum number of temporal windows to process")
    parser.add_argument("--verbose", action="store_true", help="Print detailed state for every temporal window")

    args = parser.parse_args()

    runner = ReplayRunner()
    runner.run(
        dataset_path=args.dataset,
        mode=args.mode,
        speed=args.speed,
        max_windows=args.max_windows,
        verbose=args.verbose,
    )

if __name__ == "__main__":
    main()
