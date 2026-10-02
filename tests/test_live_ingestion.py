import pytest
from unittest.mock import patch, MagicMock
from scapy.packet import Packet
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether
import time
import queue
import pandas as pd

from backend.telemetry.live.flow_builder import FlowBuilder
from backend.telemetry.flow_sources import LiveFlowSource
from backend.telemetry.window_aggregator import WindowAggregator, CANONICAL_17_FEATURES

def create_tcp_packet(src="1.1.1.1", dst="2.2.2.2", sport=12345, dport=80, flags="S", pkt_time=None):
    pkt = Ether()/IP(src=src, dst=dst)/TCP(sport=sport, dport=dport, flags=flags)
    if pkt_time:
        pkt.time = pkt_time
    return pkt

def create_udp_packet(src="1.1.1.1", dst="2.2.2.2", sport=12345, dport=53, pkt_time=None):
    pkt = Ether()/IP(src=src, dst=dst)/UDP(sport=sport, dport=dport)
    if pkt_time:
        pkt.time = pkt_time
    return pkt

def create_icmp_packet(src="1.1.1.1", dst="2.2.2.2", pkt_time=None):
    pkt = Ether()/IP(src=src, dst=dst)/ICMP()
    if pkt_time:
        pkt.time = pkt_time
    return pkt

def test_flow_builder_tcp_syn():
    builder = FlowBuilder()
    pkt = create_tcp_packet(flags="S")
    emitted = builder.process_packet(pkt)
    assert len(emitted) == 0
    assert len(builder.active_flows) == 1
    key = list(builder.active_flows.keys())[0]
    flow = builder.active_flows[key]
    assert flow.protocol == "TCP"
    assert flow.tcp_flags & 0x02  # SYN

def test_flow_builder_tcp_ack():
    builder = FlowBuilder()
    pkt = create_tcp_packet(flags="A")
    emitted = builder.process_packet(pkt)
    assert len(emitted) == 0
    flow = list(builder.active_flows.values())[0]
    assert flow.tcp_flags & 0x10  # ACK

def test_flow_builder_fin_termination():
    builder = FlowBuilder()
    pkt_syn = create_tcp_packet(flags="S")
    pkt_fin = create_tcp_packet(flags="F")
    
    emitted = builder.process_packet(pkt_syn)
    assert len(emitted) == 0
    
    emitted = builder.process_packet(pkt_fin)
    assert len(emitted) == 1
    assert emitted[0].tcp_flags & 0x01  # FIN
    assert len(builder.active_flows) == 0

def test_flow_builder_rst_termination():
    builder = FlowBuilder()
    pkt_syn = create_tcp_packet(flags="S")
    pkt_rst = create_tcp_packet(flags="R")
    
    emitted = builder.process_packet(pkt_syn)
    assert len(emitted) == 0
    
    emitted = builder.process_packet(pkt_rst)
    assert len(emitted) == 1
    assert emitted[0].tcp_flags & 0x04  # RST
    assert len(builder.active_flows) == 0

def test_flow_builder_udp():
    builder = FlowBuilder()
    pkt = create_udp_packet()
    emitted = builder.process_packet(pkt)
    assert len(emitted) == 0
    flow = list(builder.active_flows.values())[0]
    assert flow.protocol == "UDP"

def test_flow_builder_icmp():
    builder = FlowBuilder()
    pkt = create_icmp_packet()
    emitted = builder.process_packet(pkt)
    assert len(emitted) == 0
    flow = list(builder.active_flows.values())[0]
    assert flow.protocol == "ICMP"
    assert flow.src_port == 0
    assert flow.dst_port == 0

def test_flow_builder_multiple_packets_same_flow():
    builder = FlowBuilder()
    for i in range(5):
        pkt = create_tcp_packet(flags="A")
        builder.process_packet(pkt)
        
    assert len(builder.active_flows) == 1
    flow = list(builder.active_flows.values())[0]
    assert flow.packets == 5

def test_flow_builder_two_different_flows():
    builder = FlowBuilder()
    pkt1 = create_tcp_packet(src="1.1.1.1", dst="2.2.2.2")
    pkt2 = create_tcp_packet(src="3.3.3.3", dst="4.4.4.4")
    
    builder.process_packet(pkt1)
    builder.process_packet(pkt2)
    
    assert len(builder.active_flows) == 2

def test_flow_builder_duration_and_timestamps():
    builder = FlowBuilder()
    now = time.time()
    pkt1 = create_tcp_packet(flags="S", pkt_time=now)
    pkt2 = create_tcp_packet(flags="A", pkt_time=now + 5.0)
    pkt3 = create_tcp_packet(flags="F", pkt_time=now + 10.0)
    
    builder.process_packet(pkt1)
    builder.process_packet(pkt2)
    emitted = builder.process_packet(pkt3)
    
    assert len(emitted) == 1
    flow_rec = emitted[0]
    assert flow_rec.duration_seconds == 10.0
    assert flow_rec.packets == 3

def test_flow_builder_idle_timeout():
    builder = FlowBuilder(idle_timeout_seconds=60.0)
    now = time.time()
    pkt = create_tcp_packet(pkt_time=now)
    builder.process_packet(pkt)
    
    assert len(builder.active_flows) == 1
    
    # Expiry before timeout
    emitted = builder.expire_stale_flows(current_time=now + 30.0)
    assert len(emitted) == 0
    assert len(builder.active_flows) == 1
    
    # Expiry after timeout
    emitted = builder.expire_stale_flows(current_time=now + 65.0)
    assert len(emitted) == 1
    assert len(builder.active_flows) == 0

def test_flow_builder_explicit_flush():
    builder = FlowBuilder()
    builder.process_packet(create_tcp_packet())
    builder.process_packet(create_udp_packet())
    
    assert len(builder.active_flows) == 2
    emitted = builder.flush()
    assert len(emitted) == 2
    assert len(builder.active_flows) == 0

def test_flow_builder_malformed_and_unsupported():
    builder = FlowBuilder()
    
    # Just Ether, no IP
    pkt_ether = Ether()
    emitted = builder.process_packet(pkt_ether)
    assert len(emitted) == 0
    assert len(builder.active_flows) == 0
    
    # Monkeypatch __getitem__
    class FakePkt:
        def __init__(self):
            self.IP = MagicMock()
            self.IP.src = "1.1.1.1"
            self.IP.dst = "2.2.2.2"
        def haslayer(self, layer):
            return layer == "IP"
        def __len__(self):
            return 64
        def __getitem__(self, layer):
            if layer == "IP": return self.IP
            raise KeyError
        @property
        def time(self):
            return time.time()
            
    pkt_unsupported = FakePkt()
    
    builder.process_packet(pkt_unsupported)
    assert len(builder.active_flows) == 1
    flow = list(builder.active_flows.values())[0]
    assert flow.protocol == "OTHER"

def test_live_flow_source_repeated_start_stop():
    source = LiveFlowSource("lo0")
    
    with patch("threading.Thread.start") as mock_start:
        source.start()
        assert source.state == "STARTING"
        
        # Calling start again does nothing if running
        source._is_running = True
        source.start()
        mock_start.assert_called_once()
        
        # Stop
        source.stop()
        assert source.state == "STOPPED"
        assert source._is_running is False

def test_live_flow_source_permission_failure():
    source = LiveFlowSource("lo0")
    
    def mock_sniff(*args, **kwargs):
        raise PermissionError("Permission denied: '/dev/bpf0'")
        
    with patch("scapy.all.sniff", mock_sniff):
        source._capture_loop()
        assert source.state == "PERMISSION_DENIED"
        assert "LIVE NETWORK UNAVAILABLE: PACKET CAPTURE PERMISSION REQUIRED" in source.error_message
        assert source._is_running is False

def test_live_ingestion_17_feature_contract_integration():
    """
    Scapy -> FlowBuilder -> FlowRecord -> WindowAggregator -> 17 features
    """
    builder = FlowBuilder()
    agg = WindowAggregator(window_size_seconds=60)
    
    base_time = pd.Timestamp("2026-10-02T12:00:00Z").timestamp()
    
    # 1. Flow 1: TCP SYN-ACK-FIN (2 seconds)
    builder.process_packet(create_tcp_packet(src="1.1.1.1", dst="2.2.2.2", sport=1000, dport=80, flags="S", pkt_time=base_time))
    builder.process_packet(create_tcp_packet(src="1.1.1.1", dst="2.2.2.2", sport=1000, dport=80, flags="A", pkt_time=base_time+1))
    f1_records = builder.process_packet(create_tcp_packet(src="1.1.1.1", dst="2.2.2.2", sport=1000, dport=80, flags="F", pkt_time=base_time+2))
    assert len(f1_records) == 1
    
    # 2. Flow 2: UDP short burst to high port
    builder.process_packet(create_udp_packet(src="3.3.3.3", dst="4.4.4.4", sport=1000, dport=5000, pkt_time=base_time+5))
    builder.process_packet(create_udp_packet(src="3.3.3.3", dst="4.4.4.4", sport=1000, dport=5000, pkt_time=base_time+6))
    
    # 3. Flush the UDP flow
    flushed = builder.flush()
    records = f1_records + flushed
    assert len(records) == 2
    
    # Push to aggregator
    for r in records:
        agg.add_flow(r)
        
    # Flush aggregator to get window features
    window_completed, emitted_ts, features = agg.flush()
    assert window_completed is True
    assert features is not None
    
    # Verify exact 17 canonical features exist and are not NaN
    for feat in CANONICAL_17_FEATURES:
        assert feat in features
        assert features[feat] is not None
        assert not pd.isna(features[feat])
        assert type(features[feat]) == float
        
    assert features["flow_count"] == 2.0
    assert features["unique_sources"] == 2.0
    assert features["unique_destinations"] == 2.0
    assert features["syn_flag_count"] == 1.0 # Only flow 1 had SYN
    assert features["privileged_port_ratio"] == 0.5 # Flow 1 to port 80 (privileged)
