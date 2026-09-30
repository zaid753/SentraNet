"""End-to-end data preprocessing and feature pipeline for SENTRANET."""

from typing import Dict, Any, Tuple, Optional, List
import os
import json
import time
import datetime
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
import logging

from ml.data.registry import DatasetRegistry
from ml.preprocessing.cleaner import DataCleaner, DatasetQualityReport
from ml.preprocessing.features import FeatureEngineer, FeatureRegistry
from ml.preprocessing.windowing import TemporalWindowAggregator
from ml.preprocessing.scaler import SafeFeatureScaler
from ml.preprocessing.labels import TARGET_CLASSES

logger = logging.getLogger("sentranet.pipeline")

class PreprocessingPipeline:
    """
    Orchestrates raw dataset normalization, cleaning, feature derivation,
    temporal sequence aggregation, chronological splitting, and leakage-safe scaling.
    """

    def __init__(
        self,
        dataset_name: str,
        window_size_seconds: int = 60,
        rolling_window_count: int = 5,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        scaler_type: str = "standard",
        random_seed: int = 42,
    ):
        self.dataset_name = dataset_name
        self.window_size_seconds = window_size_seconds
        self.rolling_window_count = rolling_window_count
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.scaler_type = scaler_type
        self.random_seed = random_seed

        # Submodules
        self.cleaner = DataCleaner(dataset_name)
        self.engineer = FeatureEngineer()
        self.aggregator = TemporalWindowAggregator(window_size_seconds, rolling_window_count)
        self.scaler = SafeFeatureScaler(scaler_type)
        self.label_encoder = LabelEncoder()

    def run(
        self,
        input_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        max_rows: Optional[int] = None,
        enable_windowing: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the complete pipeline:
        raw input -> normalize -> clean -> engineer features -> window -> split -> scale -> save
        """
        start_time = time.time()
        logger.info(f"Initiating SENTRANET data pipeline for '{self.dataset_name}'")

        # 1. Load Data via Registry
        loader = DatasetRegistry.get_loader(self.dataset_name, input_path)
        raw_df = loader.load(max_rows=max_rows)

        if raw_df.empty:
            raise ValueError(f"No records loaded for dataset '{self.dataset_name}' from path '{input_path}'")

        logger.info(f"Loaded {len(raw_df)} raw records")

        # 2. Normalize Schema
        normalized_df = loader.normalize(raw_df)

        # 3. Clean Data & Generate Quality Report
        cleaned_df, quality_report = self.cleaner.clean(normalized_df)

        if cleaned_df.empty:
            raise ValueError("All records were removed during cleaning.")

        # 4. Feature Engineering
        engineered_df, model_features = self.engineer.engineer_features(cleaned_df)

        # 5. Temporal Windowing (if timestamps present and enabled)
        has_timestamps = quality_report.timestamp_available
        if enable_windowing and has_timestamps:
            logger.info("Aggregating flows into temporal windows...")
            processed_data = self.aggregator.aggregate_windows(engineered_df)
            if processed_data.empty:
                logger.warning("Windowing produced empty DataFrame; falling back to flow-level records")
                processed_data = engineered_df
                is_windowed = False
            else:
                is_windowed = True
                # Update feature list for windowed features
                numeric_window_cols = [
                    c for c in processed_data.select_dtypes(include=[np.number]).columns
                    if c not in ["window_id"]
                ]
                model_features = numeric_window_cols
        else:
            processed_data = engineered_df
            is_windowed = False

        # 6. Chronological Train / Validation / Test Split
        n = len(processed_data)
        train_end = int(n * self.train_ratio)
        val_end = int(n * (self.train_ratio + self.val_ratio))

        train_df = processed_data.iloc[:train_end].copy()
        val_df = processed_data.iloc[train_end:val_end].copy()
        test_df = processed_data.iloc[val_end:].copy()

        if len(train_df) == 0 or len(val_df) == 0 or len(test_df) == 0:
            raise ValueError(
                f"Split generated empty partitions: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}"
            )

        logger.info(f"Chronological Split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

        # 7. Safe Scaling (Fit ON TRAIN ONLY, transform Val/Test)
        numeric_features = [f for f in model_features if f in train_df.columns]
        self.scaler.fit(train_df, numeric_features)
        train_df = self.scaler.transform(train_df)
        val_df = self.scaler.transform(val_df)
        test_df = self.scaler.transform(test_df)

        # 8. Label Encoding (Fit ON TARGET_CLASSES + train labels, transform all)
        all_possible_classes = list(set(TARGET_CLASSES + list(train_df["label"].unique())))
        self.label_encoder.fit(all_possible_classes)
        train_df["label_encoded"] = self.label_encoder.transform(train_df["label"])
        val_df["label_encoded"] = self.label_encoder.transform(val_df["label"])
        test_df["label_encoded"] = self.label_encoder.transform(test_df["label"])

        # Measure Class Distribution in output
        class_distribution = processed_data["label"].value_counts().to_dict()
        class_percentages = (processed_data["label"].value_counts(normalize=True) * 100).round(2).to_dict()

        # 9. Save Artifacts & Processed Files
        target_out = output_dir or f"data/processed/{self.dataset_name}"
        artifacts_dir = os.path.join(target_out, "artifacts")
        os.makedirs(target_out, exist_ok=True)
        os.makedirs(artifacts_dir, exist_ok=True)

        # Save Parquet datasets
        train_path = os.path.join(target_out, "train.parquet")
        val_path = os.path.join(target_out, "validation.parquet")
        test_path = os.path.join(target_out, "test.parquet")

        train_df.to_parquet(train_path, index=False)
        val_df.to_parquet(val_path, index=False)
        test_df.to_parquet(test_path, index=False)

        # Also save CSV for easy inspection
        train_df.head(100).to_csv(os.path.join(target_out, "train_sample.csv"), index=False)

        # Save Model Artifacts for Phase 3
        scaler_path = os.path.join(artifacts_dir, "scaler.joblib")
        encoder_path = os.path.join(artifacts_dir, "label_encoder.joblib")
        features_path = os.path.join(target_out, "feature_names.json")
        schema_path = os.path.join(target_out, "schema.json")
        report_path = os.path.join(target_out, "quality_report.json")
        metadata_path = os.path.join(target_out, "preprocessing_metadata.json")

        self.scaler.save(scaler_path)
        joblib.dump(self.label_encoder, encoder_path)

        with open(features_path, "w", encoding="utf-8") as f:
            json.dump({"features": numeric_features, "count": len(numeric_features)}, f, indent=2)

        schema_dict = {
            col: str(dtype) for col, dtype in processed_data.dtypes.items()
        }
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)

        quality_report.save_json(report_path)

        total_runtime = round(time.time() - start_time, 4)
        metadata = {
            "dataset_name": self.dataset_name,
            "processing_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "pipeline_version": "0.2.0",
            "is_windowed": is_windowed,
            "window_size_seconds": self.window_size_seconds if is_windowed else None,
            "train_rows": len(train_df),
            "validation_rows": len(val_df),
            "test_rows": len(test_df),
            "feature_count": len(numeric_features),
            "classes": self.label_encoder.classes_.tolist(),
            "class_distribution": class_distribution,
            "class_percentages": class_percentages,
            "runtime_seconds": total_runtime,
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Pipeline executed successfully in {total_runtime}s. Artifacts saved to {target_out}")
        return metadata
