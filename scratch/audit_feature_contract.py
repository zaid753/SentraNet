import os
import json
import joblib
import pandas as pd
import numpy as np
import glob

def run_audit():
    out = {}

    # 1. ACTUAL TRAINING DISTRIBUTION
    train_path = "data/processed/sample/train.parquet"
    if os.path.exists(train_path):
        train_df = pd.read_parquet(train_path)
        out["training"] = {
            "dataset": train_path,
            "samples": len(train_df),
            "label_distribution": train_df["label"].value_counts().to_dict(),
        }
    else:
        out["training"] = {"error": "Training dataset not found."}

    # Scaler
    scaler_paths = ["models/scaler/sentranet_scaler.joblib", "data/processed/sample/artifacts/scaler.joblib"]
    scaler = None
    scaler_path_used = None
    for sp in scaler_paths:
        if os.path.exists(sp):
            scaler = joblib.load(sp)
            scaler_path_used = sp
            break
            
    out["training"]["scaler_used"] = scaler_path_used
    out["training"]["scaler_type"] = type(scaler).__name__ if scaler else "Unknown"
    
    # 2. AUDIT 17 FEATURES
    cic_path = "data/processed/cicids2017/Friday-WorkingHours-Morning.parquet"
    cic_df = pd.read_parquet(cic_path)
    
    features = [
        "flow_count", "total_packets", "total_bytes", "avg_packet_rate",
        "avg_byte_rate", "unique_sources", "unique_destinations",
        "avg_packet_size", "avg_flow_duration", "syn_flag_count",
        "ack_flag_count", "privileged_port_ratio", "rolling_5_flow_count",
        "rolling_5_total_packets", "rolling_5_total_bytes",
        "rolling_5_avg_byte_rate", "rolling_5_unique_sources"
    ]
    
    out["training"]["feature_order"] = features
    
    feature_audit = {}
    for f in features:
        if f in train_df.columns and f in cic_df.columns:
            train_vals = train_df[f]
            cic_vals = cic_df[f]
            feature_audit[f] = {
                "train": {
                    "min": float(train_vals.min()),
                    "p25": float(np.percentile(train_vals, 25)),
                    "median": float(np.median(train_vals)),
                    "mean": float(train_vals.mean()),
                    "p75": float(np.percentile(train_vals, 75)),
                    "p99": float(np.percentile(train_vals, 99)),
                    "max": float(train_vals.max()),
                    "std": float(train_vals.std())
                },
                "cic": {
                    "min": float(cic_vals.min()),
                    "p25": float(np.percentile(cic_vals, 25)),
                    "median": float(np.median(cic_vals)),
                    "mean": float(cic_vals.mean()),
                    "p75": float(np.percentile(cic_vals, 75)),
                    "p99": float(np.percentile(cic_vals, 99)),
                    "max": float(cic_vals.max()),
                    "std": float(cic_vals.std())
                }
            }
            
            # Semantic compatibility evaluation heuristically
            feature_audit[f]["compatibility"] = "UNCERTAIN"
            
    out["features"] = feature_audit
    
    # 4. SCALER AUDIT
    if scaler:
        if isinstance(scaler, dict):
            actual_scaler = scaler.get('scaler')
        else:
            actual_scaler = scaler
            
        if actual_scaler:
            if hasattr(actual_scaler, 'feature_names_in_'):
                out["scaler"] = {"feature_names_in": list(actual_scaler.feature_names_in_)}
            else:
                out["scaler"] = {"feature_names_in": "Unknown"}
                
            scaled_cic = actual_scaler.transform(cic_df[features])
            out["scaler"]["transformed_cic_ranges"] = {}
            for i, f in enumerate(features):
                out["scaler"]["transformed_cic_ranges"][f] = {
                    "min": float(scaled_cic[:, i].min()),
                    "max": float(scaled_cic[:, i].max()),
                    "mean": float(scaled_cic[:, i].mean()),
                    "std": float(scaled_cic[:, i].std())
                }

    # 6. LABEL COVERAGE & 7. TEMPORAL COVERAGE
    raw_files = glob.glob("data/raw/cicids2017/TrafficLabelling /*.csv")
    coverage = {}
    total_flows = 0
    for file in raw_files:
        filename = os.path.basename(file)
        # We will just do a quick count of lines via pandas chunking
        try:
            chunks = pd.read_csv(file, usecols=["Label", "Timestamp"], chunksize=100000, encoding="cp1252", skipinitialspace=True)
            labels = {}
            for chunk in chunks:
                total_flows += len(chunk)
                counts = chunk["Label"].value_counts().to_dict()
                for k, v in counts.items():
                    labels[str(k)] = labels.get(str(k), 0) + v
            coverage[filename] = {"labels": labels}
        except Exception as e:
            coverage[filename] = {"error": str(e)}

    out["coverage"] = {
        "files": [os.path.basename(f) for f in raw_files],
        "total_flows": total_flows,
        "details": coverage
    }
    
    with open("scratch/audit_report.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_audit()
