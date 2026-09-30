# SENTRANET — Development Guide

## Prerequisites

- **Python**: Version 3.11+ (Python 3.13 tested and verified)
- **Node.js**: Version 18+ (Node 20+ recommended)
- **Package Managers**: `pip` and `npm`
- **Git**: Installed and configured

---

## Environment Setup

1. Copy the example environment configuration:
   ```bash
   cp .env.example .env
   ```

2. Configuration variables:
   ```env
   APP_NAME=SENTRANET
   APP_VERSION=0.1.0
   BACKEND_HOST=127.0.0.1
   BACKEND_PORT=8000
   FRONTEND_URL=http://localhost:5173
   LOG_LEVEL=INFO
   DATABASE_URL=
   MODEL_PATH=
   DATA_PATH=./data
   ```

---

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Initialize a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

---

## Running the Development Servers

### Terminal 1: Backend Service
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: `http://127.0.0.1:8000`
- Interactive API Docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Frontend Client
```bash
cd frontend
npm run dev
```
- Dashboard URL: `http://localhost:5173`

---

## Running Tests

### Backend Unit & Integration Tests
```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/
```

### Frontend Typechecking & Production Build
```bash
cd frontend
npm run build
```

---

## Troubleshooting

### 1. Frontend displays "Backend unavailable"
- Ensure the FastAPI server is running on `http://127.0.0.1:8000`.
- Verify CORS: Confirm `FRONTEND_URL=http://localhost:5173` matches your frontend origin.
- Check network tab in browser developer tools for connection errors.

### 2. Python Virtual Environment conflicts
- Ensure you activate `.venv` before running `pytest` or `uvicorn`.
- Always set `PYTHONPATH=.` when running tests from within the `backend` folder.

### 3. Port collisions
- If port 8000 is occupied, set `BACKEND_PORT` in `.env` and pass `--port <new_port>` to uvicorn. Update `VITE_API_URL` in `frontend/.env` accordingly.
