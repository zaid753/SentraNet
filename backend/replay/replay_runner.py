"""
SENTRANET — Replay Runner Module (Phase 6)
Executes replay streams, handles SOC CLI formatting, and exports report artifacts to reports/replay/.
"""

from typing import Dict, Any, List, Optional
import os
import json
import pandas as pd

from backend.replay.replay_config import ReplayConfig
from backend.replay.replay_engine import ReplayEngine
from backend.replay.replay_event import ReplayEvent, AlertEvent

class ReplayRunner:
    """
    Coordinates execution of ReplayEngine from CLI/scripts.
    Renders SOC-style terminal events and saves JSONL/JSON artifacts.
    """

    def __init__(self, config: Optional[ReplayConfig] = None):
        self.config = config or ReplayConfig.load()
        self.engine = ReplayEngine(config=self.config)

    def run(
        self,
        dataset_path: Optional[str] = None,
        mode: str = "batch",
        speed: float = 10.0,
        max_windows: Optional[int] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Runs the full replay stream and outputs artifacts.
        """
        data_path = dataset_path or self.config.replay.default_dataset
        self.engine.mode = mode
        self.engine.speed = speed
        self.engine.clock.mode = mode
        self.engine.clock.speed_multiplier = speed

        # Handle "full" or "synthetic" shortcuts
        if data_path in {"full", "synthetic", "all"}:
            train_df = pd.read_parquet("data/processed/sample/train.parquet")
            val_df = pd.read_parquet("data/processed/sample/validation.parquet")
            test_df = pd.read_parquet("data/processed/sample/test.parquet")
            df = pd.concat([train_df, val_df, test_df], ignore_index=True)
            dataset_name = "full_synthetic_fixture"
        else:
            df = self.engine.load_dataset(data_path)
            dataset_name = os.path.basename(data_path)

        df_sorted = df.sort_values("window_start" if "window_start" in df.columns else "timestamp").reset_index(drop=True)
        if max_windows is not None and max_windows > 0:
            df_sorted = df_sorted.iloc[:max_windows]

        print("\n" + "=" * 60)
        print("SENTRANET HISTORICAL REPLAY")
        print(f"Mode     : {mode.upper()}")
        print(f"Dataset  : {dataset_name} ({len(df_sorted)} windows)")
        print(f"Speed    : {speed}x" if mode == "realtime" else f"Speed    : N/A ({mode.upper()})")
        print("Status   : RUNNING")
        print("=" * 60 + "\n")

        # Stream windows
        for replay_event, alert_events in self.engine.replay_stream(df_sorted):
            ts_str = replay_event.timestamp[11:19] if len(replay_event.timestamp) >= 19 else replay_event.timestamp

            # Compact state line
            if verbose or replay_event.alert_state in {"WATCH", "ALERT"} or alert_events:
                print(f"[{ts_str}]")
                print(f"Class       : {replay_event.attack_class}")
                if replay_event.attack_class != "BENIGN":
                    print(f"Probability : {replay_event.class_probability:.2f}")
                print(f"Anomaly     : {replay_event.anomaly_score:.2f}")
                print(f"Risk        : {replay_event.risk_score:.2f}")
                print(f"State       : {replay_event.alert_state}")
                if replay_event.risk_trend != "STABLE":
                    print(f"Trend       : {replay_event.risk_trend}")
                if replay_event.forecast_active:
                    print(f"Forecast    : YES ({replay_event.forecast_class})")
                    eta_str = f"{replay_event.estimated_eta_seconds}s" if replay_event.estimated_eta_seconds is not None else "0s"
                    print(f"ETA         : {eta_str}")

            # Alert events display
            for a_ev in alert_events:
                print(f"\n>>> {a_ev.event_type}")
                if a_ev.incident_id:
                    print(f"Incident    : {a_ev.incident_id}")
                print(f"Severity    : {a_ev.severity}")
                if a_ev.reasons:
                    print(f"Reason      : {a_ev.reasons[0]}")
                print()

        summary = self.engine.get_summary(dataset_identifier=dataset_name)

        print("=" * 60)
        print("SENTRANET REPLAY COMPLETE")
        print("=" * 60)
        print(f"Windows processed : {summary['number_of_windows']}")
        print(f"Incidents         : {summary['number_of_incidents']}")
        print(f"Forecast signals  : {summary['number_of_forecasts']}")
        print(f"Highest risk      : {summary['highest_risk']}")
        print(f"Highest anomaly   : {summary['highest_anomaly']}")
        print(f"Classes observed  : {', '.join(summary['attack_classes_seen'])}")
        print(f"Replay mode       : {summary['replay_mode'].upper()}")
        print(f"Simulation        : {str(summary['simulation']).upper()}")
        print("\nIMPORTANT:")
        print("This replay uses a historical/synthetic fixture.")
        print("It demonstrates pipeline and alert behavior.")
        print("It does not establish real-world forecasting performance.")
        print("=" * 60 + "\n")

        # Save artifacts
        if self.config.output.output_dir:
            out_dir = self.config.output.output_dir
            os.makedirs(out_dir, exist_ok=True)

            if self.config.output.save_events:
                events_file = os.path.join(out_dir, "replay_events.jsonl")
                with open(events_file, "w", encoding="utf-8") as f:
                    for ev in self.engine.replay_events:
                        f.write(json.dumps(ev.to_dict()) + "\n")

            if self.config.output.save_alerts:
                alerts_file = os.path.join(out_dir, "alert_events.jsonl")
                with open(alerts_file, "w", encoding="utf-8") as f:
                    for al in self.engine.alert_events:
                        f.write(json.dumps(al.to_dict()) + "\n")

            if self.config.output.save_summary:
                summary_file = os.path.join(out_dir, "replay_summary.json")
                with open(summary_file, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)

                incidents_file = os.path.join(out_dir, "incident_summary.json")
                inc_data = [inc.to_dict() for inc in self.engine.incident_manager.incidents]
                with open(incidents_file, "w", encoding="utf-8") as f:
                    json.dump(inc_data, f, indent=2)

        return summary
