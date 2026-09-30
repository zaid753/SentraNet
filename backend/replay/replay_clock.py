"""
SENTRANET — Replay Clock Module (Phase 6)
Provides simulated temporal pacing for historical stream replay.
"""

from typing import Optional, Callable, Any
import time
import datetime
import pandas as pd

class ReplayClock:
    """
    Simulated clock that paces playback across historical timestamps.
    Never alters original timestamps.
    """

    def __init__(
        self,
        mode: str = "batch",
        speed_multiplier: float = 10.0,
        step_prompt_fn: Optional[Callable[[str], bool]] = None,
    ):
        self.mode = mode.lower()
        if self.mode not in {"batch", "realtime", "step"}:
            raise ValueError(f"Invalid replay mode '{mode}'. Choose 'batch', 'realtime', or 'step'.")

        self.speed_multiplier = max(0.1, float(speed_multiplier))
        self.step_prompt_fn = step_prompt_fn

        self.current_simulated_time: Optional[datetime.datetime] = None
        self.previous_simulated_time: Optional[datetime.datetime] = None
        self.elapsed_simulated_seconds: float = 0.0

    def tick(self, timestamp: Any) -> float:
        """
        Advances the clock to the next historical timestamp.
        Sleeps or pauses according to configured mode.
        Returns the simulated delta in seconds from previous timestamp.
        """
        curr_dt = pd.to_datetime(timestamp).to_pydatetime()

        if self.current_simulated_time is None:
            self.current_simulated_time = curr_dt
            self.previous_simulated_time = curr_dt
            delta_seconds = 0.0
        else:
            self.previous_simulated_time = self.current_simulated_time
            self.current_simulated_time = curr_dt
            delta_seconds = max(0.0, (curr_dt - self.previous_simulated_time).total_seconds())

        self.elapsed_simulated_seconds += delta_seconds

        # Pacing behavior based on mode
        if self.mode == "realtime" and delta_seconds > 0:
            sleep_duration = delta_seconds / self.speed_multiplier
            # Cap sleep to 10 seconds to avoid extreme hangs in tests
            time.sleep(min(10.0, sleep_duration))
        elif self.mode == "step":
            if self.step_prompt_fn:
                cont = self.step_prompt_fn(f"[STEP] Window {curr_dt.strftime('%H:%M:%S')}. Continue? [Y/n]: ")
                if not cont:
                    raise KeyboardInterrupt("Replay stepped halted by user.")
            else:
                # Default CLI step
                try:
                    user_in = input(f"[STEP] Window {curr_dt.strftime('%H:%M:%S')}. Press Enter to continue (or 'q' to quit): ")
                    if user_in.strip().lower() == "q":
                        raise KeyboardInterrupt("Replay stepped halted by user.")
                except EOFError:
                    pass

        return delta_seconds

    def reset(self) -> None:
        self.current_simulated_time = None
        self.previous_simulated_time = None
        self.elapsed_simulated_seconds = 0.0
