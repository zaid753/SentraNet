import threading
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio

from backend.telemetry.flow_sources import LiveFlowSource
from backend.telemetry.stream_processor import StreamProcessor
from backend.api.events import event_bus, EventEnvelope, EventTypes

logger = logging.getLogger("sentranet.live_service")

class LiveService:
    _instance: Optional["LiveService"] = None
    _init_lock = threading.Lock()
    
    def __init__(self, stream_processor: Optional[StreamProcessor] = None):
        self.stream_processor = stream_processor or StreamProcessor.get_instance()
        self.live_source: Optional[LiveFlowSource] = None
        
        self.start_time: Optional[float] = None
        self.packet_count: int = 0
        self.flow_count: int = 0
        self.last_packet_time: Optional[float] = None
        
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False

    @classmethod
    def get_instance(cls, stream_processor: Optional[StreamProcessor] = None) -> "LiveService":
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = cls(stream_processor)
        return cls._instance

    def get_status(self) -> Dict[str, Any]:
        state = "STOPPED"
        error_msg = None
        interface = None
        
        if self.live_source:
            state = self.live_source.state
            error_msg = self.live_source.error_message
            interface = self.live_source.interface
            
        start_time_iso = None
        if self.start_time:
            start_time_iso = datetime.fromtimestamp(self.start_time, timezone.utc).isoformat()
            
        last_packet_iso = None
        if self.last_packet_time:
            last_packet_iso = datetime.fromtimestamp(self.last_packet_time, timezone.utc).isoformat()
            
        return {
            "state": state,
            "interface": interface,
            "error_message": error_msg,
            "packet_count": self.packet_count,
            "flow_count": self.flow_count,
            "start_time": start_time_iso,
            "last_packet_time": last_packet_iso
        }

    def start(self, interface: str) -> Dict[str, Any]:
        if self._is_running or (self.live_source and self.live_source.state in ["RUNNING", "STARTING"]):
            return self.get_status()
            
        self.stream_processor.reset()
            
        self.live_source = LiveFlowSource(interface=interface)
        self.live_source.start()
        
        self.start_time = time.time()
        self.packet_count = 0
        self.flow_count = 0
        self.last_packet_time = None
        self._stop_event.clear()
        
        self._is_running = True
        self._thread = threading.Thread(target=self._pump_loop, daemon=True)
        self._thread.start()
        
        self._broadcast_status()
        
        return self.get_status()

    def stop(self) -> Dict[str, Any]:
        self._stop_event.set()
        
        if self.live_source:
            self.live_source.stop()
            
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            
        self._is_running = False
        
        # Flush stream processor
        self.stream_processor.flush()
        
        self._broadcast_status()
        
        return self.get_status()

    def _pump_loop(self) -> None:
        last_broadcast_state = None
        while not self._stop_event.is_set():
            if not self.live_source:
                break
                
            current_state = self.live_source.state
            if current_state != last_broadcast_state:
                self._broadcast_status()
                last_broadcast_state = current_state
                
            # If live source is stopped/error, we should stop pumping after emptying queue
            if current_state in ["ERROR", "PERMISSION_DENIED", "STOPPED"]:
                # empty queue then exit
                while True:
                    rec = self.live_source.read()
                    if rec is None:
                        break
                    self._process_record(rec)
                
                self._is_running = False
                self._broadcast_status()
                break
                
            rec = self.live_source.read()
            if rec:
                self._process_record(rec)
            else:
                time.sleep(0.1)
                
    def _process_record(self, rec) -> None:
        self.flow_count += 1
        self.packet_count += rec.packets
        self.last_packet_time = time.time()
        
        # Ingest to stream processor
        self.stream_processor.ingest_flow(rec, source_type="live")
        
    def _broadcast_status(self) -> None:
        status = self.get_status()
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(
                event_bus.publish,
                EventEnvelope(
                    event_type=EventTypes.SYSTEM_STATUS_CHANGED,
                    payload={"component": "live_capture", "status": status}
                )
            )
        except RuntimeError:
            event_bus.publish(
                EventEnvelope(
                    event_type=EventTypes.SYSTEM_STATUS_CHANGED,
                    payload={"component": "live_capture", "status": status}
                )
            )

    @staticmethod
    def get_interfaces() -> List[Dict[str, str]]:
        try:
            from scapy.all import get_if_list
            ifaces = []
            for iface in get_if_list():
                ifaces.append({"name": iface, "description": f"Interface {iface}"})
            if not ifaces:
                 ifaces.append({"name": "lo0", "description": "Loopback"})
            return ifaces
        except Exception:
            return [{"name": "lo0", "description": "Loopback (Fallback)"}]
