"""
SENTRANET — Canonical FlowRecord Schema (Phase 9)
Strict Pydantic model for network flow metadata ingestion.
"""

from typing import Optional, Union, Any
import math
import ipaddress
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class FlowRecord(BaseModel):
    """
    Canonical Network Flow Metadata Record.
    Contains flow headers and traffic volume statistics only.
    No packet payload contents or deep packet payloads are ever captured or stored.
    """
    timestamp: str = Field(
        ...,
        description="Flow timestamp (ISO-8601 string, e.g. '2026-09-30T08:42:10Z' or '2026-09-30 08:42:10')"
    )
    src_ip: str = Field(..., description="Source IPv4 or IPv6 address")
    dst_ip: str = Field(..., description="Destination IPv4 or IPv6 address")
    src_port: int = Field(..., ge=0, le=65535, description="Source transport port (0-65535)")
    dst_port: int = Field(..., ge=0, le=65535, description="Destination transport port (0-65535)")
    protocol: str = Field(default="TCP", description="Transport protocol (e.g. TCP, UDP, ICMP, OTHER)")
    duration_seconds: float = Field(..., ge=0.0, description="Flow duration in seconds (>= 0.0)")
    packets: int = Field(..., ge=0, description="Total packet count in flow (>= 0)")
    bytes: float = Field(..., ge=0.0, description="Total byte volume in flow (>= 0.0)")
    tcp_flags: Optional[Union[str, int]] = Field(
        default=None,
        description="TCP flag representations (e.g. 'SYN,ACK', 'SYN', or bitwise integer)"
    )

    # Optional metadata (no payload)
    flow_id: Optional[str] = Field(default=None, description="Optional unique flow tracking identifier")
    interface: Optional[str] = Field(default=None, description="Optional network interface name")
    direction: Optional[str] = Field(default=None, description="Optional traffic direction (ingress/egress)")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("src_ip", "dst_ip")
    @classmethod
    def validate_ip(cls, v: str, info) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty IP address string.")
        try:
            ipaddress.ip_address(v.strip())
        except ValueError:
            raise ValueError(f"Field '{info.field_name}' contains an invalid IP address: '{v}'.")
        return v.strip()

    @field_validator("duration_seconds", "bytes")
    @classmethod
    def validate_finite_non_nan(cls, v: float, info) -> float:
        if math.isnan(v):
            raise ValueError(f"Field '{info.field_name}' must not be NaN.")
        if math.isinf(v):
            raise ValueError(f"Field '{info.field_name}' must not be Infinite.")
        if v < 0:
            raise ValueError(f"Field '{info.field_name}' must be non-negative (got {v}).")
        return float(v)

    @field_validator("packets")
    @classmethod
    def validate_packets(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"Field 'packets' must be non-negative (got {v}).")
        return int(v)

    @field_validator("src_port", "dst_port")
    @classmethod
    def validate_ports(cls, v: int, info) -> int:
        if v < 0 or v > 65535:
            raise ValueError(f"Field '{info.field_name}' must be between 0 and 65535 (got {v}).")
        return int(v)

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Field 'timestamp' must be a non-empty string.")
        clean_v = v.strip()
        # Parse ISO or standard space-separated format
        try:
            datetime.fromisoformat(clean_v.replace("Z", "+00:00"))
        except Exception:
            try:
                # Also accept standard SQL-like 'YYYY-MM-DD HH:MM:SS'
                datetime.strptime(clean_v, "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise ValueError(f"Field 'timestamp' cannot be parsed as a valid datetime: '{v}'.")
        return clean_v
