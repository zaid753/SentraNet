"""
SENTRANET — Chronological Replay Engine (Phase 6)
Orchestrates simulated temporal streaming across historical network windows.
Reuses existing Phase 2-5 pipelines with strict separation between runtime inference
and retrospective evaluation labels.
"""

from typing import Dict, Any, List, Optional, Callable, Generator, Tuple
import os
import datetime
import pandas as pd
import numpy as np

from ml.forecast.forecast_engine import ForecastEngine
from backend.replay.replay_config import ReplayConfig
from backend.replay.replay_clock import ReplayClock
from backend.replay.replay_event import ReplayEvent, AlertEvent
from backend.replay.incident_manager import IncidentManager
from backend.replay.alert_state_machine import AlertStateMachine

class ReplayEngine:
    """
    Main chronological replay engine.
    Streams preprocessed temporal windows through the complete Phase 3-5 ML stack
    and Phase 6 Alert State Machine without lookahead leakage.
    """

    def __init__(
        self,
        config: Optional[ReplayConfig] = None,
        forecast_engine: Optional[ForecastEngine] = None,
        mode: Optional[str] = None,
        speed: Optional[float] = None,
        incident_manager: Optional[IncidentManager] = None,
        state_machine: Optional[AlertStateMachine] = None,
    ):
        self.config = config or ReplayConfig.load()
        self.mode = mode or self.config.replay.default_mode
        self.speed = speed or self.config.replay.default_speed

        self.forecast_engine = forecast_engine or ForecastEngine()
        self.clock = ReplayClock(mode=self.mode, speed_multiplier=self.speed)
        self.incident_manager = incident_manager or IncidentManager(
            resolution_consecutive_windows=self.config.alerts.resolution_consecutive_windows,
            cooldown_seconds=self.config.alerts.cooldown_seconds,
        )
        self.state_machine = state_machine or AlertStateMachine(incident_manager=self.incident_manager)


        self.event_counter: int = 0
        self.replay_events: List[ReplayEvent] = []
        self.alert_events: List[AlertEvent] = []
        self.runtime_records: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self.clock.reset()
        self.forecast_engine.reset()
        self.state_machine.reset()
        self.incident_manager.reset()
        self.event_counter = 0
        self.replay_events = []
        self.alert_events = []
        self.runtime_records = []

    def load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """
        Loads dataset and guarantees chronological ascending order.
        Validates presence of 17 canonical features.
        """
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Replay dataset '{dataset_path}' not found.")

        df = pd.read_parquet(dataset_path)
        if len(df) == 0:
            raise ValueError(f"Replay dataset '{dataset_path}' is empty.")

        # Ensure timestamp column
        ts_col = "window_start" if "window_start" in df.columns else "timestamp"
        if ts_col not in df.columns:
            raise KeyError(f"Dataset missing timestamp column (expected 'window_start' or 'timestamp')")

        df_sorted = df.sort_values(ts_col).reset_index(drop=True)

        # Validate features exist
        expected_feats = self.forecast_engine.classifier.expected_features
        missing = [f for f in expected_feats if f not in df_sorted.columns]
        if missing:
            raise ValueError(f"Dataset missing required model features: {missing}")

        return df_sorted

    def replay_stream(
        self,
        df: pd.DataFrame,
        max_windows: Optional[int] = None,
        callback: Optional[Callable[[ReplayEvent, List[AlertEvent]], None]] = None,
    ) -> Generator[Tuple[ReplayEvent, List[AlertEvent]], None, None]:
        """
        Generator streaming temporal windows chronologically.
        Enforces strict runtime boundary: ground-truth labels are never passed to the ML pipeline.
        """
        self.reset()
        df_sorted = df.sort_values("window_start" if "window_start" in df.columns else "timestamp").reset_index(drop=True)

        if max_windows is not None and max_windows > 0:
            df_sorted = df_sorted.iloc[:max_windows]

        features_list = self.forecast_engine.classifier.expected_features

        for idx, row in df_sorted.iterrows():
            self.event_counter += 1
            ts = str(row.get("window_start", row.get("timestamp")))
            window_id = str(row.get("window_id", f"WIN-{idx:04d}"))
            actual_label = str(row.get("label", "UNKNOWN"))

            # 1. Clock advance (sleep/pause in realtime/step mode)
            self.clock.tick(ts)

            # 2. Strict Runtime Separation: Extract features ONLY (no label passed to ML)
            feature_row = df_sorted.iloc[[idx]][features_list]

            # 3. Model Inference Pipeline (XGBoost + Isolation Forest + Risk Fusion + Trajectory + Forecast)
            decision = self.forecast_engine.update(feature_row, timestamp=ts)

            # 4. Alert State Machine Update
            alert_state, severity, newly_emitted_alerts = self.state_machine.process_decision(decision)

            # 5. Assemble ReplayEvent
            event_id = f"EVT-{self.event_counter:04d}"
            replay_event = ReplayEvent(
                event_id=event_id,
                timestamp=ts,
                window_id=window_id,
                attack_class=decision["predicted_class"],
                class_probability=decision["classification_confidence"],
                attack_likelihood=round(1.0 - float(decision["class_probabilities"].get("BENIGN", 0.0)), 4),
                anomaly_score=decision["anomaly_score"],
                is_anomalous=decision["is_anomalous"],
                risk_score=decision["risk_score"],
                risk_state=decision["risk_state"],
                risk_velocity=decision["risk_velocity"],
                risk_acceleration=decision["risk_acceleration"],
                risk_trend=decision["risk_trend"],
                emergence_detected=decision.get("forecast_available", False),
                forecast_active=decision.get("forecast_available", False),
                forecast_class=decision.get("forecast_class"),
                estimated_eta_seconds=decision.get("time_to_impact_seconds"),
                forecast_confidence=decision.get("forecast_confidence"),
                reasons=decision.get("forecast_reason") or [],
                alert_state=alert_state,
                severity=severity,
                replay_mode=self.mode,
            )

            self.replay_events.append(replay_event)
            self.alert_events.extend(newly_emitted_alerts)

            # Post-hoc evaluation record (cleanly isolated)
            self.runtime_records.append({
                "event_id": event_id,
                "timestamp": ts,
                "window_id": window_id,
                "actual_label": actual_label,
                "predicted_class": decision["predicted_class"],
                "risk_score": decision["risk_score"],
                "alert_state": alert_state,
                "forecast_available": decision["forecast_available"],
            })

            if callback:
                callback(replay_event, newly_emitted_alerts)

            yield replay_event, newly_emitted_alerts

        # End of stream: Resolve any remaining active incident
        if len(df_sorted) > 0:
            final_ts = str(df_sorted.iloc[-1].get("window_start", df_sorted.iloc[-1].get("timestamp")))
            final_events = self.incident_manager.force_resolve_all(final_ts)
            self.alert_events.extend(final_events)

    def get_summary(self, dataset_identifier: str = "synthetic_fixture") -> Dict[str, Any]:
        """Compiles comprehensive replay summary statistics."""
        if not self.replay_events:
            return {
                "simulation": True,
                "evaluation_status": "historical_replay_only",
                "number_of_windows": 0,
            }

        risks = [e.risk_score for e in self.replay_events]
        anomalies = [e.anomaly_score for e in self.replay_events]
        classes_seen = sorted(list({e.attack_class for e in self.replay_events}))

        watch_count = sum(1 for e in self.alert_events if e.event_type.startswith("WATCH"))
        alert_count = sum(1 for e in self.alert_events if e.event_type == "ALERT_CREATED")
        forecast_count = sum(1 for e in self.alert_events if e.event_type == "FORECAST_TRIGGERED")
        total_incidents = len(self.incident_manager.incidents)
        resolved_incidents = sum(1 for inc in self.incident_manager.incidents if inc.status == "RESOLVED")

        return {
            "simulation": True,
            "evaluation_status": "historical_replay_only",
            "replay_mode": self.mode,
            "speed_multiplier": self.speed,
            "dataset_identifier": dataset_identifier,
            "replay_start": self.replay_events[0].timestamp,
            "replay_end": self.replay_events[-1].timestamp,
            "number_of_windows": len(self.replay_events),
            "number_of_watch_events": watch_count,
            "number_of_alerts": alert_count,
            "number_of_forecasts": forecast_count,
            "number_of_incidents": total_incidents,
            "number_of_resolved_incidents": resolved_incidents,
            "highest_risk": round(float(max(risks)), 4) if risks else 0.0,
            "highest_anomaly": round(float(max(anomalies)), 4) if anomalies else 0.0,
            "attack_classes_seen": classes_seen,
        }
