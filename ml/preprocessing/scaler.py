"""Configurable feature scaler enforcing strict fit-on-train-only data leakage prevention."""

from typing import List, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
import joblib
import logging

logger = logging.getLogger("sentranet.scaler")

class SafeFeatureScaler:
    """
    Standardizes numeric feature distributions.
    
    Guarantees:
    - Fits strictly on training split.
    - Transforms validation and test sets using parameters learned from train.
    - Serializes fitted scaler to joblib for Phase 3 model inference reuse.
    """

    def __init__(self, scaler_type: str = "standard"):
        self.scaler_type = scaler_type.lower()
        if self.scaler_type == "robust":
            self.scaler = RobustScaler()
        elif self.scaler_type == "minmax":
            self.scaler = MinMaxScaler()
        else:
            self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit(self, train_df: pd.DataFrame, feature_names: List[str]) -> "SafeFeatureScaler":
        """Fit scaler exclusively on training partition."""
        self.feature_names = [f for f in feature_names if f in train_df.columns]
        if not self.feature_names:
            raise ValueError("No matching features found in training data to fit scaler.")

        X = train_df[self.feature_names].values.astype(np.float64)
        # Check and replace any leftover NaN/inf with 0.0 before fitting
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        self.scaler.fit(X)
        self.is_fitted = True
        logger.info(f"Fitted {self.scaler_type} scaler on {len(X)} training samples across {len(self.feature_names)} features")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms a DataFrame using previously fitted scaler parameters."""
        if not self.is_fitted:
            raise RuntimeError("SafeFeatureScaler must be fitted on training data before transforming.")

        res = df.copy()
        X = res[self.feature_names].values.astype(np.float64)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        transformed = self.scaler.transform(X)
        for idx, col in enumerate(self.feature_names):
            res[col] = transformed[:, idx]

        return res

    def save(self, filepath: str) -> None:
        """Save fitted scaler to disk."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save an unfitted scaler.")
        joblib.dump({"scaler": self.scaler, "features": self.feature_names, "type": self.scaler_type}, filepath)
        logger.info(f"Saved scaler artifact to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "SafeFeatureScaler":
        """Load fitted scaler from disk."""
        data = joblib.load(filepath)
        instance = cls(scaler_type=data["type"])
        instance.scaler = data["scaler"]
        instance.feature_names = data["features"]
        instance.is_fitted = True
        return instance
