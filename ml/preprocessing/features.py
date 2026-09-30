"""Feature engineering, derivation, and model feature registry for SENTRANET."""

from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("sentranet.features")

class FeatureRegistry:
    """Registry documenting all canonical model features, their origin, and derivation."""

    REGISTERED_FEATURES: Dict[str, Dict[str, str]] = {
        "flow_duration": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Duration of network flow in seconds or microseconds",
        },
        "forward_packet_count": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Number of packets transmitted in forward direction",
        },
        "backward_packet_count": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Number of packets transmitted in backward direction",
        },
        "total_packet_count": {
            "type": "numeric",
            "source": "derived",
            "description": "Total packet count (forward + backward)",
        },
        "forward_bytes": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Total bytes transmitted in forward direction",
        },
        "backward_bytes": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Total bytes transmitted in backward direction",
        },
        "total_bytes": {
            "type": "numeric",
            "source": "derived",
            "description": "Total volume of bytes transmitted (forward + backward)",
        },
        "packet_rate": {
            "type": "numeric",
            "source": "derived",
            "description": "Packet transmission rate per unit time (total_packets / duration)",
        },
        "byte_rate": {
            "type": "numeric",
            "source": "derived",
            "description": "Byte transfer rate per unit time (total_bytes / duration)",
        },
        "average_packet_size": {
            "type": "numeric",
            "source": "derived",
            "description": "Mean packet size in bytes (total_bytes / total_packets)",
        },
        "packet_size_variance": {
            "type": "numeric",
            "source": "raw/derived",
            "description": "Variance of packet sizes within the flow",
        },
        "inter_arrival_time": {
            "type": "numeric",
            "source": "raw/derived",
            "description": "Mean packet inter-arrival time in microseconds",
        },
        "packet_ratio": {
            "type": "numeric",
            "source": "derived",
            "description": "Ratio of forward packets to backward packets (directionality)",
        },
        "byte_ratio": {
            "type": "numeric",
            "source": "derived",
            "description": "Ratio of forward bytes to backward bytes (directionality)",
        },
        "is_privileged_port": {
            "type": "binary",
            "source": "derived",
            "description": "1 if destination port is a privileged system port (< 1024), 0 otherwise",
        },
        "syn_flag_count": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Number of TCP SYN flags observed",
        },
        "ack_flag_count": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Number of TCP ACK flags observed",
        },
        "fin_flag_count": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Number of TCP FIN flags observed",
        },
        "rst_flag_count": {
            "type": "numeric",
            "source": "raw/normalized",
            "description": "Number of TCP RST flags observed",
        },
    }

    @classmethod
    def get_feature_list(cls) -> List[str]:
        return list(cls.REGISTERED_FEATURES.keys())

class FeatureEngineer:
    """Computes robust, safe derived features from normalized network flows."""

    EPSILON = 1e-6  # Zero-division protection constant

    @classmethod
    def safe_divide(cls, numerator: pd.Series, denominator: pd.Series, fill_val: float = 0.0) -> pd.Series:
        """Performs division with zero/infinite protection."""
        denom = denominator.replace(0, np.nan)
        res = numerator / denom
        return res.fillna(fill_val).replace([np.inf, -np.inf], fill_val)

    def engineer_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Derives domain features from network flow records:
        - Packet & byte totals
        - Packet rates & byte rates
        - Packet size statistics
        - Forward/backward directionality ratios
        - Port categories
        """
        data = df.copy()

        # 1. Total Packets
        if "total_packet_count" not in data.columns:
            fwd = data.get("forward_packet_count", pd.Series(0, index=data.index))
            bwd = data.get("backward_packet_count", pd.Series(0, index=data.index))
            data["total_packet_count"] = fwd + bwd

        # 2. Total Bytes
        if "total_bytes" not in data.columns:
            fwd_b = data.get("forward_bytes", pd.Series(0.0, index=data.index))
            bwd_b = data.get("backward_bytes", pd.Series(0.0, index=data.index))
            data["total_bytes"] = fwd_b + bwd_b

        # 3. Flow Duration (ensure numeric and non-negative)
        duration = data.get("flow_duration", pd.Series(0.0, index=data.index)).clip(lower=0.0)
        data["flow_duration"] = duration

        # 4. Rates (using safe divide)
        data["packet_rate"] = self.safe_divide(data["total_packet_count"], duration)
        data["byte_rate"] = self.safe_divide(data["total_bytes"], duration)

        # 5. Average Packet Size
        data["average_packet_size"] = self.safe_divide(data["total_bytes"], data["total_packet_count"])

        # 6. Directionality Ratios
        fwd_p = data.get("forward_packet_count", pd.Series(0, index=data.index))
        bwd_p = data.get("backward_packet_count", pd.Series(0, index=data.index))
        data["packet_ratio"] = self.safe_divide(fwd_p, bwd_p + self.EPSILON)

        fwd_bytes = data.get("forward_bytes", pd.Series(0.0, index=data.index))
        bwd_bytes = data.get("backward_bytes", pd.Series(0.0, index=data.index))
        data["byte_ratio"] = self.safe_divide(fwd_bytes, bwd_bytes + self.EPSILON)

        # 7. Port Classification (Privileged Ports < 1024 often targeted in scans/exploits)
        dst_port = data.get("destination_port", pd.Series(0, index=data.index))
        data["is_privileged_port"] = (dst_port < 1024).astype(int)

        # 8. Ensure optional fields exist with zero defaults if not in raw dataset
        optional_defaults = {
            "packet_size_variance": 0.0,
            "inter_arrival_time": 0.0,
            "syn_flag_count": 0,
            "ack_flag_count": 0,
            "fin_flag_count": 0,
            "rst_flag_count": 0,
        }
        for col, default_val in optional_defaults.items():
            if col not in data.columns:
                data[col] = default_val

        # Collect model feature subset
        registered = FeatureRegistry.get_feature_list()
        available_features = [f for f in registered if f in data.columns]

        logger.info(f"Feature engineering complete: {len(available_features)} model features ready")
        return data, available_features
