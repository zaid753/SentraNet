"""
SENTRANET — Flow Normalizer (Phase 9)
Converts raw flow metadata into canonical representation.
"""

from typing import Tuple, Union, Optional
from datetime import datetime, timezone
import re
from backend.telemetry.flow_schema import FlowRecord

SUPPORTED_PROTOCOLS = {"TCP", "UDP", "ICMP"}

def normalize_protocol(protocol: Optional[str]) -> str:
    """
    Normalizes transport protocol string:
    'tcp', 'TCP', 'Tcp' -> 'TCP'
    'udp' -> 'UDP'
    'icmp' -> 'ICMP'
    Unknown/other -> 'OTHER'
    """
    if not protocol or not isinstance(protocol, str):
        return "OTHER"
    clean = protocol.strip().upper()
    if clean in SUPPORTED_PROTOCOLS:
        return clean
    if "TCP" in clean:
        return "TCP"
    if "UDP" in clean:
        return "UDP"
    if "ICMP" in clean:
        return "ICMP"
    return "OTHER"

def normalize_flags(flags: Optional[Union[str, int]]) -> Tuple[int, int, str]:
    """
    Normalizes TCP flag metadata into:
    (syn_flag_count, ack_flag_count, normalized_flag_str)

    Accepts:
    - String representations: 'SYN', 'ACK', 'SYN,ACK', 'SYN/ACK', 'PSH+ACK'
    - Bitwise integers: 0x02 (SYN), 0x10 (ACK), 0x12 (SYN+ACK)
    """
    if flags is None:
        return 0, 0, ""

    syn_count = 0
    ack_count = 0
    detected_flags = []

    if isinstance(flags, int):
        # Standard TCP flag bitmask:
        # FIN=0x01, SYN=0x02, RST=0x04, PSH=0x08, ACK=0x10, URG=0x20
        if flags & 0x02:
            syn_count = 1
            detected_flags.append("SYN")
        if flags & 0x10:
            ack_count = 1
            detected_flags.append("ACK")
        if flags & 0x01:
            detected_flags.append("FIN")
        if flags & 0x04:
            detected_flags.append("RST")
        if flags & 0x08:
            detected_flags.append("PSH")
        if flags & 0x20:
            detected_flags.append("URG")
        return syn_count, ack_count, ",".join(detected_flags)

    # String representation
    flag_str = str(flags).upper().strip()
    tokens = [t.strip() for t in re.split(r"[,/|+ ]+", flag_str) if t.strip()]

    if "SYN" in tokens or "SYN" in flag_str:
        syn_count = 1
        detected_flags.append("SYN")
    if "ACK" in tokens or "ACK" in flag_str:
        ack_count = 1
        detected_flags.append("ACK")
    if "FIN" in tokens or "FIN" in flag_str:
        detected_flags.append("FIN")
    if "RST" in tokens or "RST" in flag_str:
        detected_flags.append("RST")

    normalized_str = ",".join(detected_flags) if detected_flags else flag_str
    return syn_count, ack_count, normalized_str

def normalize_timestamp_str(ts_str: str) -> str:
    """
    Standardizes timestamp string while strictly preserving the original time semantics.
    Does NOT shift timezones silently.
    Converts space-separated 'YYYY-MM-DD HH:MM:SS' to ISO-8601 'YYYY-MM-DDTHH:MM:SS'.
    """
    clean_ts = ts_str.strip()
    clean_ts = clean_ts.replace(" ", "T")
    # If trailing Z, preserve
    return clean_ts

def normalize_flow(flow: FlowRecord) -> FlowRecord:
    """
    Returns a normalized FlowRecord:
    - Protocol normalized (TCP/UDP/ICMP/OTHER)
    - IP addresses stripped
    - Timestamp normalized
    - TCP flags normalized
    """
    _, _, normalized_flags = normalize_flags(flow.tcp_flags)
    return FlowRecord(
        timestamp=normalize_timestamp_str(flow.timestamp),
        src_ip=flow.src_ip.strip(),
        dst_ip=flow.dst_ip.strip(),
        src_port=flow.src_port,
        dst_port=flow.dst_port,
        protocol=normalize_protocol(flow.protocol),
        duration_seconds=round(float(flow.duration_seconds), 6),
        packets=int(flow.packets),
        bytes=round(float(flow.bytes), 2),
        tcp_flags=normalized_flags or flow.tcp_flags,
        flow_id=flow.flow_id,
        interface=flow.interface,
        direction=flow.direction,
    )
