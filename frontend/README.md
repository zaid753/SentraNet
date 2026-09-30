# SENTRANET Frontend

React + TypeScript + Vite SOC Dashboard for the SENTRANET predictive cybersecurity platform (Smart India Hackathon 2026, Problem Statement: SIH26153).

## Purpose

Provides the SOC analyst user interface for monitoring infrastructure health, network attack forecasts, risk escalation, and temporal early warnings. In Phase 1, the frontend delivers the foundation status matrix, verified connectivity with the FastAPI backend, resilient offline state handling, and cybersecurity visual language.

## Architecture

```
frontend/
├── src/
│   ├── components/   # Modular UI elements (Header, StatusIndicator, SystemStatusCard)
│   ├── pages/        # View screens (FoundationPage)
│   ├── hooks/        # Custom React hooks
│   ├── services/     # Centralized API clients (api.ts)
│   ├── types/        # TypeScript interfaces and contracts (DecisionObject, HealthResponse, etc.)
│   ├── utils/        # Formatting and helper utilities
│   ├── assets/       # Static branding and media assets
│   ├── App.tsx       # Root view router / mounting point
│   ├── main.tsx      # React entrypoint
│   └── index.css     # Tailwind CSS & cybersecurity visual styling tokens
├── index.html        # HTML shell with typography and metadata
├── vite.config.ts    # Vite bundler configuration
└── tsconfig.json     # Strict TypeScript configuration
```

## Setup

Ensure Node.js (v18+) is installed.

```bash
cd frontend
npm install
```

## Running the Frontend

Start the Vite development server:
```bash
npm run dev
```

Frontend application will be accessible at:
`http://localhost:5173`

## Production Build

To build and validate TypeScript types and generate production bundles:
```bash
npm run build
```

Preview the built application:
```bash
npm run preview
```

## Environment Variables

Configured via `.env` or defaults:

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Target URL for the SENTRANET FastAPI backend |

## Backend Dependency

The frontend queries `GET /api/health` and `GET /api/system/status` on startup. If the backend is offline, the frontend handles it gracefully without crashing, displaying an informative "Backend unavailable" status with reconnection actions.
