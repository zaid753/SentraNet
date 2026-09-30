"""
SENTRANET — Feature Metadata (Phase 11)
Canonical metadata for all 17 SENTRANET features.

Every field is factual — no domain claims beyond what the feature measures.
"""

from typing import Dict, Any

# ──────────────────────────────────────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────────────────────────────────────
CATEGORY_TRAFFIC_VOLUME = "TRAFFIC_VOLUME"
CATEGORY_PACKET_METRICS = "PACKET_METRICS"
CATEGORY_HOST_DIVERSITY = "HOST_DIVERSITY"
CATEGORY_FLOW_BEHAVIOR = "FLOW_BEHAVIOR"
CATEGORY_TCP_BEHAVIOR = "TCP_BEHAVIOR"
CATEGORY_PORT_BEHAVIOR = "PORT_BEHAVIOR"
CATEGORY_ROLLING_VOLUME = "ROLLING_VOLUME"
CATEGORY_ROLLING_RATE = "ROLLING_RATE"
CATEGORY_ROLLING_DIVERSITY = "ROLLING_DIVERSITY"

# ──────────────────────────────────────────────────────────────────────────────
# Canonical Feature Metadata
# Keys match exactly the 17 SENTRANET canonical feature names.
# ──────────────────────────────────────────────────────────────────────────────
FEATURE_METADATA: Dict[str, Dict[str, Any]] = {
    "flow_count": {
        "display_name": "Flow Count",
        "description": "Number of distinct network flows observed in the current 60-second window.",
        "unit": "flows",
        "category": CATEGORY_TRAFFIC_VOLUME,
        "higher_means": "More flows (higher network activity).",
        "index": 0,
    },
    "total_packets": {
        "display_name": "Total Packets",
        "description": "Total number of packets across all flows in the window.",
        "unit": "packets",
        "category": CATEGORY_TRAFFIC_VOLUME,
        "higher_means": "More packets transmitted.",
        "index": 1,
    },
    "total_bytes": {
        "display_name": "Total Bytes",
        "description": "Total bytes transferred across all flows in the window.",
        "unit": "bytes",
        "category": CATEGORY_TRAFFIC_VOLUME,
        "higher_means": "Higher data volume.",
        "index": 2,
    },
    "avg_packet_rate": {
        "display_name": "Avg Packet Rate",
        "description": "Average packets per second across flows in the window.",
        "unit": "packets/sec",
        "category": CATEGORY_PACKET_METRICS,
        "higher_means": "Higher packet transmission rate.",
        "index": 3,
    },
    "avg_byte_rate": {
        "display_name": "Avg Byte Rate",
        "description": "Average bytes per second across flows in the window.",
        "unit": "bytes/sec",
        "category": CATEGORY_PACKET_METRICS,
        "higher_means": "Higher data rate.",
        "index": 4,
    },
    "unique_sources": {
        "display_name": "Unique Sources",
        "description": "Number of distinct source IP addresses observed in the window.",
        "unit": "IPs",
        "category": CATEGORY_HOST_DIVERSITY,
        "higher_means": "More distinct source hosts communicating.",
        "index": 5,
    },
    "unique_destinations": {
        "display_name": "Unique Destinations",
        "description": "Number of distinct destination IP addresses observed in the window.",
        "unit": "IPs",
        "category": CATEGORY_HOST_DIVERSITY,
        "higher_means": "More distinct destination hosts targeted.",
        "index": 6,
    },
    "avg_packet_size": {
        "display_name": "Avg Packet Size",
        "description": "Average packet size in bytes across all flows in the window.",
        "unit": "bytes",
        "category": CATEGORY_PACKET_METRICS,
        "higher_means": "Larger average payload size.",
        "index": 7,
    },
    "avg_flow_duration": {
        "display_name": "Avg Flow Duration",
        "description": "Average duration of individual flows in the window.",
        "unit": "seconds",
        "category": CATEGORY_FLOW_BEHAVIOR,
        "higher_means": "Longer-lived connections on average.",
        "index": 8,
    },
    "syn_flag_count": {
        "display_name": "SYN Flag Count",
        "description": "Total count of TCP SYN flags observed across all flows in the window.",
        "unit": "flags",
        "category": CATEGORY_TCP_BEHAVIOR,
        "higher_means": "More TCP connection initiation attempts.",
        "index": 9,
    },
    "ack_flag_count": {
        "display_name": "ACK Flag Count",
        "description": "Total count of TCP ACK flags observed across all flows in the window.",
        "unit": "flags",
        "category": CATEGORY_TCP_BEHAVIOR,
        "higher_means": "More TCP acknowledgment activity.",
        "index": 10,
    },
    "privileged_port_ratio": {
        "display_name": "Privileged Port Ratio",
        "description": "Ratio of flows using privileged destination ports (< 1024) to all flows.",
        "unit": "ratio [0–1]",
        "category": CATEGORY_PORT_BEHAVIOR,
        "higher_means": "Greater proportion of flows targeting system/privileged ports.",
        "index": 11,
    },
    "rolling_5_flow_count": {
        "display_name": "5-Window Rolling Flow Count",
        "description": "Average flow count over the preceding 5 windows (causal rolling average).",
        "unit": "flows",
        "category": CATEGORY_ROLLING_VOLUME,
        "higher_means": "Sustained higher flow activity over the recent history.",
        "index": 12,
    },
    "rolling_5_total_packets": {
        "display_name": "5-Window Rolling Total Packets",
        "description": "Average total packet count over the preceding 5 windows.",
        "unit": "packets",
        "category": CATEGORY_ROLLING_VOLUME,
        "higher_means": "Sustained higher packet activity over the recent history.",
        "index": 13,
    },
    "rolling_5_total_bytes": {
        "display_name": "5-Window Rolling Total Bytes",
        "description": "Average total bytes transferred over the preceding 5 windows.",
        "unit": "bytes",
        "category": CATEGORY_ROLLING_VOLUME,
        "higher_means": "Sustained higher data volume over the recent history.",
        "index": 14,
    },
    "rolling_5_avg_byte_rate": {
        "display_name": "5-Window Rolling Avg Byte Rate",
        "description": "Average byte rate over the preceding 5 windows.",
        "unit": "bytes/sec",
        "category": CATEGORY_ROLLING_RATE,
        "higher_means": "Sustained higher data rate over the recent history.",
        "index": 15,
    },
    "rolling_5_unique_sources": {
        "display_name": "5-Window Rolling Unique Sources",
        "description": "Average number of unique source IPs over the preceding 5 windows.",
        "unit": "IPs",
        "category": CATEGORY_ROLLING_DIVERSITY,
        "higher_means": "Sustained higher source diversity over the recent history.",
        "index": 16,
    },
}

# Ordered canonical feature list (17 features, phase-invariant)
CANONICAL_FEATURES = [
    "flow_count",
    "total_packets",
    "total_bytes",
    "avg_packet_rate",
    "avg_byte_rate",
    "unique_sources",
    "unique_destinations",
    "avg_packet_size",
    "avg_flow_duration",
    "syn_flag_count",
    "ack_flag_count",
    "privileged_port_ratio",
    "rolling_5_flow_count",
    "rolling_5_total_packets",
    "rolling_5_total_bytes",
    "rolling_5_avg_byte_rate",
    "rolling_5_unique_sources",
]

assert len(CANONICAL_FEATURES) == 17, "Feature contract violation"
assert set(CANONICAL_FEATURES) == set(FEATURE_METADATA.keys()), "Metadata mismatch"


def get_feature_meta(feature_name: str) -> Dict[str, Any]:
    """Returns metadata for a canonical feature. Raises KeyError if unknown."""
    if feature_name not in FEATURE_METADATA:
        raise KeyError(f"Unknown feature '{feature_name}'. Not in canonical 17-feature schema.")
    return FEATURE_METADATA[feature_name]


def get_display_name(feature_name: str) -> str:
    """Returns the human-readable display name for a feature."""
    return FEATURE_METADATA.get(feature_name, {}).get("display_name", feature_name)
