# SENTRANET Backend

FastAPI backend service powering the SENTRANET AI-based predictive network security platform (SIH 2026, Problem Statement: SIH26153).

## Purpose

The backend provides the REST and future real-time streaming backbone for network traffic ingestion, ML attack forecasting, risk escalation calculation, and SOC telemetry dissemination. In Phase 1, it implements the core service foundation, configuration management, health telemetry, and shared data contracts.

## Architecture

```
backend/
├── app/
│   ├── api/          # API route definitions and router aggregator
│   ├── core/         # Settings, logging, and error handling
│   ├── models/       # Pydantic schemas and shared data contracts
│   ├── services/     # Core domain logic (planned)
│   ├── ingestion/    # Network traffic & PCAP ingestion (planned)
│   ├── ml/           # Machine learning inference adapters (planned)
│   ├── storage/      # Persistence abstraction layer (planned)
│   ├── utils/        # Helper utilities
│   └── main.py       # Application factory, lifespan, CORS, error handling
├── tests/            # Test suite (pytest)
└── requirements.txt  # Phase 1 runtime dependencies
```

## Setup

1. **Create and activate virtual environment**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Backend

Start the development server with live reloading:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:
- Base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/health`
- System Status: `http://127.0.0.1:8000/api/system/status`

## Testing

Execute the test suite using pytest:
```bash
PYTHONPATH=. pytest tests/
```

## Environment Variables

Configured in `.env` (refer to `.env.example` in root):

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `SENTRANET` | Application name identifier |
| `APP_VERSION` | `0.1.0` | Semantic version |
| `BACKEND_HOST` | `127.0.0.1` | Host interface to bind |
| `BACKEND_PORT` | `8000` | Port number |
| `FRONTEND_URL` | `http://localhost:5173` | Allowed CORS origin |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `DATABASE_URL` | `""` | Database connection string (future) |
| `MODEL_PATH` | `""` | Path to trained model artifacts (future) |
| `DATA_PATH` | `./data` | Path to dataset directory |
