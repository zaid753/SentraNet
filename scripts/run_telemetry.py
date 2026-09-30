#!/usr/bin/env python3
"""
SENTRANET — Phase 9 Telemetry Ingestion & Stream Processing CLI Tool
Simulates flow metadata telemetry (synthetic or replay), runs 60-second temporal aggregation,
and executes the SENTRANET AI Core inference pipeline.
"""

import os
import sys
import time
import argparse

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.telemetry.synthetic_source import SyntheticFlowSource, VALID_PROFILES
from backend.telemetry.flow_sources import ReplayFlowSource, FileFlowSource
from backend.telemetry.stream_processor import StreamProcessor


def main():
    parser = argparse.ArgumentParser(
        description="SENTRANET Network Telemetry Ingestion & Feature Aggregation CLI"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="synthetic",
        choices=["synthetic", "replay", "file"],
        help="Telemetry source: synthetic, replay, or file",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=10.0,
        help="Speed multiplier for simulation (e.g. 10.0)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic random seed for synthetic flow generation",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="scenario_1",
        choices=list(VALID_PROFILES),
        help="Synthetic behavioral profile or temporal scenario",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration of simulation in seconds (default: 10s)",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Input CSV/JSONL file path when using file source",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose details for every flow and window",
    )

    args = parser.parse_args()

    print("=" * 65)
    print(" SENTRANET — Network Telemetry Ingestion Layer (Phase 9)")
    print(" Tagline: 'From detecting attacks to forecasting them.'")
    print("=" * 65)
    print(f" Source type       : {args.source.upper()}")
    print(f" Speed multiplier  : {args.speed}x")
    print(f" Seed              : {args.seed}")
    print(f" Profile           : {args.profile}")
    print(f" Target duration   : {args.duration}s")
    print("-" * 65)

    processor = StreamProcessor()
    processor.reset()

    # Source selection
    if args.source == "synthetic":
        source = SyntheticFlowSource(seed=args.seed, profile=args.profile)
        source_type_label = "synthetic"
    elif args.source == "replay":
        source = ReplayFlowSource(file_path=args.file)
        source_type_label = "historical"
    else:
        if not args.file:
            print("Error: --file argument required when source is 'file'.")
            sys.exit(1)
        source = FileFlowSource(file_path=args.file)
        source_type_label = "historical"

    start_wall_time = time.time()
    flows_count = 0
    windows_count = 0

    print("Streaming flow records...")

    try:
        while True:
            elapsed_wall = time.time() - start_wall_time
            if args.duration and elapsed_wall >= args.duration:
                print(f"\n[CLI] Reached requested duration of {args.duration}s. Halting stream.")
                break

            flow = source.read()
            if flow is None:
                print("\n[CLI] End of telemetry stream reached.")
                break

            flows_count += 1
            res = processor.ingest_flow(flow, source_type=source_type_label)

            if res.get("window_complete", False):
                windows_count += 1
                decision = res.get("decision", {})
                attack = decision.get("attack_class", "UNKNOWN")
                risk = decision.get("risk_score", 0.0)
                print(
                    f"  [WINDOW {windows_count:03d}] {res.get('window')} | "
                    f"Flows: {res.get('flows_in_window', 0):3d} | "
                    f"Class: {attack:<12} | Risk: {risk:.3f}"
                )
            elif args.verbose:
                print(
                    f"  [FLOW {flows_count:05d}] {flow.timestamp} | {flow.src_ip}:{flow.src_port} -> "
                    f"{flow.dst_ip}:{flow.dst_port} | {flow.protocol} ({flow.bytes:.0f} B)"
                )

            # Sleep pacing
            sleep_sec = max(0.0005, 0.05 / args.speed)
            time.sleep(sleep_sec)

    except KeyboardInterrupt:
        print("\n[CLI] Streaming interrupted by user.")

    # Flush partial window upon exit
    flush_res = processor.flush()
    if flush_res.get("flushed", False):
        windows_count += 1
        decision = flush_res.get("decision", {})
        attack = decision.get("attack_class", "UNKNOWN")
        risk = decision.get("risk_score", 0.0)
        print(
            f"  [FLUSHED]    {flush_res.get('window')} | "
            f"Class: {attack:<12} | Risk: {risk:.3f}"
        )

    total_time = round(time.time() - start_wall_time, 2)
    print("=" * 65)
    print(" TELEMETRY STREAM SUMMARY")
    print("=" * 65)
    print(f" Execution time     : {total_time}s")
    print(f" Total flows        : {flows_count}")
    print(f" Completed windows  : {windows_count}")
    print(f" Flow ingestion rate: {flows_count / total_time:.1f} flows/sec")
    print("=" * 65)


if __name__ == "__main__":
    main()
