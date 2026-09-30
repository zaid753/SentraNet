"""Dataset inspection and exploratory quality reporting for SENTRANET."""

from typing import Dict, Any, Optional
import os
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("sentranet.inspector")

class DatasetInspector:
    """Generates detailed, human-readable inspection reports on raw or normalized datasets."""

    def __init__(self, dataset_name: str, input_path: str):
        self.dataset_name = dataset_name
        self.input_path = input_path

    def inspect(self, max_sample_rows: Optional[int] = 100000) -> Dict[str, Any]:
        """Inspects directory or file and computes summary metrics."""
        files_info = []
        total_size_bytes = 0

        if os.path.isdir(self.input_path):
            files = [
                os.path.join(self.input_path, f)
                for f in os.listdir(self.input_path)
                if f.endswith(".csv") or f.endswith(".parquet")
            ]
        elif os.path.isfile(self.input_path):
            files = [self.input_path]
        else:
            return {"error": f"Path '{self.input_path}' does not exist"}

        for f in files:
            size = os.path.getsize(f)
            total_size_bytes += size
            files_info.append({"filename": os.path.basename(f), "size_bytes": size, "path": f})

        if not files:
            return {
                "dataset_name": self.dataset_name,
                "file_count": 0,
                "status": "No raw CSV or Parquet files found",
            }

        # Load representative sample or complete dataset
        dfs = []
        for f in files:
            try:
                if f.endswith(".parquet"):
                    df = pd.read_parquet(f)
                else:
                    df = pd.read_csv(f, nrows=max_sample_rows, low_memory=False)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error reading {f}: {e}")

        if not dfs:
            return {"error": "Failed to read any files from target path"}

        full_df = pd.concat(dfs, ignore_index=True)
        nrows, ncols = full_df.shape

        # Column classification
        numeric_cols = full_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = full_df.select_dtypes(include=["object", "string", "category"]).columns.tolist()

        # Missing values & Infinity
        missing_count = int(full_df.isna().sum().sum())
        inf_count = 0
        for col in numeric_cols:
            inf_count += int(np.isinf(full_df[col]).sum())

        duplicate_count = int(full_df.duplicated().sum())

        # Check timestamp
        ts_candidates = ["timestamp", "time", "date_time", "flow_start_time"]
        matched_ts = None
        for c in full_df.columns:
            if c.strip().lower() in ts_candidates:
                matched_ts = c
                break

        # Check labels
        label_col = None
        for c in full_df.columns:
            if c.strip().lower() in ["label", "attack", "class", "attack_cat"]:
                label_col = c
                break

        label_dist = {}
        if label_col:
            label_dist = full_df[label_col].value_counts().to_dict()

        report = {
            "dataset_name": self.dataset_name,
            "target_path": self.input_path,
            "file_count": len(files),
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "sample_rows": nrows,
            "column_count": ncols,
            "columns": list(full_df.columns),
            "numeric_columns_count": len(numeric_cols),
            "categorical_columns_count": len(categorical_cols),
            "missing_values": missing_count,
            "infinite_values": inf_count,
            "duplicate_rows": duplicate_count,
            "timestamp_column": matched_ts,
            "timestamp_available": matched_ts is not None,
            "label_column": label_col,
            "label_distribution": label_dist,
        }

        return report

    @staticmethod
    def format_human_readable(report: Dict[str, Any]) -> str:
        """Formats the inspection dictionary into a clean CLI output."""
        if "error" in report:
            return f"[ERROR] {report['error']}"

        lines = [
            "=" * 60,
            f"SENTRANET DATASET INSPECTION: {report.get('dataset_name', 'UNKNOWN').upper()}",
            "=" * 60,
            f"Location:           {report.get('target_path')}",
            f"Discovered Files:   {report.get('file_count')} ({report.get('total_size_mb', 0)} MB)",
            f"Analyzed Rows:      {report.get('sample_rows', 0):,}",
            f"Total Columns:      {report.get('column_count', 0)} (Numeric: {report.get('numeric_columns_count', 0)}, Categorical: {report.get('categorical_columns_count', 0)})",
            f"Missing Values:     {report.get('missing_values', 0):,}",
            f"Infinite Values:    {report.get('infinite_values', 0):,}",
            f"Duplicate Records:  {report.get('duplicate_rows', 0):,}",
            f"Timestamp Field:    {report.get('timestamp_column') or 'None detected'}",
            "-" * 60,
            "LABEL DISTRIBUTION:",
        ]

        label_dist = report.get("label_distribution", {})
        if label_dist:
            for lbl, cnt in label_dist.items():
                lines.append(f"  • {lbl}: {cnt:,}")
        else:
            lines.append("  (No explicit label column detected)")

        lines.append("=" * 60)
        return "\n".join(lines)
