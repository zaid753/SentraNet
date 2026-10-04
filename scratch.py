import time
from backend.telemetry.flow_sources import LiveFlowSource
import logging
logging.basicConfig(level=logging.INFO)

src = LiveFlowSource()
src.start()
time.sleep(3)
rec = src.read()
if rec:
    print(f"Captured: {rec}")
else:
    print(f"No packets. State: {src.state}, Error: {src.error_message}")
src.stop()
