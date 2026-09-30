# SENTRANET SIH 2026: Demo Runbook

This document provides exact, deterministic steps to demonstrate SENTRANET end-to-end for the SIH 2026 presentation.

## 1. Prerequisites

- **Python 3.10+** (Tested with 3.10, 3.11, 3.12, 3.13)
- **Node.js 18+** and npm
- **macOS / Linux / Windows WSL**

## 2. Install Dependencies

### Backend
Navigate to the `backend` directory and create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
Navigate to the `frontend` directory and install NPM packages:
```bash
cd frontend
npm install
```

## 3. Configure Environment

Ensure a `.env` file exists in the project root if you are overriding defaults. The system is designed to work out-of-the-box using the sensible defaults mapped in `.env.example`. 

You can simply copy the example:
```bash
cp .env.example .env
```

## 4. Run the Deterministic Demo

To run the complete system with one command, execute:
```bash
./scripts/run_demo.sh
```

**What this does:**
1. Starts the FastAPI Backend on port 8000.
2. Starts the React Frontend on port 5173.
3. Automates an API call to start the **Synthetic Telemetry Stream** using a deterministic profile (`scenario_1`) and a fixed random seed (`42`).

*Note: If you prefer to start them separately, see the "Manual Startup" section below.*

## 5. What Should Appear

1. Open your browser and navigate to **http://localhost:5173**.
2. You will see the **SENTRANET SOC Dashboard**.
3. At the top, verify the banner says **SYNTHETIC STREAM // SIMULATION**. This ensures scientific honesty for the judges—we are not faking live network traffic.
4. The **System Status** bar should show `CONNECTED` and all ML models as `LOADED`.
5. The **Current Risk** card will begin updating every 5 seconds.

## 6. How to Observe the Scenario (The "Golden Path")

The deterministic synthetic stream is programmed to simulate the following phases:

1.  **T=0s to T=30s (Baseline):** 
    *   Risk score remains low (green).
    *   Explainability panel shows normal behavior.
2.  **T=30s to T=60s (Scanning/Reconnaissance):**
    *   Anomaly score will spike first as novel ports are scanned.
    *   Risk increases to `ELEVATED` (yellow).
3.  **T=60s+ (Active Attack):**
    *   XGBoost classifies malicious flows (e.g., DDoS or Brute Force).
    *   Risk reaches `CRITICAL` (red).
    *   **Forecasting Engine triggers**: You will see the Forecast Evidence Card light up, predicting emergence.
4.  **Alert Generation:**
    *   Once risk thresholds are crossed, an Alert is generated and appears in the **Alert Feed** on the left.
5.  **Incident Creation:**
    *   The Incident Manager correlates the alerts into a single **Active Incident**.

## 7. How to Inspect Explanations

1. **Real-time Explainability:** Look at the **AI Decision Explainability** panel directly on the dashboard. It updates live with the math decomposing the Risk Score into Anomaly vs. Classification components, and the Top Signals driving the XGBoost inference.
2. **Post-Mortem Dossier:** Click on the **Active Incident** card (or an incident in the table). This opens the **Incident Dossier**.
3. Navigate through the tabs: **Overview, Evidence, Risk, Forecast, Timeline** to show the judges how the AI arrived at its conclusion without hallucinating data.

## 8. How to Stop and Reset

To stop the demo, simply go back to your terminal where `./scripts/run_demo.sh` is running and press `Ctrl+C`. This will gracefully kill the backend and frontend processes.

To clear the system state for a fresh demo:
1. Restart the backend.
2. The internal ML states, chronological caches, and active incidents reset to zero on initialization. There are no stale databases to clear—the entire prototype runs statefully in memory for reliable, reproducible demos.

---

### Manual Startup (Optional)

If you need to start the components separately for debugging:

**Terminal 1 (Backend):**
```bash
PYTHONPATH=. backend/.venv/bin/python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

**Terminal 3 (Trigger Stream):**
```bash
curl -X POST http://127.0.0.1:8000/api/telemetry/synthetic/start -H "Content-Type: application/json" -d '{"profile": "scenario_1", "speed": 1.0, "seed": 42}'
```
