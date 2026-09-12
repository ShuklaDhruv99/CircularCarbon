# Spec: Project Foundation

## Overview

This is the first implementation step for CircularCarbon AI. It establishes the base repository structure, tooling, and configuration for both the backend (FastAPI + SQLAlchemy + Alembic) and frontend (React + TypeScript + Vite + Tailwind CSS) so that subsequent feature steps (data ingestion, CO₂e calculation, recommendations, Gemini explanation, what-if simulation) have a working skeleton to build on. No business logic, models, or UI features are implemented in this step — only scaffolding, configuration, and a health-check to prove the stack boots end to end.

## Depends on

None. This is the first feature step.

## API Endpoints / Routes

- `GET /health` — returns service status (e.g. `{"status": "ok"}`) — no auth required, used to verify the backend is running

## Database changes

- Initialize Alembic migration environment (`alembic init`) with a baseline (empty) migration to establish version control for schema changes.
- No application tables are created in this step.

## Component & UI changes

- **Create:**
  - `frontend/src/pages/HomePage.tsx` — minimal placeholder page confirming the app renders and can reach the backend `/health` endpoint
  - `frontend/src/services/api.ts` — base API client (fetch/axios wrapper) configured with the backend base URL
  - `frontend/src/types/index.ts` — placeholder shared types file
- **Modify:** None (no existing components yet)

## Files to change

None — this is a greenfield step; there are no existing implementation files to modify.

## Files to create

Backend:
- `backend/app/main.py` — FastAPI app entrypoint, registers routers, CORS config (dev origin: `http://localhost:5173`, the Vite default)
- `backend/app/core/config.py` — settings (env vars, database URL, Gemini API key placeholder) via Pydantic settings
- `backend/app/core/database.py` — SQLAlchemy engine/session setup
- `backend/app/api/health.py` — health-check route
- `backend/app/models/__init__.py`
- `backend/app/schemas/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/ai/__init__.py`
- `backend/app/data/__init__.py`
- `backend/app/utils/__init__.py`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/` (baseline migration)
- `backend/tests/test_health.py` — test asserting `GET /health` returns 200
- `backend/requirements.txt` (or `pyproject.toml`) — fastapi, uvicorn, sqlalchemy, alembic, pydantic-settings, psycopg2-binary, pytest, httpx
- `backend/.env.example` — includes a `DATABASE_URL` default pointing at a local PostgreSQL instance (e.g. `postgresql://postgres:postgres@localhost:5432/circularcarbon`)
- `.gitignore` — excludes `node_modules/`, `__pycache__/`, `.venv/`, `.env`, and other build artifacts

Frontend:
- `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`
- `frontend/tailwind.config.js`, `frontend/postcss.config.js`
- `frontend/src/main.tsx`, `frontend/src/App.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/types/index.ts`
- `frontend/.env.example`

Docs:
- `docs/architecture.md` — brief note on the scaffolded structure

## New dependencies

Backend: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic-settings`, `psycopg2-binary` (sync SQLAlchemy engine — no async driver in this step), `pytest`, `httpx`

Frontend: `react`, `react-dom`, `typescript`, `vite`, `tailwindcss`, `postcss`, `autoprefixer` (added now since it's listed as a core dependency in CLAUDE.md, even though unused until the what-if simulation step)

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only
- Gemini must never calculate or invent numerical emission values
- Gemini is used only for explanation/contextualization
- Strict input validation and type safety
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality

## Definition of done

- [ ] `backend/app/main.py` starts successfully with `uvicorn app.main:app`
- [ ] `GET /health` returns `200 OK` with a JSON status payload
- [ ] `backend/tests/test_health.py` passes via `pytest`
- [ ] Alembic is initialized and `alembic upgrade head` runs cleanly against a local PostgreSQL instance (developer is expected to have Postgres running locally; connection string is set via `DATABASE_URL` per `.env.example`)
- [ ] `frontend` builds successfully via `npm run build`
- [ ] `frontend` dev server (`npm run dev`) HomePage calls GET /health through services/api.ts and displays either the backend status or a clear error message.
- [ ] Tailwind CSS classes render correctly on the placeholder page
- [ ] No business logic, emission calculations, or Gemini integration exists yet — confirmed by code review
