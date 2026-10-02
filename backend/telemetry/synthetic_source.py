"""
SENTRANET — Synthetic Telemetry Flow Generator (Phase 9)
Generates deterministic network flow metadata streams for integration testing and SOC demos.

SCIENTIFIC BOUNDARY:
- Generates synthetic FLOW METADATA ONLY (IPs, ports, protocols, timestamps, volume).
- NEVER inspects, creates, or stores packet payloads.
- Strictly labeled as 'synthetic' simulation traffic.
"""

from typing import Iterator, Optional, Dict, Any, List
import random
from datetime import datetime, timedelta, timezone
import logging

from backend.telemetry.flow_schema import FlowRecord
from backend.telemetry.flow_sources import SourceType

logger = logging.getLogger("sentranet.telemetry.synthetic")

VALID_PROFILES = {"BASELINE", "SCANNING", "DDOS", "BOTNET", "scenario_1", "forecastable_escalation"}


class SyntheticFlowSource:
    """
    Deterministic Synthetic Network Flow Generator.
    Produces metadata sequences conforming to predefined behavioral profiles or temporal scenarios.
    """

    def __init__(
        self,
        seed: int = 42,
        profile: str = "scenario_1",
        start_time: Optional[str] = None,
    ):
        self.seed = int(seed)
        self.profile = profile if profile in VALID_PROFILES else "scenario_1"
        self._source_type: SourceType = "synthetic"

        self.rng = random.Random(self.seed)

        if start_time:
            # Parse start time cleanly
            clean_ts = start_time.replace("Z", "+00:00")
            try:
                self.current_dt = datetime.fromisoformat(clean_ts)
            except Exception:
                self.current_dt = datetime(2026, 9, 30, 10, 0, 0, tzinfo=timezone.utc)
        else:
            self.current_dt = datetime(2026, 9, 30, 10, 0, 0, tzinfo=timezone.utc)

        self.elapsed_seconds: float = 0.0
        self._flow_counter: int = 0

    @property
    def source_type(self) -> SourceType:
        return self._source_type

    def _get_active_profile_for_elapsed(self, elapsed: float) -> str:
        """Evaluates profile based on elapsed scenario time."""
        if self.profile != "scenario_1" and self.profile != "forecastable_escalation":
            return self.profile

        if self.profile == "forecastable_escalation":
            # Deterministic timeline for evaluation
            # 0-300s (0-5m): BASELINE
            # 300-600s (5-10m): EARLY_PRECURSOR (slight elevated)
            # 600-900s (10-15m): MILD_ESCALATION
            # 900-1200s (15-20m): STRONGER_ESCALATION
            # 1200-1500s (20-25m): SCANNING (Attack Onset)
            # 1500-1800s (25-30m): DDOS
            # 1800+s: BASELINE
            if elapsed < 300.0:
                return "BASELINE"
            elif elapsed < 600.0:
                return "EARLY_PRECURSOR"
            elif elapsed < 900.0:
                return "MILD_ESCALATION"
            elif elapsed < 1200.0:
                return "STRONGER_ESCALATION"
            elif elapsed < 1500.0:
                return "SCANNING"
            elif elapsed < 1800.0:
                return "DDOS"
            else:
                return "BASELINE"

        # Scenario 1 Progression:
        # 0 - 180s (0-3m): BASELINE
        # 180 - 300s (3-5m): SCANNING
        # 300 - 420s (5-7m): DDOS
        # 420s+ (7m+): BASELINE
        if elapsed < 180.0:
            return "BASELINE"
        elif elapsed < 300.0:
            return "SCANNING"
        elif elapsed < 420.0:
            return "DDOS"
        else:
            return "BASELINE"

    def read(self) -> Optional[FlowRecord]:
        """
        Generates and advances the next synthetic FlowRecord.
        Advances simulation clock by a small stochastic delta based on profile intensity.
        """
        active_profile = self._get_active_profile_for_elapsed(self.elapsed_seconds)
        self._flow_counter += 1

        # Profile-specific generation parameters
        if active_profile == "SCANNING":
            # Scanning: Many distinct destination ports/IPs, short duration, SYN heavy, small bytes
            time_delta = self.rng.uniform(0.01, 0.08)
            src_ip = f"192.168.1.{self.rng.choice([105, 106, 107])}"
            dst_ip = f"10.0.0.{self.rng.randint(1, 254)}"
            src_port = self.rng.randint(40000, 65000)
            dst_port = self.rng.choice([21, 22, 23, 25, 80, 443, 445, 1433, 3306, 3389, 8080, 8443])
            protocol = "TCP"
            duration = round(self.rng.uniform(0.001, 0.05), 4)
            packets = self.rng.randint(1, 3)
            bytes_val = float(packets * self.rng.randint(40, 64))
            tcp_flags = "SYN"

        elif active_profile == "DDOS":
            # DDoS: High flow rate, heavy traffic, targeted destination, high packets/bytes
            time_delta = self.rng.uniform(0.005, 0.03)
            src_ip = f"172.16.{self.rng.randint(1, 10)}.{self.rng.randint(1, 254)}"
            dst_ip = "10.0.0.50"  # Target server
            src_port = self.rng.randint(1024, 65535)
            dst_port = self.rng.choice([80, 443, 53])
            protocol = self.rng.choice(["TCP", "UDP"])
            duration = round(self.rng.uniform(0.1, 1.5), 4)
            packets = self.rng.randint(25, 120)
            bytes_val = float(packets * self.rng.randint(800, 1460))
            tcp_flags = "SYN,ACK" if protocol == "TCP" else None

        elif active_profile == "BOTNET":
            # Botnet: Periodic beaconing to C2, moderate packets, steady intervals
            time_delta = self.rng.uniform(0.2, 0.8)
            src_ip = f"192.168.1.{self.rng.randint(20, 30)}"
            dst_ip = "198.51.100.42"  # C2 IP
            src_port = self.rng.randint(45000, 60000)
            dst_port = self.rng.choice([443, 8443, 80])
            protocol = "TCP"
            duration = round(self.rng.uniform(0.5, 2.0), 4)
            packets = self.rng.randint(10, 30)
            bytes_val = float(packets * self.rng.randint(150, 450))
            tcp_flags = "ACK"

        elif active_profile == "EARLY_PRECURSOR":
            # Slightly elevated flow/packet/byte activity
            time_delta = self.rng.uniform(0.04, 0.3)
            src_ip = f"192.168.1.{self.rng.randint(10, 80)}"
            dst_ip = f"172.217.16.{self.rng.randint(1, 40)}"
            src_port = self.rng.randint(30000, 65000)
            dst_port = self.rng.choice([80, 443, 53, 8080, 22])
            protocol = self.rng.choice(["TCP", "TCP", "UDP"])
            duration = round(self.rng.uniform(0.05, 2.5), 4)
            packets = self.rng.randint(10, 40)
            bytes_val = float(packets * self.rng.randint(250, 950))
            tcp_flags = "ACK" if protocol == "TCP" else None

        elif active_profile == "MILD_ESCALATION":
            # Increasing source diversity and SYN activity
            time_delta = self.rng.uniform(0.03, 0.2)
            src_ip = f"192.168.1.{self.rng.randint(80, 150)}"
            dst_ip = f"10.0.0.{self.rng.randint(1, 100)}"
            src_port = self.rng.randint(30000, 65000)
            dst_port = self.rng.choice([80, 443, 8080, 22, 21, 23])
            protocol = "TCP"
            duration = round(self.rng.uniform(0.02, 1.5), 4)
            packets = self.rng.randint(5, 25)
            bytes_val = float(packets * self.rng.randint(100, 500))
            tcp_flags = self.rng.choice(["SYN", "ACK", "SYN,ACK"])

        elif active_profile == "STRONGER_ESCALATION":
            # High SYN rate, focused on a few targets, short durations
            time_delta = self.rng.uniform(0.015, 0.1)
            src_ip = f"192.168.1.{self.rng.randint(100, 200)}"
            dst_ip = "10.0.0.50"
            src_port = self.rng.randint(1024, 65000)
            dst_port = self.rng.choice([80, 443])
            protocol = "TCP"
            duration = round(self.rng.uniform(0.005, 0.5), 4)
            packets = self.rng.randint(2, 10)
            bytes_val = float(packets * self.rng.randint(50, 200))
            tcp_flags = "SYN"

        else:
            # BASELINE: Normal diverse enterprise/web traffic
            time_delta = self.rng.uniform(0.05, 0.4)
            src_ip = f"192.168.1.{self.rng.randint(10, 80)}"
            dst_ip = f"172.217.16.{self.rng.randint(1, 30)}"
            src_port = self.rng.randint(30000, 65000)
            dst_port = self.rng.choice([80, 443, 53, 8080, 22])
            protocol = self.rng.choice(["TCP", "TCP", "TCP", "UDP"])
            duration = round(self.rng.uniform(0.05, 3.0), 4)
            packets = self.rng.randint(4, 25)
            bytes_val = float(packets * self.rng.randint(200, 900))
            tcp_flags = "ACK" if protocol == "TCP" else None

        # Advance internal time
        self.elapsed_seconds += time_delta
        self.current_dt += timedelta(seconds=time_delta)

        ts_str = self.current_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        flow_id = f"syn-{self.seed}-{self._flow_counter:08d}"

        return FlowRecord(
            timestamp=ts_str,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            duration_seconds=duration,
            packets=packets,
            bytes=bytes_val,
            tcp_flags=tcp_flags,
            flow_id=flow_id,
            interface="eth0",
            direction="ingress",
        )

    def __iter__(self) -> Iterator[FlowRecord]:
        while True:
            yield self.read()

    def reset(self) -> None:
        """Resets the generator to initial seed and timestamp."""
        self.rng = random.Random(self.seed)
        self.current_dt = datetime(2026, 9, 30, 10, 0, 0, tzinfo=timezone.utc)
        self.elapsed_seconds = 0.0
        self._flow_counter = 0
