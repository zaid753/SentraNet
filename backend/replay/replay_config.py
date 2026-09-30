"""
SENTRANET — Replay Configuration Module (Phase 6)
Loads and validates configuration for historical replay streaming and alert state machine.
"""

from typing import Dict, Any, Optional
import os
import yaml
from dataclasses import dataclass, field

DEFAULT_REPLAY_CONFIG_PATH = "config/replay.yaml"

@dataclass
class ReplaySettings:
    default_mode: str = "batch"          # batch, realtime, step
    default_speed: float = 10.0          # Speed multiplier for realtime mode
    step_pause: bool = True              # Interactive pause in step mode
    default_dataset: str = "data/processed/sample/validation.parquet"

@dataclass
class AlertSettings:
    resolution_consecutive_windows: int = 2
    cooldown_seconds: float = 120.0

@dataclass
class OutputSettings:
    output_dir: str = "reports/replay"
    save_events: bool = True
    save_alerts: bool = True
    save_summary: bool = True

@dataclass
class ReplayConfig:
    replay: ReplaySettings = field(default_factory=ReplaySettings)
    alerts: AlertSettings = field(default_factory=AlertSettings)
    output: OutputSettings = field(default_factory=OutputSettings)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "ReplayConfig":
        path = config_path or DEFAULT_REPLAY_CONFIG_PATH
        if not os.path.exists(path):
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        replay_data = data.get("replay", {})
        alerts_data = data.get("alerts", {})
        output_data = data.get("output", {})

        return cls(
            replay=ReplaySettings(
                default_mode=replay_data.get("default_mode", "batch"),
                default_speed=float(replay_data.get("default_speed", 10.0)),
                step_pause=bool(replay_data.get("step_pause", True)),
                default_dataset=replay_data.get("default_dataset", "data/processed/sample/validation.parquet"),
            ),
            alerts=AlertSettings(
                resolution_consecutive_windows=int(alerts_data.get("resolution_consecutive_windows", 2)),
                cooldown_seconds=float(alerts_data.get("cooldown_seconds", 120.0)),
            ),
            output=OutputSettings(
                output_dir=output_data.get("output_dir", "reports/replay"),
                save_events=bool(output_data.get("save_events", True)),
                save_alerts=bool(output_data.get("save_alerts", True)),
                save_summary=bool(output_data.get("save_summary", True)),
            ),
        )
