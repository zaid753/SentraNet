"""Canonical SENTRANET network-flow schema definition and normalization layer."""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

@dataclass
class CanonicalField:
    name: str
    dtype: str
    category: str  # "AVAILABLE", "OPTIONAL", "DERIVED", "IDENTIFIER", "LABEL"
    description: str
    default_value: Optional[any] = None

# Canonical fields definitions
CANONICAL_SCHEMA: Dict[str, CanonicalField] = {
    # Identifiers & Context (Retained for grouping/analysis, NOT raw continuous model features)
    "timestamp": CanonicalField("timestamp", "datetime64[ns]", "AVAILABLE", "Timestamp of network flow occurrence"),
    "source_ip": CanonicalField("source_ip", "string", "IDENTIFIER", "Source IP address"),
    "destination_ip": CanonicalField("destination_ip", "string", "IDENTIFIER", "Destination IP address"),
    "source_port": CanonicalField("source_port", "int64", "AVAILABLE", "Source port number", 0),
    "destination_port": CanonicalField("destination_port", "int64", "AVAILABLE", "Destination port number", 0),
    "protocol": CanonicalField("protocol", "string", "AVAILABLE", "Transport protocol (e.g. TCP, UDP, ICMP)", "TCP"),
    
    # Core Flow Metrics
    "flow_duration": CanonicalField("flow_duration", "float64", "AVAILABLE", "Duration of flow in microseconds or seconds", 0.0),
    "forward_packet_count": CanonicalField("forward_packet_count", "int64", "AVAILABLE", "Packets sent in forward direction", 0),
    "backward_packet_count": CanonicalField("backward_packet_count", "int64", "AVAILABLE", "Packets sent in backward direction", 0),
    "total_packet_count": CanonicalField("total_packet_count", "int64", "DERIVED", "Total packets in flow", 0),
    "forward_bytes": CanonicalField("forward_bytes", "float64", "AVAILABLE", "Total payload/header bytes in forward direction", 0.0),
    "backward_bytes": CanonicalField("backward_bytes", "float64", "AVAILABLE", "Total payload/header bytes in backward direction", 0.0),
    "total_bytes": CanonicalField("total_bytes", "float64", "DERIVED", "Total bytes in flow", 0.0),
    
    # Flow Rates & Packet Sizing
    "packet_rate": CanonicalField("packet_rate", "float64", "DERIVED", "Packets per unit time", 0.0),
    "byte_rate": CanonicalField("byte_rate", "float64", "DERIVED", "Bytes per unit time", 0.0),
    "average_packet_size": CanonicalField("average_packet_size", "float64", "DERIVED", "Mean size of packets in flow", 0.0),
    "packet_size_variance": CanonicalField("packet_size_variance", "float64", "OPTIONAL", "Variance of packet sizes", 0.0),
    "inter_arrival_time": CanonicalField("inter_arrival_time", "float64", "OPTIONAL", "Mean packet inter-arrival time", 0.0),
    
    # Flags & Header Statistics
    "tcp_flags": CanonicalField("tcp_flags", "int64", "OPTIONAL", "Bitwise representation of TCP flags", 0),
    "syn_flag_count": CanonicalField("syn_flag_count", "int64", "OPTIONAL", "Count of SYN flags", 0),
    "ack_flag_count": CanonicalField("ack_flag_count", "int64", "OPTIONAL", "Count of ACK flags", 0),
    "fin_flag_count": CanonicalField("fin_flag_count", "int64", "OPTIONAL", "Count of FIN flags", 0),
    "rst_flag_count": CanonicalField("rst_flag_count", "int64", "OPTIONAL", "Count of RST flags", 0),
    
    # Ground Truth Label
    "label": CanonicalField("label", "string", "LABEL", "Normalized attack classification label", "BENIGN"),
    "original_label": CanonicalField("original_label", "string", "LABEL", "Raw dataset label before mapping", "BENIGN"),
}

# Feature Categorization for ML pipelines
IDENTIFIER_COLUMNS: Set[str] = {
    "source_ip",
    "destination_ip",
}

LABEL_COLUMNS: Set[str] = {
    "label",
    "original_label",
}

MODEL_BASE_NUMERIC_FEATURES: List[str] = [
    "flow_duration",
    "forward_packet_count",
    "backward_packet_count",
    "total_packet_count",
    "forward_bytes",
    "backward_bytes",
    "total_bytes",
    "packet_rate",
    "byte_rate",
    "average_packet_size",
    "packet_size_variance",
    "inter_arrival_time",
    "source_port",
    "destination_port",
    "syn_flag_count",
    "ack_flag_count",
    "fin_flag_count",
    "rst_flag_count",
]

def get_canonical_fields(category: Optional[str] = None) -> List[str]:
    """Retrieve list of canonical field names filtered by category."""
    if not category:
        return list(CANONICAL_SCHEMA.keys())
    return [k for k, v in CANONICAL_SCHEMA.items() if v.category == category]
