# Architecture

CircularCarbon AI is an SME manufacturing carbon decision-support platform, built as a 24-hour hackathon MVP.

Core flow:

```
Factory Process Data
→ Deterministic CO₂e Calculation
→ Emission Hotspots
→ Ranked Circular Recommendations
→ Gemini Explanation
→ What-If Simulation
→ Prioritized Action Plan
```

## Layout

```text
circularcarbon-ai/

├── backend/
│   ├── app/
│   │   ├── core/             # Configuration and database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/              # FastAPI routes
│   │   ├── services/         # Core business logic
│   │   ├── ai/               # Gemini + LangChain
│   │   ├── data/             # Factors and demo data
│   │   └── utils/            # Shared utilities
│   ├── alembic/               # Database migrations
│   └── tests/                 # Backend tests
│
├── frontend/
│   └── src/
│       ├── pages/             # Application pages
│       ├── components/        # Reusable UI components
│       ├── services/          # API communication
│       ├── types/             # TypeScript types
│       └── assets/
│
└── docs/                      # Architecture, API and demo documentation
```

## Step 01 — Project Foundation

This step scaffolds the backend and frontend skeletons only — no business logic, no models, no Gemini integration. It establishes:

- A FastAPI backend with a `GET /health` endpoint, Pydantic-based settings, a SQLAlchemy engine/session, and an Alembic migration pipeline (baseline migration only, no tables yet).
- A React + TypeScript + Vite + Tailwind CSS frontend with a placeholder home page that calls the backend health check.

See `.claude/specs/01-project-foundation.md` for the full spec and Definition of Done.
