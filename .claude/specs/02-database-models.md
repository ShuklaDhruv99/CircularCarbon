# Spec: Database Models

## Overview

This step introduces the core SQLAlchemy data model for CircularCarbon AI: `factories`, `processes`, `energy_consumption`, `materials`, `waste`, `emission_results`, and `recommendations`, exactly as outlined in the PRD's database design section. It establishes the persistent schema that every later step (data input APIs, deterministic CO₂e calculation, hotspot detection, recommendation engine, what-if simulation) will read and write. This step is schema-only: no calculation logic, no API routes beyond what's needed to prove the models work, and no seed/demo data.

## Depends on

- Step 01 — Project Foundation (FastAPI app, SQLAlchemy engine/session, Alembic migration environment)

## API Endpoints / Routes

No new routes.

## Database changes

New tables (SQLAlchemy models + one Alembic migration):

- **`factories`**
  - `id` (PK)
  - `name` (str, required)
  - `industry` (str, required) — constrained to the MVP-supported industries (Metal Manufacturing, Textile Manufacturing, Food Processing) via an enum/check, per PRD §23 scope limitation
  - `location` (str, optional)
  - `production_volume` (numeric, optional)
  - `production_unit` (str, optional) — e.g. "units/month"
  - `assessment_period` (str, optional) — e.g. "Monthly"
  - `created_at` (timestamp, server default now)

- **`processes`**
  - `id` (PK)
  - `factory_id` (FK → factories.id, required)
  - `name` (str, required) — e.g. "Cutting", "Furnace"
  - `process_type` (str, optional)
  - `production_volume` (numeric, optional)
  - `created_at` (timestamp, server default now)

- **`energy_consumption`**
  - `id` (PK)
  - `process_id` (FK → processes.id, required)
  - `energy_type` (str, required) — electricity / natural_gas / diesel / coal / other / renewable_electricity
  - `quantity` (numeric, required)
  - `unit` (str, required) — e.g. kWh, L, kg
  - `period` (str, required) — assessment period this reading belongs to
  - `created_at` (timestamp, server default now)

- **`materials`**
  - `id` (PK)
  - `process_id` (FK → processes.id, required)
  - `material_name` (str, required)
  - `quantity` (numeric, required)
  - `unit` (str, required)
  - `recycled_percentage` (numeric, 0-100, default 0)
  - `source` (str, optional) — virgin / recycled / supplier note
  - `created_at` (timestamp, server default now)

- **`waste`**
  - `id` (PK)
  - `process_id` (FK → processes.id, required)
  - `waste_type` (str, required)
  - `quantity` (numeric, required)
  - `unit` (str, required)
  - `disposal_method` (str, required) — reused / recycled / sold / landfilled / other
  - `recycled_quantity` (numeric, default 0)
  - `landfilled_quantity` (numeric, default 0)
  - `reused_quantity` (numeric, default 0)
  - `created_at` (timestamp, server default now)

- **`emission_results`**
  - `id` (PK)
  - `process_id` (FK → processes.id, required)
  - `category` (str, required) — energy / materials / waste / transport
  - `activity` (str, required) — the specific activity calculated (e.g. "electricity", "diesel")
  - `emission_factor` (numeric, required) — the factor value used
  - `emission_factor_source` (str, optional) — traceability per PRD Risk 1 (source/unit/version/date)
  - `co2e` (numeric, required) — computed CO₂e result
  - `period` (str, required)
  - `created_at` (timestamp, server default now)

- **`recommendations`**
  - `id` (PK)
  - `hotspot_id` (FK → emission_results.id, required) — links the recommendation to the emission result it addresses
  - `title` (str, required)
  - `description` (text, required)
  - `strategy` (str, required) — reduce / reuse / recycle / substitute / recover / process_optimization
  - `estimated_cost` (str, required) — low / medium / high
  - `co2_reduction` (numeric, required) — estimated percentage or absolute tCO₂e
  - `payback_period` (numeric, optional) — months
  - `score` (numeric, optional) — computed ranking score (added in the recommendation-engine step)
  - `created_at` (timestamp, server default now)

All tables use `id` as an auto-incrementing integer primary key. Foreign keys cascade on delete (deleting a factory removes its processes and their child records) so demo data resets stay simple during the hackathon.

One Alembic migration (`alembic revision --autogenerate`) creates all seven tables on top of the Step 01 baseline.

## Component & UI changes

None. This step is backend-only.

## Files to change

- `backend/app/models/__init__.py` — currently empty; will import and expose all model classes and the shared declarative `Base`
- `backend/app/core/database.py` — add the declarative `Base` (deferred from Step 01, now needed for the first models)
- `backend/alembic/env.py` — set `target_metadata` to the models' `Base.metadata` so `--autogenerate` works

## Files to create

- `backend/app/models/factory.py`
- `backend/app/models/process.py`
- `backend/app/models/energy_consumption.py`
- `backend/app/models/material.py`
- `backend/app/models/waste.py`
- `backend/app/models/emission_result.py`
- `backend/app/models/recommendation.py`
- `backend/alembic/versions/<rev>_create_core_tables.py` — the migration
- `backend/tests/test_models.py` — verifies tables can be created and basic relationships (factory → process → child records) work against a test database/session

## New dependencies

No new dependencies.

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

- [ ] All seven models are defined with correct types, FKs, and cascade behavior
- [ ] `alembic revision --autogenerate -m "create core tables"` produces a migration with no missed changes (verified by running `--autogenerate` again afterward and confirming an empty diff)
- [ ] `alembic upgrade head` runs cleanly against a local PostgreSQL instance and creates all seven tables
- [ ] `alembic downgrade -1` cleanly reverts the migration
- [ ] `backend/tests/test_models.py` passes via `pytest`, covering: creating a factory, a process under it, and one child record per table (energy/materials/waste/emission_results/recommendations), plus cascade-delete behavior
- [ ] No calculation logic, hotspot detection, or recommendation-generation logic exists yet — confirmed by code review
