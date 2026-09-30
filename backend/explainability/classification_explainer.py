"""
SENTRANET — Classification Explainer (Phase 11)
Generates traceable classification explanations from XGBoost output.
Uses model-native feature importance (gain). No SHAP. No fabrication.
"""

from typing import Dict, List, Optional, Any
import os
import json
import numpy as np

from backend.explainability.feature_metadata import FEATURE_METADATA, CANONICAL_FEATURES, get_display_name
from backend.explainability.schemas import ClassificationExplanation, FeatureExplanation


# Global importance cache (loaded once, model-level)
_GLOBAL_IMPORTANCE_CACHE: Optional[Dict[str, float]] = None


def _load_global_importance(booster) -> Dict[str, float]:
    """
    Loads and normalizes global feature importance (gain) from XGBoost booster.
    Cached after first call. Returns normalized scores (sum = 1.0 approximately).
    """
    global _GLOBAL_IMPORTANCE_CACHE
    if _GLOBAL_IMPORTANCE_CACHE is not None:
        return _GLOBAL_IMPORTANCE_CACHE

    try:
        raw = booster.get_score(importance_type="gain")
        if not raw:
            _GLOBAL_IMPORTANCE_CACHE = {}
            return {}
        total = sum(raw.values())
        if total > 0:
            normalized = {k: v / total for k, v in raw.items()}
        else:
            normalized = {k: 0.0 for k in raw}
        _GLOBAL_IMPORTANCE_CACHE = normalized
        return normalized
    except Exception:
        _GLOBAL_IMPORTANCE_CACHE = {}
        return {}


def invalidate_importance_cache() -> None:
    """Call when model is reloaded (should not happen in frozen operation)."""
    global _GLOBAL_IMPORTANCE_CACHE
    _GLOBAL_IMPORTANCE_CACHE = None


def build_classification_explanation(
    predicted_class: str,
    class_probabilities: Dict[str, float],
    classification_confidence: float,
) -> ClassificationExplanation:
    """
    Builds classification explanation from actual XGBoost output.
    All values are directly derived from model output — no fabrication.
    """
    p_benign = float(class_probabilities.get("BENIGN", 0.0))
    attack_likelihood = float(max(0.0, 1.0 - p_benign))

    return ClassificationExplanation(
        predicted_class=predicted_class,
        confidence=round(classification_confidence, 4),
        all_probabilities={k: round(v, 4) for k, v in class_probabilities.items()},
        attack_likelihood=round(attack_likelihood, 4),
        p_benign=round(p_benign, 4),
    )


def build_feature_explanations(
    feature_values: Dict[str, float],
    booster,
) -> tuple[List[FeatureExplanation], List[FeatureExplanation]]:
    """
    Builds feature-level explanations for all 17 canonical features.

    Returns:
        Tuple of (all_features: List[FeatureExplanation], top_5: List[FeatureExplanation])
        top_5 sorted by global model importance (not prediction-specific).

    Notes:
        - importance is model-level (global), not prediction-level attribution.
        - values of features not in the current window are None.
        - importance labeled as model-level, not causal/prediction attribution.
    """
    global_importance = _load_global_importance(booster)

    # Build ranked importance (all canonical features present)
    # Features not in the booster's importance dict get 0.0
    importance_with_ranks = []
    for feat in CANONICAL_FEATURES:
        imp = global_importance.get(feat, 0.0)
        importance_with_ranks.append((feat, imp))

    importance_with_ranks.sort(key=lambda x: x[1], reverse=True)
    rank_map = {feat: idx + 1 for idx, (feat, _) in enumerate(importance_with_ranks)}

    all_features: List[FeatureExplanation] = []
    for feat in CANONICAL_FEATURES:
        meta = FEATURE_METADATA[feat]
        val = feature_values.get(feat)
        imp = global_importance.get(feat, 0.0)

        all_features.append(FeatureExplanation(
            feature=feat,
            display_name=meta["display_name"],
            category=meta["category"],
            current_value=round(float(val), 4) if val is not None else None,
            unit=meta.get("unit", ""),
            global_importance=round(imp, 6) if imp > 0.0 else None,
            importance_rank=rank_map.get(feat),
            description=meta["description"],
        ))

    # Top 5 by global importance
    top_features = sorted(all_features, key=lambda f: f.global_importance or 0.0, reverse=True)[:5]

    return all_features, top_features
