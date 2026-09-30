"""
SENTRANET — Dataset Manifest Generator & Auditor (Phase 10)
Inspects repository for raw benchmark files, records actual availability,
file counts, flow counts, schema status, and official provenance.
"""

from typing import Dict, Any, List, Optional
import os
import json
import hashlib
import pandas as pd
from datetime import datetime, timezone

DATASET_SPECS = {
    "sample": {
        "name": "Synthetic Development Fixture (sample)",
        "category": "Category B — Synthetic Development Fixture",
        "official_source": "SENTRANET internal fixture generator (scripts/generate_sample_data.py)",
        "expected_path": "data/samples/sample_network_traffic.csv",
        "description": "Multi-phase synthetic attack cycles structured into recurring temporal episodes.",
        "required_files": ["sample_network_traffic.csv"],
        "schema_type": "CICIDS2017-like NetFlow features",
        "timestamp_available": True,
        "labels_available": True,
        "classes": ["BENIGN", "PortScan", "DDoS", "Bot", "SSH-Patator"],
    },
    "cicids2017": {
        "name": "CICIDS2017",
        "category": "Category A — Real Benchmark Capture",
        "official_source": "Canadian Institute for Cybersecurity (University of New Brunswick) — https://www.unb.ca/cic/datasets/ids-2017.html",
        "expected_path": "data/raw/cicids2017",
        "description": "Intrusion detection benchmark captured July 2017 containing DoS, DDoS, PortScan, Botnet, and Web attacks.",
        "required_files": [
            "Monday-WorkingHours.pcap_ISCX.csv",
            "Tuesday-WorkingHours.pcap_ISCX.csv",
            "Wednesday-workingHours.pcap_ISCX.csv",
            "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
            "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
            "Friday-WorkingHours-Morning.pcap_ISCX.csv",
            "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
            "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
        ],
        "schema_type": "CICFlowMeter 80+ features",
        "timestamp_available": True,
        "labels_available": True,
        "classes": ["BENIGN", "DDoS", "PortScan", "Bot", "DoS Hulk", "DoS GoldenEye", "FTP-Patator", "SSH-Patator"],
    },
    "unsw_nb15": {
        "name": "UNSW-NB15",
        "category": "Category A — Real Benchmark Capture",
        "official_source": "Cyber Range Lab of the Australian Centre for Cyber Security (UNSW Canberra) — https://research.unsw.edu.au/projects/unsw-nb15-dataset",
        "expected_path": "data/raw/unsw_nb15",
        "description": "Comprehensive network dataset created using the IXIA PerfectStorm tool containing synthetic modern normal activities and attack behaviors.",
        "required_files": [
            "UNSW-NB15_1.csv",
            "UNSW-NB15_2.csv",
            "UNSW-NB15_3.csv",
            "UNSW-NB15_4.csv",
        ],
        "schema_type": "Argus/Bro 49 features",
        "timestamp_available": True,
        "labels_available": True,
        "classes": ["Normal", "Fuzzers", "Analysis", "Backdoors", "DoS", "Exploits", "Generic", "Reconnaissance", "Shellcode", "Worms"],
    },
    "cic_ddos2019": {
        "name": "CIC-DDoS2019",
        "category": "Category A — Real Benchmark Capture",
        "official_source": "Canadian Institute for Cybersecurity (University of New Brunswick) — https://www.unb.ca/cic/datasets/ddos-2019.html",
        "expected_path": "data/raw/cic_ddos2019",
        "description": "DDoS attack evaluation dataset containing reflection/amplification and exploitation DDoS attacks.",
        "required_files": [
            "DrDoS_DNS.csv",
            "DrDoS_LDAP.csv",
            "DrDoS_MSSQL.csv",
            "DrDoS_NetBIOS.csv",
            "DrDoS_NTP.csv",
            "DrDoS_SNMP.csv",
            "DrDoS_SSDP.csv",
            "DrDoS_UDP.csv",
            "Syn.csv",
            "TFTP.csv",
            "UDPLag.csv",
        ],
        "schema_type": "CICFlowMeter 80+ features",
        "timestamp_available": True,
        "labels_available": True,
        "classes": ["BENIGN", "DrDoS_DNS", "DrDoS_LDAP", "DrDoS_MSSQL", "DrDoS_NetBIOS", "Syn", "TFTP", "UDP-lag", "PortScan"],
    },
}


def audit_dataset_availability(dataset_id: str) -> Dict[str, Any]:
    """Audits local availability of a specific dataset and records actual measured statistics."""
    spec = DATASET_SPECS.get(dataset_id)
    if not spec:
        raise ValueError(f"Unknown dataset '{dataset_id}'. Available: {list(DATASET_SPECS.keys())}")

    path = spec["expected_path"]
    manifest_entry = {
        "dataset_id": dataset_id,
        "name": spec["name"],
        "category": spec["category"],
        "official_source": spec["official_source"],
        "expected_path": path,
        "available": False,
        "status": "NOT_AVAILABLE",
        "file_count": 0,
        "available_files": [],
        "missing_files": spec["required_files"],
        "total_bytes": 0,
        "total_rows": 0,
        "timestamp_available": spec["timestamp_available"],
        "labels_available": spec["labels_available"],
        "attack_categories": spec["classes"],
        "download_instructions": f"Download raw benchmark files from {spec['official_source']} into '{path}/'.",
    }

    if not os.path.exists(path):
        return manifest_entry

    if os.path.isfile(path):
        manifest_entry["available"] = True
        manifest_entry["status"] = "AVAILABLE"
        manifest_entry["file_count"] = 1
        manifest_entry["available_files"] = [os.path.basename(path)]
        manifest_entry["missing_files"] = []
        manifest_entry["total_bytes"] = os.path.getsize(path)

        # Quick row count check
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                manifest_entry["total_rows"] = sum(1 for _ in f) - 1
        except Exception:
            manifest_entry["total_rows"] = 0

        return manifest_entry

    # Path is directory
    all_files = [f for f in os.listdir(path) if f.endswith(".csv") or f.endswith(".parquet")]
    if not all_files:
        return manifest_entry

    manifest_entry["file_count"] = len(all_files)
    manifest_entry["available_files"] = sorted(all_files)
    manifest_entry["missing_files"] = [f for f in spec["required_files"] if f not in all_files]
    manifest_entry["total_bytes"] = sum(os.path.getsize(os.path.join(path, f)) for f in all_files)

    if manifest_entry["missing_files"]:
        manifest_entry["available"] = True
        manifest_entry["status"] = "PARTIALLY_AVAILABLE"
    else:
        manifest_entry["available"] = True
        manifest_entry["status"] = "AVAILABLE"

    # Count rows across available files
    total_r = 0
    for f in all_files:
        fp = os.path.join(path, f)
        try:
            if f.endswith(".parquet"):
                df_p = pd.read_parquet(fp)
                total_r += len(df_p)
            else:
                with open(fp, "r", encoding="utf-8", errors="ignore") as file_obj:
                    total_r += max(0, sum(1 for _ in file_obj) - 1)
        except Exception:
            pass
    manifest_entry["total_rows"] = total_r

    return manifest_entry


def generate_manifest(output_path: str = "data/dataset_manifest.json") -> Dict[str, Any]:
    """Generates the comprehensive dataset manifest for all supported benchmarks."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "SENTRANET",
        "phase": "Phase 10 — Benchmark Evaluation & Empirical Validation",
        "datasets": {},
    }

    for d_id in DATASET_SPECS.keys():
        manifest["datasets"][d_id] = audit_dataset_availability(d_id)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest
