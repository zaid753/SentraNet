"""Generates a realistic synthetic network flow sample fixture structured into recurring temporal security cycles."""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_sample_traffic(num_rows: int = 3500, output_path: str = "data/samples/sample_network_traffic.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.random.seed(42)

    base_time = datetime(2026, 9, 30, 8, 0, 0)
    
    # Generate bursty arrival intervals across ~4 hours
    intervals = np.random.exponential(scale=3.5, size=num_rows).clip(0.1, 30.0)
    cumulative_seconds = np.cumsum(intervals)
    timestamps = [base_time + timedelta(seconds=float(s)) for s in cumulative_seconds]

    # IPs
    internal_ips = [f"192.168.1.{i}" for i in range(10, 60)]
    external_ips = [f"203.0.113.{i}" for i in range(1, 40)] + [f"198.51.100.{i}" for i in range(1, 30)]

    src_ips = np.random.choice(internal_ips + external_ips, size=num_rows)
    dst_ips = np.random.choice(internal_ips + external_ips, size=num_rows)

    # Ports
    common_ports = [80, 443, 22, 53, 8080, 21, 3389, 8443]
    high_ports = list(range(49152, 65535, 50))
    src_ports = np.random.choice(high_ports, size=num_rows)
    dst_ports = np.random.choice(common_ports + high_ports[:30], size=num_rows)

    # Protocols (TCP=6, UDP=17, ICMP=1)
    protocols = np.random.choice([6, 17, 1], p=[0.75, 0.20, 0.05], size=num_rows)

    # Base Metrics
    durations = np.random.exponential(scale=450000.0, size=num_rows).clip(50.0, 10000000.0)
    fwd_packets = np.random.poisson(lam=10, size=num_rows) + 1
    bwd_packets = np.random.poisson(lam=8, size=num_rows)
    fwd_bytes = fwd_packets * np.random.randint(40, 1460, size=num_rows)
    bwd_bytes = bwd_packets * np.random.randint(40, 1460, size=num_rows)

    syn_flags = np.random.binomial(n=1, p=0.2, size=num_rows)
    ack_flags = np.random.binomial(n=1, p=0.8, size=num_rows)
    fin_flags = np.random.binomial(n=1, p=0.2, size=num_rows)
    rst_flags = np.random.binomial(n=1, p=0.05, size=num_rows)

    labels = []

    # Two repeating operational cycles across time so that all classes exist in Train, Val, and Test
    # Cycle period is 7,200 seconds (~2 hours)
    for i, s in enumerate(cumulative_seconds):
        cycle_phase = (s % 7200.0) / 7200.0  # 0.0 to 1.0 within cycle

        if cycle_phase < 0.35:
            # Baseline quiet / enterprise operation (70 minutes) -> 95% BENIGN, 5% low probe
            lbl = np.random.choice(["BENIGN", "PortScan"], p=[0.95, 0.05])
        elif 0.35 <= cycle_phase < 0.55:
            # Reconnaissance & Scanning phase (40 minutes) -> 65% PortScan, 35% BENIGN
            lbl = np.random.choice(["PortScan", "BENIGN"], p=[0.65, 0.35])
        elif 0.55 <= cycle_phase < 0.75:
            # Volumetric Attack Surge (40 minutes) -> 75% DDoS, 25% BENIGN
            lbl = np.random.choice(["DDoS", "BENIGN"], p=[0.75, 0.25])
        elif 0.75 <= cycle_phase < 0.90:
            # Infiltration / Botnet C2 phase (30 minutes) -> 55% Bot, 25% SSH-Patator, 20% BENIGN
            lbl = np.random.choice(["Bot", "SSH-Patator", "BENIGN"], p=[0.55, 0.25, 0.20])
        else:
            # Recovery / Normal Baseline (20 minutes) -> 95% BENIGN, 5% Bot
            lbl = np.random.choice(["BENIGN", "Bot"], p=[0.95, 0.05])

        labels.append(lbl)

        # Inject attack-specific flow signatures
        if lbl == "DDoS":
            fwd_packets[i] = np.random.randint(150, 700)
            bwd_packets[i] = np.random.randint(0, 3)
            fwd_bytes[i] = fwd_packets[i] * np.random.randint(800, 1400)
            durations[i] = np.random.uniform(5000.0, 150000.0)
            syn_flags[i] = 1
        elif lbl == "PortScan":
            fwd_packets[i] = np.random.randint(1, 3)
            bwd_packets[i] = 0
            durations[i] = np.random.uniform(20.0, 300.0)
            syn_flags[i] = 1
            ack_flags[i] = 0
        elif lbl == "Bot":
            fwd_packets[i] = np.random.randint(5, 25)
            bwd_packets[i] = np.random.randint(5, 25)
            durations[i] = np.random.uniform(1000000.0, 5000000.0)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "source_ip": src_ips,
        "destination_ip": dst_ips,
        "source_port": src_ports,
        "destination_port": dst_ports,
        "protocol": protocols,
        "flow_duration": durations,
        "total_fwd_packets": fwd_packets,
        "total_backward_packets": bwd_packets,
        "total_length_of_fwd_packets": fwd_bytes,
        "total_length_of_bwd_packets": bwd_bytes,
        "syn_flag_count": syn_flags,
        "ack_flag_count": ack_flags,
        "fin_flag_count": fin_flags,
        "rst_flag_count": rst_flags,
        "label": labels,
    })

    # Add edge-case rows for cleaner verification
    df.loc[15, "flow_duration"] = np.inf
    df.loc[30, "total_fwd_packets"] = np.nan
    df = pd.concat([df, df.iloc[[75, 150]]], ignore_index=True)

    df.to_csv(output_path, index=False)
    print(f"[OK] Generated {len(df)} cyclic episodic sample rows to {output_path}")

if __name__ == "__main__":
    generate_sample_traffic()
