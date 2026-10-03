"""
SENTRANET — Central Service Manager (Phase 7)
Orchestrates thread-safe access to ML inference engines, alert state machine,
incident correlation, and timeline state.
"""

from typing import Dict, Any, List, Optional, Callable
import threading
import datetime
import pandas as pd
import numpy as np

from ml.forecast.forecast_engine import ForecastEngine
from backend.replay.alert_state_machine import AlertStateMachine
from backend.replay.incident_manager import IncidentManager
from backend.replay.replay_event import ReplayEvent, AlertEvent
from backend.api.schemas.inference import AnalyzeRequest, AnalyzeResponse
from backend.api.schemas.alerts import CurrentAlertResponse, AlertItemResponse
from backend.api.schemas.incidents import IncidentItemResponse, IncidentDetailResponse
from backend.api.schemas.timeline import TimelineResponse, TimelinePointResponse
from backend.api.schemas.status import SystemStatusResponse
from backend.api.errors import ResourceNotFoundException, ConflictException, ServiceUnavailableException
from backend.api.services.serializers import (
    serialize_analyze_response,
    serialize_alert_event,
    serialize_incident_summary,
    serialize_incident_detail,
)
from backend.explainability.schemas import ExplanationResponse
from backend.explainability.explainer import build_explanation, invalidate_cache

class SentranetService:
    """
    Singleton service managing in-memory models and temporal pipeline state.
    """

    _instance: Optional["SentranetService"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.lock = threading.Lock()
        self.is_ready = False

        self.forecast_engine: Optional[ForecastEngine] = None
        self.incident_manager: Optional[IncidentManager] = None
        self.state_machine: Optional[AlertStateMachine] = None

        self.latest_timestamp: Optional[datetime.datetime] = None
        self.latest_decision: Optional[Dict[str, Any]] = None
        self.latest_alert_state: str = "NORMAL"
        self.latest_severity: str = "INFO"

        self.timeline_history: List[Dict[str, Any]] = []
        self.alert_history: List[AlertEvent] = []
        self.windows_processed_count: int = 0
        self.latest_features: Optional[Dict[str, float]] = None

        self.active_model_id: str = "sentranet_synthetic_v1"
        self.initialize_models()

    @classmethod
    def get_instance(cls) -> "SentranetService":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def initialize_models(self) -> None:
        """Initializes and caches models and engines exactly once (or on reload)."""
        from backend.api.services.model_registry import ModelRegistry
        try:
            entry = ModelRegistry.get_model(self.active_model_id)
            self.forecast_engine = ForecastEngine(
                xgb_model_path=entry.xgboost_artifact,
                if_model_path=entry.isolation_forest_artifact
            )
            # Retain existing instances if already created to avoid losing incident state,
            # but usually it's fine. For safety, we keep incident_manager if it exists.
            if self.incident_manager is None:
                self.incident_manager = IncidentManager()
            if self.state_machine is None:
                self.state_machine = AlertStateMachine(incident_manager=self.incident_manager)
            self.is_ready = True
        except Exception as e:
            self.is_ready = False
            raise ServiceUnavailableException(
                code="MODEL_INITIALIZATION_FAILED",
                message=f"Failed to initialize SENTRANET models for {self.active_model_id}: {str(e)}"
            )
            
    def set_active_model(self, model_id: str) -> None:
        """Changes the active model and reinitializes the pipeline engines."""
        with self.lock:
            # Check validity first before updating state
            from backend.api.services.model_registry import ModelRegistry
            ModelRegistry.get_model(model_id)
            
            self.active_model_id = model_id
            self.initialize_models()

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Executes chronological analysis on a single telemetry window.
        Enforces strict timestamp ordering and canonical feature alignment.
        """
        if not self.is_ready or self.forecast_engine is None:
            raise ServiceUnavailableException(message="SENTRANET models not initialized")

        with self.lock:
            curr_dt = pd.to_datetime(request.timestamp).to_pydatetime()

            # Temporal Causality & Duplicate Check
            if self.latest_timestamp is not None:
                if curr_dt < self.latest_timestamp:
                    raise ConflictException(
                        code="OUT_OF_ORDER_TIMESTAMP",
                        message=(
                            f"Inference timestamp '{request.timestamp}' precedes the current "
                            f"stream state '{self.latest_timestamp.isoformat()}'."
                        )
                    )
                elif curr_dt == self.latest_timestamp:
                    raise ConflictException(
                        code="DUPLICATE_TIMESTAMP",
                        message=f"Inference timestamp '{request.timestamp}' has already been processed."
                    )

            # Strict Canonical Feature Ordering
            canonical_names = self.forecast_engine.classifier.expected_features
            features_dict = request.features.model_dump()
            feature_vector = np.array([[features_dict[name] for name in canonical_names]], dtype=np.float64)

            # 1. Update ML Pipeline (XGBoost, Isolation Forest, Risk Fusion, Trajectory, Forecast)
            decision = self.forecast_engine.update(feature_vector, timestamp=request.timestamp)

            # 2. Update Alert State Machine
            alert_state, severity, newly_emitted_alerts = self.state_machine.process_decision(decision)

            # 3. Update Internal State
            self.latest_timestamp = curr_dt
            self.latest_decision = decision
            self.latest_alert_state = alert_state
            self.latest_severity = severity
            self.latest_features = features_dict
            self.windows_processed_count += 1
            invalidate_cache()

            # Append to timeline
            self.timeline_history.append({
                "timestamp": str(decision["timestamp"]),
                "risk_score": float(round(decision["risk_score"], 4)),
                "risk_state": str(decision["risk_state"]),
                "anomaly_score": float(round(decision["anomaly_score"], 4)),
                "attack_class": str(decision["predicted_class"]),
                "forecast_active": bool(decision.get("forecast_available", False)),
                "eta_seconds": int(decision["time_to_impact_seconds"]) if decision.get("time_to_impact_seconds") is not None else None,
            })
            if len(self.timeline_history) > 500:
                self.timeline_history.pop(0)

            # Append alerts
            self.alert_history.extend(newly_emitted_alerts)
            if len(self.alert_history) > 500:
                self.alert_history = self.alert_history[-500:]

            active_inc_id = (
                self.incident_manager.active_incident.incident_id
                if self.incident_manager.active_incident
                else None
            )

            return serialize_analyze_response(
                decision=decision,
                alert_state=alert_state,
                incident_id=active_inc_id,
                emitted_alerts=newly_emitted_alerts,
            )

    def sync_from_replay(
        self,
        replay_event: ReplayEvent,
        alert_events: List[AlertEvent],
        decision: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Synchronizes SentranetService state from replay engine iterations.
        Ensures timeline, alerts, latest decision, and current risk endpoints stay updated.
        """
        with self.lock:
            self.latest_timestamp = pd.to_datetime(replay_event.timestamp).to_pydatetime()
            self.latest_alert_state = replay_event.alert_state
            self.latest_severity = replay_event.severity
            self.latest_features = features
            self.windows_processed_count += 1
            invalidate_cache()

            if decision is not None:
                self.latest_decision = decision
            else:
                self.latest_decision = {
                    "timestamp": replay_event.timestamp,
                    "predicted_class": replay_event.attack_class,
                    "classification_confidence": replay_event.class_probability,
                    "anomaly_score": replay_event.anomaly_score,
                    "is_anomalous": replay_event.is_anomalous,
                    "risk_score": replay_event.risk_score,
                    "risk_state": replay_event.risk_state,
                    "risk_velocity": replay_event.risk_velocity,
                    "risk_acceleration": replay_event.risk_acceleration,
                    "risk_trend": replay_event.risk_trend,
                    "forecast_available": replay_event.forecast_active,
                    "forecast_class": replay_event.forecast_class,
                    "time_to_impact_seconds": replay_event.estimated_eta_seconds,
                    "forecast_confidence": replay_event.forecast_confidence,
                    "forecast_reason": replay_event.reasons,
                    "class_probabilities": {
                        replay_event.attack_class: replay_event.class_probability,
                        "BENIGN": max(0.0, 1.0 - replay_event.attack_likelihood),
                    },
                }

            self.timeline_history.append({
                "timestamp": str(replay_event.timestamp),
                "risk_score": float(round(replay_event.risk_score, 4)),
                "risk_state": str(replay_event.risk_state),
                "anomaly_score": float(round(replay_event.anomaly_score, 4)),
                "attack_class": str(replay_event.attack_class),
                "forecast_active": bool(replay_event.forecast_active),
                "eta_seconds": int(replay_event.estimated_eta_seconds) if replay_event.estimated_eta_seconds is not None else None,
            })
            if len(self.timeline_history) > 500:
                self.timeline_history.pop(0)

            self.alert_history.extend(alert_events)
            if len(self.alert_history) > 500:
                self.alert_history = self.alert_history[-500:]

    def reset_stream(self, is_replay_active_check: Optional[Callable[[], bool]] = None) -> Dict[str, Any]:
        """Resets all in-memory temporal state, trajectories, and incident caches."""
        with self.lock:
            if is_replay_active_check and is_replay_active_check():
                raise ConflictException(
                    code="STREAM_REPLAY_ACTIVE",
                    message="Cannot reset stream while a historical replay simulation is actively running."
                )

            if self.forecast_engine:
                self.forecast_engine.reset()
            if self.state_machine:
                self.state_machine.reset()
            if self.incident_manager:
                self.incident_manager.reset()

            self.latest_timestamp = None
            self.latest_decision = None
            self.latest_alert_state = "NORMAL"
            self.latest_severity = "INFO"
            self.latest_features = None
            self.timeline_history.clear()
            self.alert_history.clear()
            self.windows_processed_count = 0
            invalidate_cache()

            return {
                "status": "reset",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "simulation": True,
            }

    def get_current_risk(self) -> Dict[str, Any]:
        with self.lock:
            if self.latest_decision is None:
                raise ResourceNotFoundException(
                    code="NO_CURRENT_STATE",
                    message="No inference has been processed yet."
                )
            active_inc_id = (
                self.incident_manager.active_incident.incident_id
                if self.incident_manager and self.incident_manager.active_incident
                else None
            )
            return serialize_analyze_response(
                decision=self.latest_decision,
                alert_state=self.latest_alert_state,
                incident_id=active_inc_id,
                emitted_alerts=None,
            ).model_dump()

    def get_current_alert(self) -> CurrentAlertResponse:
        with self.lock:
            active_inc = self.incident_manager.active_incident if self.incident_manager else None
            is_active = active_inc is not None or self.latest_alert_state in {"WATCH", "ALERT"}

            inc_dict = active_inc.to_dict() if active_inc else None
            dec = self.latest_decision or {}

            return CurrentAlertResponse(
                active=is_active,
                incident=inc_dict,
                alert_state=self.latest_alert_state,
                severity=self.latest_severity,
                attack_class=dec.get("predicted_class"),
                risk_score=float(round(dec["risk_score"], 4)) if "risk_score" in dec else None,
                anomaly_score=float(round(dec["anomaly_score"], 4)) if "anomaly_score" in dec else None,
                forecast_active=bool(dec.get("forecast_available", False)),
                estimated_eta_seconds=dec.get("time_to_impact_seconds"),
                forecast_confidence=dec.get("forecast_confidence"),
                reasons=dec.get("forecast_reason") or [],
            )

    def get_current_explanation(self) -> Optional[ExplanationResponse]:
        """Returns ExplanationObject for the current streaming window."""
        with self.lock:
            if not self.is_ready or self.latest_decision is None or self.forecast_engine is None:
                raise ResourceNotFoundException(
                    code="NO_CURRENT_STATE",
                    message="No current telemetry state available."
                )
            
            return build_explanation(
                decision=self.latest_decision,
                feature_values=self.latest_features or {},
                booster=self.forecast_engine.classifier.booster,
                history_length=len(self.timeline_history),
                anomaly_threshold=self.forecast_engine.anomaly_detector.threshold,
                data_source="LIVE" if self.latest_features else "HISTORICAL_REPLAY",
                cls_weight=self.forecast_engine.risk_fusion.classification_weight,
                ano_weight=self.forecast_engine.risk_fusion.anomaly_weight,
            )

    def get_alerts(
        self,
        limit: int = 20,
        severity: Optional[str] = None,
        attack_class: Optional[str] = None,
    ) -> List[AlertItemResponse]:
        with self.lock:
            filtered = list(self.alert_history)
            if severity:
                filtered = [a for a in filtered if a.severity.lower() == severity.lower()]
            if attack_class:
                filtered = [a for a in filtered if a.attack_class.lower() == attack_class.lower()]

            safe_limit = max(1, min(limit, 100))
            recent = filtered[-safe_limit:]
            return [serialize_alert_event(ev) for ev in reversed(recent)]

    def get_incidents(self) -> List[IncidentItemResponse]:
        with self.lock:
            if not self.incident_manager:
                return []
            return [serialize_incident_summary(inc) for inc in self.incident_manager.incidents]

    def get_incident(self, incident_id: str) -> IncidentDetailResponse:
        with self.lock:
            if not self.incident_manager:
                raise ResourceNotFoundException(code="INCIDENT_NOT_FOUND", message="Incident not found.")

            match = next((inc for inc in self.incident_manager.incidents if inc.incident_id == incident_id), None)
            if not match:
                raise ResourceNotFoundException(code="INCIDENT_NOT_FOUND", message=f"Incident '{incident_id}' not found.")
            return serialize_incident_detail(match)

    def get_timeline(self, limit: int = 50) -> TimelineResponse:
        with self.lock:
            safe_limit = max(1, min(limit, 200))
            points = self.timeline_history[-safe_limit:]
            point_models = [TimelinePointResponse(**p) for p in points]
            return TimelineResponse(total_points=len(point_models), points=point_models)

    def get_system_status(self) -> SystemStatusResponse:
        with self.lock:
            return SystemStatusResponse(
                service="SENTRANET",
                status="ready" if self.is_ready else "uninitialized",
                simulation=True,
                models={
                    "xgboost": "loaded" if self.is_ready else "not_loaded",
                    "isolation_forest": "loaded" if self.is_ready else "not_loaded",
                },
                pipeline={
                    "risk_fusion": "ready" if self.is_ready else "not_ready",
                    "forecast_engine": "ready" if self.is_ready else "not_ready",
                    "alert_engine": "ready" if self.is_ready else "not_ready",
                    "incident_manager": "ready" if self.is_ready else "not_ready",
                },
                feature_count=17,
            )
