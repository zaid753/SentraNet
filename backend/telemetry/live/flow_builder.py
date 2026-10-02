"""
SENTRANET — Live Telemetry Flow Builder (Phase 13)
Groups raw packets into standardized normalized flow records.
"""

from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass
import uuid

from backend.telemetry.flow_schema import FlowRecord

FlowKey = Tuple[str, str, int, int, str]  # (src_ip, dst_ip, src_port, dst_port, protocol)

@dataclass
class ActiveFlow:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    first_seen: float
    last_seen: float
    packets: int
    bytes: int
    tcp_flags: int
    flow_id: str


class FlowBuilder:
    """
    Groups raw packets into flows. Emits FlowRecord when flow terminates via FIN/RST or idle timeout.
    Maintains bounded memory behavior.
    """

    def __init__(self, idle_timeout_seconds: float = 120.0):
        self.idle_timeout_seconds = idle_timeout_seconds
        self.active_flows: Dict[FlowKey, ActiveFlow] = {}

    def process_packet(self, pkt: Any) -> List[FlowRecord]:
        """
        Process a single scapy packet and return any terminated flows.
        """
        if not pkt.haslayer("IP"):
            return []

        ip_layer = pkt["IP"]
        src_ip = str(ip_layer.src)
        dst_ip = str(ip_layer.dst)
        pkt_len = len(pkt)
        
        ts = float(pkt.time) if hasattr(pkt, "time") and pkt.time else datetime.now(timezone.utc).timestamp()

        src_port = 0
        dst_port = 0
        protocol = "OTHER"
        tcp_flags = 0

        is_fin = False
        is_rst = False

        if pkt.haslayer("TCP"):
            tcp_layer = pkt["TCP"]
            protocol = "TCP"
            src_port = int(tcp_layer.sport)
            dst_port = int(tcp_layer.dport)
            
            flags_val = int(tcp_layer.flags)
            tcp_flags = flags_val
            
            # FIN=0x01, RST=0x04
            is_fin = (flags_val & 0x01) != 0
            is_rst = (flags_val & 0x04) != 0

        elif pkt.haslayer("UDP"):
            udp_layer = pkt["UDP"]
            protocol = "UDP"
            src_port = int(udp_layer.sport)
            dst_port = int(udp_layer.dport)

        elif pkt.haslayer("ICMP"):
            protocol = "ICMP"

        key: FlowKey = (src_ip, dst_ip, src_port, dst_port, protocol)
        
        if key not in self.active_flows:
            self.active_flows[key] = ActiveFlow(
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol,
                first_seen=ts,
                last_seen=ts,
                packets=1,
                bytes=pkt_len,
                tcp_flags=tcp_flags,
                flow_id=str(uuid.uuid4())
            )
        else:
            flow = self.active_flows[key]
            flow.packets += 1
            flow.bytes += pkt_len
            flow.last_seen = max(flow.last_seen, ts)
            flow.tcp_flags |= tcp_flags

        emitted = []
        if is_fin or is_rst:
            emitted.append(self._emit_flow(key))

        return emitted

    def expire_stale_flows(self, current_time: Optional[float] = None) -> List[FlowRecord]:
        """
        Check for flows that have been idle for longer than idle_timeout_seconds.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc).timestamp()
            
        stale_keys = []
        for key, flow in self.active_flows.items():
            if (current_time - flow.last_seen) > self.idle_timeout_seconds:
                stale_keys.append(key)
                
        return [self._emit_flow(key) for key in stale_keys]

    def flush(self) -> List[FlowRecord]:
        """
        Emit all active flows immediately.
        """
        keys = list(self.active_flows.keys())
        return [self._emit_flow(k) for k in keys]
        
    def _emit_flow(self, key: FlowKey) -> FlowRecord:
        flow = self.active_flows.pop(key)
        duration = max(0.0, flow.last_seen - flow.first_seen)
        
        ts_iso = datetime.fromtimestamp(flow.last_seen, timezone.utc).isoformat()
        
        return FlowRecord(
            timestamp=ts_iso,
            src_ip=flow.src_ip,
            dst_ip=flow.dst_ip,
            src_port=flow.src_port,
            dst_port=flow.dst_port,
            protocol=flow.protocol,
            duration_seconds=duration,
            packets=flow.packets,
            bytes=flow.bytes,
            tcp_flags=flow.tcp_flags,
            flow_id=flow.flow_id,
            interface="live",
            direction="inbound"
        )
