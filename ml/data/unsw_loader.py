"""Dataset adapter for University of New South Wales UNSW-NB15 benchmark."""

import os
from typing import Optional, List
import pandas as pd
from ml.data.base_loader import BaseDatasetLoader
from ml.preprocessing.labels import normalize_label
import logging

logger = logging.getLogger("sentranet.loader.unsw_nb15")

class UNSWNB15Loader(BaseDatasetLoader):
    """
    Adapter for the UNSW-NB15 cybersecurity flow dataset.
    Maps NetFlow attributes and attack category labels to canonical SENTRANET schema.
    """

    COLUMN_MAP = {
        "dur": "flow_duration",
        "spkts": "forward_packet_count",
        "dpkts": "backward_packet_count",
        "sbytes": "forward_bytes",
        "dbytes": "backward_bytes",
        "rate": "packet_rate",
        "sload": "byte_rate",
        "sinpkt": "inter_arrival_time",
        "smean": "average_packet_size",
        "proto": "protocol",
        "sport": "source_port",
        "dsport": "destination_port",
        "srcip": "source_ip",
        "dstip": "destination_ip",
        "attack_cat": "original_label",
        "label": "binary_label",
    }

    def __init__(self, raw_data_path: str = "data/raw/unsw_nb15"):
        super().__init__("unsw_nb15", raw_data_path)

    def load(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        if not os.path.exists(self.raw_data_path):
            logger.warning(f"Raw data path {self.raw_data_path} does not exist")
            return pd.DataFrame()

        if os.path.isfile(self.raw_data_path):
            files = [self.raw_data_path]
        elif os.path.isdir(self.raw_data_path):
            files = [
                os.path.join(self.raw_data_path, f)
                for f in os.listdir(self.raw_data_path)
                if f.endswith(".csv") or f.endswith(".parquet")
            ]
        else:
            files = []

        if not files:
            logger.warning(f"No CSV/Parquet files found in {self.raw_data_path}")
            return pd.DataFrame()

        dfs = []
        rows_loaded = 0
        for f in files:
            try:
                if f.endswith(".parquet"):
                    df_chunk = pd.read_parquet(f)
                else:
                    nrows = (max_rows - rows_loaded) if max_rows else None
                    df_chunk = pd.read_csv(f, nrows=nrows, low_memory=False)
                dfs.append(df_chunk)
                rows_loaded += len(df_chunk)
                if max_rows and rows_loaded >= max_rows:
                    break
            except Exception as e:
                logger.error(f"Error loading {f}: {e}")

        if not dfs:
            return pd.DataFrame()

        df = pd.concat(dfs, ignore_index=True)
        self.metadata["file_count"] = len(files)
        self.metadata["raw_row_count"] = len(df)
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty:
            return False
        cols = [c.strip().lower() for c in df.columns]
        return any(c in ["dur", "spkts", "sbytes"] for c in cols)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        res = df.copy()
        res.columns = [c.strip().lower() for c in res.columns]

        renamed = {}
        for col in res.columns:
            if col in self.COLUMN_MAP:
                renamed[col] = self.COLUMN_MAP[col]
        res = res.rename(columns=renamed)

        if "original_label" in res.columns:
            res["label"] = res["original_label"].apply(lambda lbl: normalize_label(lbl, "unsw_nb15"))
        elif "binary_label" in res.columns:
            res["original_label"] = res["binary_label"].map({0: "Normal", 1: "Attack"}).fillna("Normal")
            res["label"] = res["original_label"].apply(lambda lbl: normalize_label(lbl, "unsw_nb15"))
        else:
            res["original_label"] = "Normal"
            res["label"] = "BENIGN"

        return res
