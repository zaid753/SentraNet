import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.window_aggregator import WindowAggregator

class CICIDS2017Adapter:
    """
    Adapter for processing the real CIC-IDS2017 GeneratedLabelledFlows dataset.
    Converts raw CSV flow logs into canonical 17-feature temporal windows.
    """

    LABEL_MAPPING = {
        'BENIGN': 'BENIGN',
        'Bot': 'BOTNET',
        'DDoS': 'DDOS',
        'DoS GoldenEye': 'DDOS',
        'DoS Hulk': 'DDOS',
        'DoS Slowhttptest': 'DDOS',
        'DoS slowloris': 'DDOS',
        'FTP-Patator': 'OTHER_ATTACK',
        'SSH-Patator': 'OTHER_ATTACK',
        'PortScan': 'SCANNING',
        'Infiltration': 'OTHER_ATTACK',
        'Heartbleed': 'OTHER_ATTACK',
        'Web Attack \u2013 Brute Force': 'OTHER_ATTACK',
        'Web Attack \u2013 Sql Injection': 'OTHER_ATTACK',
        'Web Attack \u2013 XSS': 'OTHER_ATTACK',
        'Web Attack  Brute Force': 'OTHER_ATTACK',
        'Web Attack  Sql Injection': 'OTHER_ATTACK',
        'Web Attack  XSS': 'OTHER_ATTACK',
    }

    def __init__(self, window_size_seconds: int = 60):
        self.window_size_seconds = window_size_seconds
        self.aggregator = WindowAggregator(window_size_seconds=window_size_seconds)

    def process_file_to_windows(self, csv_path: str) -> pd.DataFrame:
        """
        Reads a single CIC-IDS2017 CSV file, sorts it chronologically, 
        and builds SENTRANET temporal windows.
        """
        self.aggregator.reset()
        
        print(f"Loading {csv_path}...")
        df_raw = pd.read_csv(csv_path, encoding="cp1252", skipinitialspace=True)
        
        print("Parsing timestamps...")
        df_raw['Timestamp'] = pd.to_datetime(df_raw['Timestamp'], format="mixed", dayfirst=True)
        
        print("Sorting chronologically...")
        df_raw = df_raw.sort_values(by='Timestamp').reset_index(drop=True)
        
        windows = []
        current_window_labels = []
        
        # We manually drive the aggregation so we can track labels
        for idx, row in df_raw.iterrows():
            lbl = str(row.get('Label', 'BENIGN'))
            mapped_lbl = self.LABEL_MAPPING.get(lbl, 'OTHER_ATTACK') if lbl != 'BENIGN' else 'BENIGN'
            
            try:
                # Flow Duration is in microseconds
                dur_sec = max(0.0, float(row['Flow Duration']) / 1e6)
                
                record = FlowRecord(
                    timestamp=row['Timestamp'].isoformat(),
                    src_ip=str(row['Source IP']),
                    dst_ip=str(row['Destination IP']),
                    src_port=int(row['Source Port']),
                    dst_port=int(row['Destination Port']),
                    protocol=str(row['Protocol']),
                    duration_seconds=dur_sec,
                    packets=int(row['Total Fwd Packets'] + row['Total Backward Packets']),
                    bytes=float(row['Total Length of Fwd Packets'] + row['Total Length of Bwd Packets']),
                    tcp_flags=f"SYN:{row.get('SYN Flag Count',0)},ACK:{row.get('ACK Flag Count',0)}"
                )
            except Exception as e:
                continue

            completed, window_ts, features = self.aggregator.add_flow(record)
            
            if completed and features is not None:
                # Derive window label: if any malicious flow, it's malicious. 
                # Pick the most severe/frequent malicious label, or just the first non-benign.
                malicious = [l for l in current_window_labels if l != 'BENIGN']
                window_label = malicious[0] if malicious else 'BENIGN'
                
                window_data = {"window_start": window_ts, "label": window_label}
                window_data.update(features)
                windows.append(window_data)
                
                # Reset current window labels
                current_window_labels = []
                
            current_window_labels.append(mapped_lbl)
            
        # Flush the last window
        completed, window_ts, features = self.aggregator.flush()
        if completed and features is not None:
            malicious = [l for l in current_window_labels if l != 'BENIGN']
            window_label = malicious[0] if malicious else 'BENIGN'
            window_data = {"window_start": window_ts, "label": window_label}
            window_data.update(features)
            windows.append(window_data)

        df_windows = pd.DataFrame(windows)
        print(f"Produced {len(df_windows)} windows.")
        return df_windows

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Compile CIC-IDS2017 CSV to SENTRANET Parquet")
    parser.add_argument("--input", required=True, help="Path to raw CSV file")
    parser.add_argument("--output", required=True, help="Path to output Parquet file")
    
    args = parser.parse_args()
    
    adapter = CICIDS2017Adapter()
    df = adapter.process_file_to_windows(args.input)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_parquet(args.output, index=False)
    print(f"Saved dataset to {args.output}")
