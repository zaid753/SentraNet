# SENTRANET — API Documentation

This document describes the Phase 1 operational REST endpoints and outlines planned endpoints for future development phases.

Base URL: `http://127.0.0.1:8000`

---

## Phase 1 Operational Endpoints

### 1. Health Check

Returns the operational status and version of the backend service.

- **Endpoint:** `GET /api/health`
- **Headers:** `Accept: application/json`
- **Request Body:** None
- **Response Code:** `200 OK`
- **Response Model:** `HealthResponse`

**Example Response:**
```json
{
  "status": "healthy",
  "service": "sentranet-backend",
  "version": "0.1.0"
}
```

---

### 2. System Status

Returns the real-time operational state of all core infrastructure components.

- **Endpoint:** `GET /api/system/status`
- **Headers:** `Accept: application/json`
- **Request Body:** None
- **Response Code:** `200 OK`
- **Response Model:** `SystemStatus`

**Component States:**
- `online`: Service is running and reachable.
- `not_configured`: Service configuration is pending implementation (e.g. Database).
- `not_loaded`: ML model artifacts are not yet loaded.
- `not_initialized`: Background engine is uninitialized (e.g. Replay Engine, WebSocket).

**Example Response:**
```json
{
  "backend": {
    "status": "online"
  },
  "database": {
    "status": "not_configured"
  },
  "ml_models": {
    "status": "not_loaded"
  },
  "replay_engine": {
    "status": "not_initialized"
  },
  "websocket": {
    "status": "not_initialized"
  }
}
```

---

## Planned API (Future Phases)

*The following endpoints represent the target architecture and are not yet implemented in Phase 1.*

| Endpoint | Method | Phase | Purpose |
|---|---|---|---|
| `/api/predict` | `POST` | Phase 3 | Submit traffic feature vectors for batch classification & forecasting |
| `/api/replay/start` | `POST` | Phase 2 | Begin PCAP/flow streaming replay |
| `/api/replay/pause` | `POST` | Phase 2 | Pause current replay stream |
| `/api/traffic/stats` | `GET` | Phase 2 | Aggregated network traffic flow metrics |
| `/api/alerts` | `GET` | Phase 4 | High-risk early warning security alert feed |
| `/api/models/info` | `GET` | Phase 3 | Active ML model metadata and accuracy metrics |
| `/api/ws/realtime` | `WebSocket` | Phase 2+ | Real-time streaming of `DecisionObject` frames |
