# CLAUDE.md

## Project overview

CircularCarbon AI is an SME manufacturing carbon decision-support platform.

Core flow:

Factory Process Data
→ Deterministic CO₂e Calculation
→ Emission Hotspots
→ Ranked Circular Recommendations
→ Gemini Explanation
→ What-If Simulation
→ Prioritized Action Plan

The project is being built as a 24-hour hackathon MVP.

The priority is a functional, traceable and demonstrable product, not production-scale complexity.

---

## Architecture

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
│   │   └── utils/             # Shared utilities
│   ├── alembic/              # Database migrations
│   └── tests/                # Backend tests
│
├── frontend/
│   └── src/
│       ├── pages/            # Application pages
│       ├── components/       # Reusable UI components
│       ├── services/         # API communication
│       ├── types/            # TypeScript types
│       └── assets/
│
└── docs/                     # Architecture, API and demo documentation