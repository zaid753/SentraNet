#!/usr/bin/env python3
"""
SENTRANET — Forecast Scenario Generator (Phase 9)
Generates a deterministic dataset designed explicitly to evaluate temporal forecast precursor lead times.
"""

import os
import pandas as pd
from backend.telemetry.synthetic_source import SyntheticFlowSource

def generate_forecast_scenario(output_path: str = "data/samples/forecast_scenario.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 0-1800s scenario length
    # Let's generate ~6000 flows over 30 minutes
    source = SyntheticFlowSource(seed=42, profile="forecastable_escalation")
    
    records = []
    
    # We want to run the simulation until 30 minutes (1800 seconds) have elapsed
    # Actually, we can generate a bit more to ensure the window aggregator has enough data.
    # We'll run it up to 2000 seconds.
    while source.elapsed_seconds < 2000.0:
        rec = source.read()
        
        # We must assign the correct labels based on the elapsed time
        # profile in synthetic_source:
        # 0-300: BASELINE (BENIGN)
        # 300-600: EARLY_PRECURSOR (BENIGN)
        # 600-900: MILD_ESCALATION (BENIGN or maybe scanning? we'll call it BENIGN because it's precursor)
        # 900-1200: STRONGER_ESCALATION (BENIGN)
        # 1200-1500: SCANNING (PortScan)
        # 1500-1800: DDOS (DDoS)
        
        elapsed = source.elapsed_seconds
        
        if elapsed < 1200.0:
            label = "BENIGN"
        elif elapsed < 1500.0:
            label = "PortScan"
        elif elapsed < 1800.0:
            label = "DDoS"
        else:
            label = "BENIGN"
            
        records.append({
            "timestamp": rec.timestamp,
            "source_ip": rec.src_ip,
            "destination_ip": rec.dst_ip,
            "source_port": rec.src_port,
            "destination_port": rec.dst_port,
            "protocol": 6 if rec.protocol == "TCP" else (17 if rec.protocol == "UDP" else 1),
            "flow_duration": rec.duration_seconds * 1_000_000, # ms or micro? Preprocessing expects microseconds
            "total_fwd_packets": rec.packets,
            "total_backward_packets": 0, # simplified
            "total_length_of_fwd_packets": rec.bytes,
            "total_length_of_bwd_packets": 0,
            "syn_flag_count": 1 if rec.tcp_flags and "SYN" in rec.tcp_flags else 0,
            "ack_flag_count": 1 if rec.tcp_flags and "ACK" in rec.tcp_flags else 0,
            "fin_flag_count": 0,
            "rst_flag_count": 0,
            "label": label,
        })
        
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"[OK] Generated {len(df)} forecast scenario rows to {output_path}")

if __name__ == "__main__":
    generate_forecast_scenario()
