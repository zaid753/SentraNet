"""Data cleaning and quality validation for network flow datasets."""

from typing import Dict, Any, Tuple, Optional
import time
import json
import logging
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger("sentranet.cleaner")

class DatasetQualityReport(BaseModel):
    dataset_name: str
    input_rows: int
    output_rows: int
    removed_rows: int
    missing_value_count: int
    infinite_value_count: int
    duplicate_count: int
    feature_count: int
    label_count: int
    timestamp_available: bool
    processing_time_seconds: float
    warnings: list[str] = Field(default_factory=list)

    def save_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

class DataCleaner:
    def __init__(self, dataset_name: str = "generic"):
        self.dataset_name = dataset_name

    @staticmethod
    def normalize_column_name(col: str) -> str:
        """Strip whitespace, lower-case, remove special characters."""
        col = col.strip().lower()
        col = col.replace("/", "_").replace(" ", "_").replace("-", "_").replace(".", "_")
        while "__" in col:
            col = col.replace("__", "_")
        return col.strip("_")

    def clean(
        self,
        df: pd.DataFrame,
        timestamp_col: Optional[str] = "timestamp",
        label_col: Optional[str] = "label",
    ) -> Tuple[pd.DataFrame, DatasetQualityReport]:
        """
        Cleans the network flow DataFrame:
        1. Normalizes column names
        2. Removes completely empty rows
        3. Replaces +/- infinity with NaN and logs counts
        4. Drops rows with missing critical labels or timestamps
        5. Handles duplicate rows
        6. Converts numeric fields safely
        7. Produces a comprehensive DatasetQualityReport
        """
        start_time = time.time()
        input_rows = len(df)
        warnings: list[str] = []

        if input_rows == 0:
            report = DatasetQualityReport(
                dataset_name=self.dataset_name,
                input_rows=0,
                output_rows=0,
                removed_rows=0,
                missing_value_count=0,
                infinite_value_count=0,
                duplicate_count=0,
                feature_count=0,
                label_count=0,
                timestamp_available=False,
                processing_time_seconds=0.0,
                warnings=["Input DataFrame is empty"],
            )
            return df, report

        # Step 1: Normalize column names
        cleaned_df = df.copy()
        cleaned_df.columns = [self.normalize_column_name(c) for c in cleaned_df.columns]

        # Step 2: Remove completely empty rows
        initial_empty = cleaned_df.isna().all(axis=1).sum()
        if initial_empty > 0:
            cleaned_df = cleaned_df.dropna(how="all")
            warnings.append(f"Dropped {initial_empty} completely blank rows")

        # Step 3: Identify and count Infinite values across numeric columns
        inf_count = 0
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            is_inf = np.isinf(cleaned_df[col])
            count = is_inf.sum()
            if count > 0:
                inf_count += count
                cleaned_df.loc[is_inf, col] = np.nan

        # Step 4: Missing value tracking
        missing_count = int(cleaned_df.isna().sum().sum())

        # Fill or drop NaNs
        # In network flow datasets, missing numeric metrics default to 0 or median
        for col in numeric_cols:
            if cleaned_df[col].isna().sum() > 0:
                cleaned_df[col] = cleaned_df[col].fillna(0.0)

        # Step 5: Duplicate rows
        duplicate_count = int(cleaned_df.duplicated().sum())
        if duplicate_count > 0:
            cleaned_df = cleaned_df.drop_duplicates()
            warnings.append(f"Removed {duplicate_count} duplicate flow records")

        # Step 6: Validate timestamp
        timestamp_available = False
        ts_candidates = [timestamp_col, "timestamp", "time", "date_time", "flow_start_time"]
        matched_ts = None
        for cand in ts_candidates:
            if cand and cand in cleaned_df.columns:
                matched_ts = cand
                break

        if matched_ts:
            try:
                cleaned_df["timestamp"] = pd.to_datetime(cleaned_df[matched_ts], errors="coerce")
                # Drop rows where timestamp is corrupted
                ts_invalid = cleaned_df["timestamp"].isna().sum()
                if ts_invalid > 0:
                    cleaned_df = cleaned_df.dropna(subset=["timestamp"])
                    warnings.append(f"Dropped {ts_invalid} rows with unparseable timestamps")
                # Sort chronologically
                cleaned_df = cleaned_df.sort_values(by="timestamp").reset_index(drop=True)
                timestamp_available = True
            except Exception as e:
                warnings.append(f"Timestamp parsing error on '{matched_ts}': {e}")
        else:
            warnings.append("No explicit timestamp column found in raw dataset")

        # Step 7: Validate label column
        lbl_candidates = [label_col, "label", "attack", "class", "target", "attack_cat"]
        matched_lbl = None
        for cand in lbl_candidates:
            if cand and cand in cleaned_df.columns:
                matched_lbl = cand
                break

        if matched_lbl:
            cleaned_df["label"] = cleaned_df[matched_lbl].astype(str)
            # Remove empty labels
            cleaned_df = cleaned_df[cleaned_df["label"].str.strip() != ""]
            label_count = cleaned_df["label"].nunique()
        else:
            cleaned_df["label"] = "BENIGN"
            label_count = 1
            warnings.append("No explicit label column found; defaulted to BENIGN")

        output_rows = len(cleaned_df)
        removed_rows = input_rows - output_rows
        duration = round(time.time() - start_time, 4)

        report = DatasetQualityReport(
            dataset_name=self.dataset_name,
            input_rows=input_rows,
            output_rows=output_rows,
            removed_rows=removed_rows,
            missing_value_count=missing_count,
            infinite_value_count=inf_count,
            duplicate_count=duplicate_count,
            feature_count=len(cleaned_df.columns),
            label_count=label_count,
            timestamp_available=timestamp_available,
            processing_time_seconds=duration,
            warnings=warnings,
        )

        logger.info(
            f"[{self.dataset_name}] Cleaning complete: {input_rows} -> {output_rows} rows "
            f"(Removed: {removed_rows} | Inf: {inf_count} | Dup: {duplicate_count}) in {duration}s"
        )

        return cleaned_df, report
