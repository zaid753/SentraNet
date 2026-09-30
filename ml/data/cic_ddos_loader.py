"""Dataset adapter for Canadian Institute for Cybersecurity CIC-DDoS2019 benchmark."""

import os
from typing import Optional
import pandas as pd
from ml.data.base_loader import BaseDatasetLoader
from ml.preprocessing.labels import normalize_label
import logging

logger = logging.getLogger("sentranet.loader.cic_ddos2019")

class CICDDoS2019Loader(BaseDatasetLoader):
    """
    Adapter for the CIC-DDoS2019 dataset.
    Normalizes specific DDoS reflection vectors (DrDoS_DNS, DrDoS_LDAP, Syn, etc.)
    into primary DDOS canonical class while preserving original attack subtype.
    """

    COLUMN_MAP = {
        "flow_duration": "flow_duration",
        "total_fwd_packets": "forward_packet_count",
        "total_backward_packets": "backward_packet_count",
        "total_length_of_fwd_packets": "forward_bytes",
        "total_length_of_bwd_packets": "backward_bytes",
        "flow_bytes_s": "byte_rate",
        "flow_packets_s": "packet_rate",
        "flow_iat_mean": "inter_arrival_time",
        "packet_length_variance": "packet_size_variance",
        "average_packet_size": "average_packet_size",
        "destination_port": "destination_port",
        "source_port": "source_port",
        "source_ip": "source_ip",
        "destination_ip": "destination_ip",
        "timestamp": "timestamp",
        "label": "label",
    }

    def __init__(self, raw_data_path: str = "data/raw/cic_ddos2019"):
        super().__init__("cic_ddos2019", raw_data_path)

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
        return any("duration" in c for c in cols) or any("flow" in c for c in cols)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        res = df.copy()
        res.columns = [
            c.strip().lower().replace(" ", "_").replace("/", "_").replace("-", "_").replace(".", "_")
            for c in res.columns
        ]

        renamed = {}
        for col in res.columns:
            if col in self.COLUMN_MAP:
                renamed[col] = self.COLUMN_MAP[col]
        res = res.rename(columns=renamed)

        if "label" in res.columns:
            res["original_label"] = res["label"].astype(str)
            res["label"] = res["label"].apply(lambda lbl: normalize_label(lbl, "cic_ddos2019"))
        else:
            res["original_label"] = "BENIGN"
            res["label"] = "BENIGN"

        return res
