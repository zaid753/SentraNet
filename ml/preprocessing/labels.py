"""Label normalization and dataset-specific attack class mapping for SENTRANET."""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger("sentranet.labels")

# Canonical SENTRANET target classes
TARGET_CLASSES: List[str] = [
    "BENIGN",
    "DDOS",
    "SCANNING",
    "BOTNET",
    "OTHER_ATTACK",
]

# CICIDS2017 explicit label mappings
CICIDS2017_LABEL_MAP: Dict[str, str] = {
    # Benign
    "benign": "BENIGN",
    
    # Denial of Service / Distributed DoS
    "ddos": "DDOS",
    "dos slowloris": "DDOS",
    "dos slowhttptest": "DDOS",
    "dos hulk": "DDOS",
    "dos goldeneye": "DDOS",
    "heartbleed": "DDOS",
    
    # Scanning & Reconnaissance
    "portscan": "SCANNING",
    
    # Botnet
    "bot": "BOTNET",
    
    # Web & Infiltration & Brute Force -> OTHER_ATTACK
    "ftp-patator": "OTHER_ATTACK",
    "ssh-patator": "OTHER_ATTACK",
    "web attack – brute force": "OTHER_ATTACK",
    "web attack – xss": "OTHER_ATTACK",
    "web attack – sql injection": "OTHER_ATTACK",
    "web attack - brute force": "OTHER_ATTACK",
    "web attack - xss": "OTHER_ATTACK",
    "web attack - sql injection": "OTHER_ATTACK",
    "infiltration": "OTHER_ATTACK",
    "other_attack": "OTHER_ATTACK",
}

# UNSW-NB15 explicit label mappings
UNSW_NB15_LABEL_MAP: Dict[str, str] = {
    "normal": "BENIGN",
    "dos": "DDOS",
    "backdoor": "DDOS",
    "reconnaissance": "SCANNING",
    "generic": "OTHER_ATTACK",
    "exploits": "OTHER_ATTACK",
    "fuzzers": "OTHER_ATTACK",
    "analysis": "OTHER_ATTACK",
    "worms": "OTHER_ATTACK",
    "other_attack": "OTHER_ATTACK",
}

# CIC-DDoS2019 explicit label mappings
CIC_DDOS2019_LABEL_MAP: Dict[str, str] = {
    "benign": "BENIGN",
    "drdos_dns": "DDOS",
    "drdos_ldap": "DDOS",
    "drdos_mssql": "DDOS",
    "drdos_netbios": "DDOS",
    "drdos_ntp": "DDOS",
    "drdos_snmp": "DDOS",
    "drdos_ssdp": "DDOS",
    "drdos_udp": "DDOS",
    "syn": "DDOS",
    "tftp": "DDOS",
    "udp-lag": "DDOS",
    "portscan": "SCANNING",
    "other_attack": "OTHER_ATTACK",
}

DATASET_LABEL_MAPS: Dict[str, Dict[str, str]] = {
    "cicids2017": CICIDS2017_LABEL_MAP,
    "unsw_nb15": UNSW_NB15_LABEL_MAP,
    "cic_ddos2019": CIC_DDOS2019_LABEL_MAP,
}

def normalize_label(label: any, dataset: Optional[str] = None) -> str:
    """
    Normalizes a dataset-specific raw label into canonical SENTRANET classes:
    BENIGN, DDOS, SCANNING, BOTNET, or OTHER_ATTACK.
    
    Strict Rule: Unmapped or unrecognized labels default to OTHER_ATTACK,
    NEVER silently to BENIGN.
    """
    if label is None:
        return "OTHER_ATTACK"

    raw_str = str(label).strip()
    cleaned = raw_str.lower()
    
    # Check if already canonical
    if cleaned in ["benign", "ddos", "scanning", "botnet", "other_attack"]:
        return cleaned.upper()

    # Check dataset-specific map first if provided
    if dataset:
        ds_key = dataset.lower().replace("-", "_")
        mapping = DATASET_LABEL_MAPS.get(ds_key)
        if mapping and cleaned in mapping:
            return mapping[cleaned]

    # Global fallback lookup
    for mapping in DATASET_LABEL_MAPS.values():
        if cleaned in mapping:
            return mapping[cleaned]

    # Fuzzy matches
    if "benign" in cleaned or "normal" in cleaned:
        return "BENIGN"
    if "ddos" in cleaned or "dos" in cleaned or "syn" in cleaned or "udp" in cleaned or "flood" in cleaned:
        return "DDOS"
    if "scan" in cleaned or "recon" in cleaned or "probe" in cleaned:
        return "SCANNING"
    if "bot" in cleaned or "zombie" in cleaned:
        return "BOTNET"

    # Strict rule: Unmapped attacks go to OTHER_ATTACK
    logger.warning(f"Unmapped label '{raw_str}' mapped to OTHER_ATTACK (never silently mapped to BENIGN)")
    return "OTHER_ATTACK"
