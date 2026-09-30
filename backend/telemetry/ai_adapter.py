"""
SENTRANET — AI Pipeline Adapter (Phase 9)
Connects aggregated 17-feature telemetry windows to the existing SENTRANET AI Core.
Enforces feature count, ordering, and finite value checks.
"""

from typing import Dict, Any, Optional
import math
import logging
from backend.api.schemas.inference import NetworkFeatures, AnalyzeRequest, AnalyzeResponse
from backend.api.services.sentranet_service import SentranetService
from backend.telemetry.window_aggregator import CANONICAL_17_FEATURES
from backend.api.errors import BadRequestException

logger = logging.getLogger("sentranet.telemetry.adapter")

class InvalidFeatureVectorException(BadRequestException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(code="FEATURE_VECTOR_INVALID", message=message, details=details or {})

class AIAdapter:
    """
    Adapter interfacing aggregated flow feature windows with the Phase 7 SentranetService.
    Does not duplicate ML inference or feature engineering.
    """

    def __init__(self, service: Optional[SentranetService] = None):
        self._service = service

    @property
    def service(self) -> SentranetService:
        if self._service is None:
            self._service = SentranetService.get_instance()
        return self._service

    def validate_features(self, features: Dict[str, float]) -> NetworkFeatures:
        """
        Validates feature vector against the 17 canonical features.
        Raises InvalidFeatureVectorException if validation fails.
        """
        # 1. Feature existence check
        missing = [f for f in CANONICAL_17_FEATURES if f not in features]
        if missing:
            raise InvalidFeatureVectorException(
                message=f"Feature vector is missing canonical features: {missing}",
                details={"missing": missing}
            )

        # 2. Check for NaN, Infinity, and non-negativity
        safe_kwargs = {}
        for feat_name in CANONICAL_17_FEATURES:
            val = features[feat_name]
            if val is None or math.isnan(val):
                raise InvalidFeatureVectorException(
                    message=f"Feature '{feat_name}' is NaN.",
                    details={"feature": feat_name}
                )
            if math.isinf(val):
                raise InvalidFeatureVectorException(
                    message=f"Feature '{feat_name}' is Infinite.",
                    details={"feature": feat_name}
                )
            if val < 0.0:
                raise InvalidFeatureVectorException(
                    message=f"Feature '{feat_name}' cannot be negative (got {val}).",
                    details={"feature": feat_name, "value": val}
                )
            safe_kwargs[feat_name] = float(val)

        return NetworkFeatures(**safe_kwargs)

    def analyze_window(
        self, timestamp: str, features: Dict[str, float]
    ) -> AnalyzeResponse:
        """
        Passes a validated feature window to the existing SentranetService.
        Returns the unified AnalyzeResponse / DecisionObject.
        """
        typed_features = self.validate_features(features)
        request = AnalyzeRequest(
            timestamp=timestamp,
            features=typed_features
        )
        return self.service.analyze(request)
