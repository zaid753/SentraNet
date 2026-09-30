"""Temporal windowing, aggregations, and rolling features for forecasting pipelines."""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import logging
from ml.preprocessing.labels import normalize_label

logger = logging.getLogger("sentranet.windowing")

class TemporalWindowAggregator:
    """
    Transforms event-level network flow streams into discrete temporal windows
    with summary aggregations and causal rolling historical features.
    
    Guarantees strict causal ordering: At window T, calculations only reference
    windows <= T to prevent future leakage.
    """

    def __init__(
        self,
        window_size_seconds: int = 60,
        rolling_window_count: int = 5,
        attack_threshold: float = 0.35,
    ):
        self.window_size_seconds = window_size_seconds
        self.rolling_window_count = rolling_window_count
        self.attack_threshold = attack_threshold

    def aggregate_windows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Groups flows into temporal bins [t, t + window_size) and computes:
        - Flow count
        - Total packets & bytes
        - Mean packet & byte rates
        - Cardinality of unique source and destination IPs
        - Directionality and sizing metrics
        - Dominant attack class label for the window
        """
        if "timestamp" not in df.columns or df["timestamp"].isna().all():
            logger.warning("No valid timestamps found for temporal windowing; returning empty window DF")
            return pd.DataFrame()

        # Ensure sorted chronologically
        data = df.sort_values(by="timestamp").reset_index(drop=True)

        # Floor timestamps to window interval
        freq_str = f"{self.window_size_seconds}s"
        data["window_start"] = data["timestamp"].dt.floor(freq_str)

        grouped = data.groupby("window_start")
        window_records = []

        for window_start, group in grouped:
            window_end = window_start + pd.Timedelta(seconds=self.window_size_seconds)
            flow_count = len(group)
            
            # Flow volume totals
            total_packets = group["total_packet_count"].sum() if "total_packet_count" in group else 0
            total_bytes = group["total_bytes"].sum() if "total_bytes" in group else 0.0

            # Rates
            avg_packet_rate = group["packet_rate"].mean() if "packet_rate" in group else 0.0
            avg_byte_rate = group["byte_rate"].mean() if "byte_rate" in group else 0.0

            # Cardinality / Host behavioral dispersion
            unique_sources = group["source_ip"].nunique() if "source_ip" in group else 1
            unique_destinations = group["destination_ip"].nunique() if "destination_ip" in group else 1

            # Packet sizing & duration stats
            avg_packet_size = group["average_packet_size"].mean() if "average_packet_size" in group else 0.0
            avg_flow_duration = group["flow_duration"].mean() if "flow_duration" in group else 0.0

            # Flags
            syn_flags = group["syn_flag_count"].sum() if "syn_flag_count" in group else 0
            ack_flags = group["ack_flag_count"].sum() if "ack_flag_count" in group else 0

            # Privileged target ratio
            privileged_ratio = group["is_privileged_port"].mean() if "is_privileged_port" in group else 0.0

            # Window Ground Truth Label:
            # Evaluates the proportion of attack flows in the window.
            # If attack ratio exceeds attack_threshold, label as the dominant attack class;
            # otherwise, preserve the baseline BENIGN state.
            labels = group["label"].dropna() if "label" in group else pd.Series(["BENIGN"])
            normalized_series = labels.apply(normalize_label)
            attack_labels = normalized_series[normalized_series != "BENIGN"]
            total_flows = len(normalized_series)

            if total_flows > 0 and (len(attack_labels) / total_flows) >= self.attack_threshold:
                dominant_label = attack_labels.value_counts().index[0]
            else:
                dominant_label = "BENIGN"

            window_records.append({
                "window_start": window_start,
                "window_end": window_end,
                "flow_count": flow_count,
                "total_packets": total_packets,
                "total_bytes": total_bytes,
                "avg_packet_rate": float(avg_packet_rate),
                "avg_byte_rate": float(avg_byte_rate),
                "unique_sources": int(unique_sources),
                "unique_destinations": int(unique_destinations),
                "avg_packet_size": float(avg_packet_size),
                "avg_flow_duration": float(avg_flow_duration),
                "syn_flag_count": int(syn_flags),
                "ack_flag_count": int(ack_flags),
                "privileged_port_ratio": float(privileged_ratio),
                "label": str(dominant_label),
            })

        window_df = pd.DataFrame(window_records)
        if window_df.empty:
            return window_df

        # Chronological window ID
        window_df = window_df.sort_values(by="window_start").reset_index(drop=True)
        window_df["window_id"] = np.arange(len(window_df))

        # Add strictly causal rolling features (looking back over previous K windows)
        if self.rolling_window_count > 1 and len(window_df) >= self.rolling_window_count:
            window_df = self._add_causal_rolling_features(window_df)

        return window_df

    def _add_causal_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds rolling statistical aggregates.
        Strict rule: window T only includes data from (T - K + 1) to T.
        No future records are ever referenced.
        """
        k = self.rolling_window_count
        res = df.copy()

        # Rolling means for key intensity metrics
        res[f"rolling_{k}_flow_count"] = res["flow_count"].rolling(window=k, min_periods=1).mean()
        res[f"rolling_{k}_total_packets"] = res["total_packets"].rolling(window=k, min_periods=1).mean()
        res[f"rolling_{k}_total_bytes"] = res["total_bytes"].rolling(window=k, min_periods=1).mean()
        res[f"rolling_{k}_avg_byte_rate"] = res["avg_byte_rate"].rolling(window=k, min_periods=1).mean()
        res[f"rolling_{k}_unique_sources"] = res["unique_sources"].rolling(window=k, min_periods=1).mean()

        return res
