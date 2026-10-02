"""
SENTRANET — Telemetry Flow Sources (Phase 9)
Defines abstract FlowSource interface and implementations:
- SyntheticFlowSource
- ReplayFlowSource
- FileFlowSource
- LiveFlowSource (Placeholder for future live packet/IPFIX capture)
"""

from typing import Protocol, Iterator, Optional, Dict, Any, List, Union
from typing_extensions import Literal
import os
import json
import pandas as pd
from datetime import datetime
import threading
import queue
import time

from backend.telemetry.live.flow_builder import FlowBuilder

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.flow_normalizer import normalize_flow

SourceType = Literal["historical", "synthetic", "live"]


class FlowSource(Protocol):
    """
    Common abstraction protocol for network flow streams.
    The AI ingestion pipeline consumes FlowRecords identically regardless of source.
    """
    @property
    def source_type(self) -> SourceType:
        """Indicates whether traffic is historical, synthetic, or live."""
        ...

    def read(self) -> Optional[FlowRecord]:
        """Reads the next single FlowRecord or returns None when source is exhausted."""
        ...

    def __iter__(self) -> Iterator[FlowRecord]:
        """Iterates over flow records sequentially."""
        ...


class FileFlowSource:
    """
    Reads flow records sequentially from CSV or JSONL files.
    Maps common column variations to canonical FlowRecord fields.
    """

    def __init__(self, file_path: str, source_type: SourceType = "historical"):
        self.file_path = file_path
        self._source_type: SourceType = source_type
        self._records: List[FlowRecord] = []
        self._cursor: int = 0
        self._load_file()

    @property
    def source_type(self) -> SourceType:
        return self._source_type

    def _load_file(self) -> None:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Telemetry flow file not found: {self.file_path}")

        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == ".jsonl":
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        self._records.append(self._dict_to_flow(data))
        else:
            # Default to CSV
            df = pd.read_csv(self.file_path)
            for _, row in df.iterrows():
                self._records.append(self._row_to_flow(row.to_dict()))

    def _row_to_flow(self, row: Dict[str, Any]) -> FlowRecord:
        """Converts raw CSV dictionary with flexible column name resolution."""
        # IP mappings
        src_ip = str(row.get("source_ip") or row.get("src_ip") or "127.0.0.1")
        dst_ip = str(row.get("destination_ip") or row.get("dst_ip") or "127.0.0.1")

        # Port mappings
        src_port = int(row.get("source_port") or row.get("src_port") or 0)
        dst_port = int(row.get("destination_port") or row.get("dst_port") or 0)

        # Protocol mapping
        proto_raw = row.get("protocol")
        if proto_raw in [6, "6", "TCP", "tcp"]:
            proto = "TCP"
        elif proto_raw in [17, "17", "UDP", "udp"]:
            proto = "UDP"
        elif proto_raw in [1, "1", "ICMP", "icmp"]:
            proto = "ICMP"
        else:
            proto = str(proto_raw or "TCP")

        # Timestamp
        ts = str(row.get("timestamp") or datetime.now().isoformat())

        # Duration (handle microsecond durations by converting if > 1000)
        raw_dur = float(row.get("flow_duration") or row.get("duration_seconds") or 0.0)
        duration_sec = raw_dur / 1e6 if raw_dur > 1000.0 else raw_dur

        # Packets
        fwd_p = int(row.get("total_fwd_packets") or row.get("forward_packet_count") or 0)
        bwd_p = int(row.get("total_backward_packets") or row.get("backward_packet_count") or 0)
        packets = int(row.get("packets") or (fwd_p + bwd_p) or 1)

        # Bytes
        fwd_b = float(row.get("total_length_of_fwd_packets") or row.get("forward_bytes") or 0.0)
        bwd_b = float(row.get("total_length_of_bwd_packets") or row.get("backward_bytes") or 0.0)
        bytes_val = float(row.get("bytes") or (fwd_b + bwd_b) or 64.0)

        # Flags
        syn_cnt = int(row.get("syn_flag_count") or 0)
        ack_cnt = int(row.get("ack_flag_count") or 0)
        flag_tokens = []
        if syn_cnt > 0:
            flag_tokens.append("SYN")
        if ack_cnt > 0:
            flag_tokens.append("ACK")
        tcp_flags = ",".join(flag_tokens) if flag_tokens else str(row.get("tcp_flags") or "")

        return FlowRecord(
            timestamp=ts,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=proto,
            duration_seconds=duration_sec,
            packets=packets,
            bytes=bytes_val,
            tcp_flags=tcp_flags or None,
        )

    def _dict_to_flow(self, data: Dict[str, Any]) -> FlowRecord:
        return FlowRecord(**data)

    def read(self) -> Optional[FlowRecord]:
        if self._cursor < len(self._records):
            rec = self._records[self._cursor]
            self._cursor += 1
            return rec
        return None

    def __iter__(self) -> Iterator[FlowRecord]:
        while True:
            rec = self.read()
            if rec is None:
                break
            yield rec

    def reset(self) -> None:
        self._cursor = 0


class ReplayFlowSource(FileFlowSource):
    """
    Historical Replay flow source.
    Reads from sample or historical dataset files and emits records with source_type='historical'.
    """

    def __init__(self, file_path: Optional[str] = None):
        default_path = "data/samples/sample_network_traffic.csv"
        target_path = file_path or default_path
        super().__init__(file_path=target_path, source_type="historical")


class LiveFlowSource:
    """
    Live packet capture and flow extraction.
    Captures traffic via scapy in a background thread, groups it via FlowBuilder,
    and exposes a read() interface for WindowAggregator.
    """

    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self._source_type: SourceType = "live"
        self._flow_builder = FlowBuilder()
        self._flow_queue: queue.Queue[FlowRecord] = queue.Queue()
        
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False
        
        self.state = "STOPPED"
        self.error_message: Optional[str] = None

    @property
    def source_type(self) -> SourceType:
        return self._source_type
        
    def start(self) -> None:
        if self._is_running:
            return
            
        self.state = "STARTING"
        self.error_message = None
        self._stop_event.clear()
        
        try:
            from scapy.all import sniff
        except ImportError as e:
            self.state = "ERROR"
            self.error_message = f"SCAPY IMPORT FAILED: {str(e)}"
            return
            
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._is_running = False
        self.state = "STOPPED"

        final_flows = self._flow_builder.flush()
        for f in final_flows:
            self._flow_queue.put(f)

    def _capture_loop(self) -> None:
        try:
            from scapy.all import sniff
        except ImportError:
            self.state = "ERROR"
            self.error_message = "Scapy not installed."
            return

        self._is_running = True
        self.state = "RUNNING"
        
        last_expire = time.time()

        def packet_handler(pkt):
            if self._stop_event.is_set():
                return
            
            flows = self._flow_builder.process_packet(pkt)
            for f in flows:
                self._flow_queue.put(f)
                
            nonlocal last_expire
            now = time.time()
            if now - last_expire > 5.0:
                stale = self._flow_builder.expire_stale_flows(now)
                for f in stale:
                    self._flow_queue.put(f)
                last_expire = now

        while not self._stop_event.is_set() and self.state == "RUNNING":
            try:
                sniff(
                    iface=self.interface,
                    prn=packet_handler,
                    store=False,
                    stop_filter=lambda _: self._stop_event.is_set(),
                    timeout=2.0
                )
            except PermissionError as pe:
                self._is_running = False
                self.state = "PERMISSION_DENIED"
                self.error_message = "LIVE NETWORK UNAVAILABLE: PACKET CAPTURE PERMISSION REQUIRED"
                break
            except Exception as e:
                self._is_running = False
                self.state = "ERROR"
                self.error_message = str(e)
                break

    def read(self) -> Optional[FlowRecord]:
        try:
            return self._flow_queue.get_nowait()
        except queue.Empty:
            return None

    def __iter__(self) -> Iterator[FlowRecord]:
        while True:
            rec = self.read()
            if rec is None:
                if not self._is_running and self._flow_queue.empty():
                    break
                else:
                    break
            yield rec

