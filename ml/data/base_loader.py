"""Abstract Base Dataset Loader Interface for SENTRANET."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
import pandas as pd
import logging

logger = logging.getLogger("sentranet.loader")

class BaseDatasetLoader(ABC):
    """
    Abstract contract for benchmark dataset adapters.
    Ensures that any raw benchmark dataset (CICIDS2017, UNSW-NB15, CIC-DDoS2019)
    can be loaded and mapped into the canonical SENTRANET schema without altering
    downstream feature engineering or ML model code.
    """

    def __init__(self, dataset_name: str, raw_data_path: str):
        self.dataset_name = dataset_name
        self.raw_data_path = raw_data_path
        self.raw_columns: List[str] = []
        self.metadata: Dict[str, Any] = {
            "dataset_name": dataset_name,
            "raw_data_path": raw_data_path,
        }

    @abstractmethod
    def load(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        """
        Discovers raw files in raw_data_path and loads them into a single DataFrame.
        Supports optional max_rows limit for memory safety.
        """
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """Validates that loaded DataFrame contains the essential fields required by this adapter."""
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Maps raw dataset-specific column names into canonical SENTRANET columns:
        timestamp, source_ip, destination_ip, source_port, destination_port, protocol,
        flow_duration, forward_packet_count, backward_packet_count, forward_bytes,
        backward_bytes, label, original_label.
        """
        pass

    def get_features(self, df: pd.DataFrame) -> List[str]:
        """Returns list of numerical/behavioral flow feature columns."""
        return [c for c in df.columns if c not in ["source_ip", "destination_ip", "timestamp", "label", "original_label"]]

    def get_labels(self, df: pd.DataFrame) -> List[str]:
        """Returns unique class labels present in the dataset."""
        if "label" in df.columns:
            return df["label"].unique().tolist()
        return []

    def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata associated with the dataset source and local files."""
        return self.metadata
