#!/bin/bash
set -e

# SENTRANET SIH 2026 - Deterministic End-to-End Demo Script
# Problem Statement: SIH26153
# Theme: Blockchain & Cybersecurity

echo "=========================================================="
echo "    SENTRANET: From detecting attacks to forecasting them   "
echo "    SIH 2026 - Deterministic Demo Runner                    "
echo "=========================================================="
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "[1/4] Checking environment..."
if [ ! -d "backend/.venv" ]; then
    echo "ERROR: Virtual environment not found at backend/.venv"
    echo "Please create it and install dependencies: python -m venv backend/.venv && backend/.venv/bin/pip install -r backend/requirements.txt"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "ERROR: node_modules not found in frontend/"
    echo "Please install dependencies: cd frontend && npm install"
    exit 1
fi

echo "[2/4] Starting FastAPI Backend (Port 8000)..."
export PYTHONPATH="$PROJECT_ROOT"
backend/.venv/bin/python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
echo "Backend running with PID: $BACKEND_PID"

echo "Waiting for backend to initialize..."
sleep 3
# Check if backend is actually running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "ERROR: Backend failed to start. Check logs."
    exit 1
fi

echo "[3/4] Skipping separate frontend launch (now served by backend directly on Port 8000)"
# Wait a moment for frontend to bind
sleep 2

# Launch the stream
echo "Starting deterministic demo stream via API..."
curl -s -X POST http://127.0.0.1:8000/api/telemetry/synthetic/start \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "scenario_1",
    "speed": 1.0,
    "seed": 42
  }' > /dev/null

echo ""
echo "=========================================================="
echo "    DEMO IS LIVE!                                         "
echo "                                                          "
echo "    Access the SOC Dashboard at: http://localhost:8000    "
echo "    API Documentation at:        http://127.0.0.1:8000/docs"
echo "                                                          "
echo "    Press Ctrl+C to stop all services.                    "
echo "=========================================================="

# Cleanup function to kill background processes on exit
function cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    echo "Services stopped."
    exit 0
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT

# Keep script running
wait
