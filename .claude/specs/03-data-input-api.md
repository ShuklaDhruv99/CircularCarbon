# Spec: Data Input API

## Overview

This step exposes the Step 02 database models through a REST API so a user (or the frontend) can create a factory, define its processes, and record the raw activity data — energy consumption, materials, and waste — that the deterministic CO₂e calculation (Step 04) will later consume. It is pure CRUD plus validation: no emission-factor lookups, no CO₂e math, and no recommendation logic happen here. This matches the PRD's Phase 1 deliverable: "User can create a factory and enter data," and mirrors the flat `/api/factories`, `/api/processes`, `/api/energy` route shape from PRD §22.

All fields beyond the required minimum (factory name/industry, process name, one activity entry) stay optional at the schema level, per PRD Risk 3 ("Too much user input") and the UI/UX plan's progressive four-step onboarding (Factory → Production Process → Energy & Materials → Waste) — the API must not force a single all-fields-required payload. The `waste.disposal_method` enum (reused / recycled / sold / landfilled / other) is intentionally worded to match the UI/UX doc's plain-language options ("What happens to your production waste?").

## Depends on

- Step 01 — Project Foundation (FastAPI app, DB session, CORS)
- Step 02 — Database Models (`Factory`, `Process`, `EnergyConsumption`, `Material`, `Waste` SQLAlchemy models)

## API Endpoints / Routes

Routes follow the flat structure defined in the PRD's API Design section (§22: `POST /api/factories`, `POST /api/processes`, `POST /api/energy`, …) — the parent id travels in the request body on create and as a query filter on list, rather than being nested into the URL path. No auth system exists yet in this MVP; all routes are open. `emission_results` and `recommendations` are read-only outputs of later steps and get no write routes here.

Factories:

- `POST /api/factories` — create a factory — public
- `GET /api/factories` — list all factories — public
- `GET /api/factories/{factory_id}` — get one factory, including its processes — public
- `PATCH /api/factories/{factory_id}` — update factory fields — public
- `DELETE /api/factories/{factory_id}` — delete a factory (cascades to processes and child records) — public

Processes:

- `POST /api/processes` — create a process (`factory_id` in body) — public
- `GET /api/processes?factory_id=` — list processes, optionally filtered by factory — public
- `GET /api/processes/{process_id}` — get one process, including its energy/materials/waste entries — public
- `PATCH /api/processes/{process_id}` — update process fields — public
- `DELETE /api/processes/{process_id}` — delete a process (cascades to child records) — public

Energy consumption:

- `POST /api/energy` — add an energy consumption entry (`process_id` in body) — public
- `GET /api/energy?process_id=` — list energy entries, optionally filtered by process — public
- `DELETE /api/energy/{energy_id}` — delete an energy entry — public

Materials:

- `POST /api/materials` — add a material entry (`process_id` in body) — public
- `GET /api/materials?process_id=` — list material entries, optionally filtered by process — public
- `DELETE /api/materials/{material_id}` — delete a material entry — public

Waste:

- `POST /api/waste` — add a waste entry (`process_id` in body) — public
- `GET /api/waste?process_id=` — list waste entries, optionally filtered by process — public
- `DELETE /api/waste/{waste_id}` — delete a waste entry — public

Every create/list route validates that a referenced `factory_id`/`process_id` exists, returning 404 if not — this replaces the path-nesting validation the earlier draft relied on.

## Database changes

No database changes. This step only reads/writes existing Step 02 tables.

## Component & UI changes

None. This step is backend-only (API layer). Frontend data-entry forms consume this API in a later step.

## Files to change

- `backend/app/main.py` — register the new routers (`factories`, `processes`, `energy`, `materials`, `waste`)
- `backend/app/schemas/__init__.py` — export the new Pydantic schemas

## Files to create

- `backend/app/schemas/factory.py` — `FactoryCreate`, `FactoryUpdate`, `FactoryRead` (with nested `processes` on read), enforcing `industry` is one of the MVP-supported industries (Metal Manufacturing, Textile Manufacturing, Food Processing)
- `backend/app/schemas/process.py` — `ProcessCreate`, `ProcessUpdate`, `ProcessRead`
- `backend/app/schemas/energy_consumption.py` — `EnergyConsumptionCreate`, `EnergyConsumptionRead`, with `energy_type` constrained to electricity / natural_gas / diesel / coal / other / renewable_electricity and `quantity` validated `> 0`
- `backend/app/schemas/material.py` — `MaterialCreate`, `MaterialRead`, with `quantity > 0` and `recycled_percentage` constrained to 0–100
- `backend/app/schemas/waste.py` — `WasteCreate`, `WasteRead`, with `disposal_method` constrained to reused / recycled / sold / landfilled / other and `quantity > 0`
- `backend/app/services/factory_service.py` — CRUD functions for factories (create/list/get/update/delete), raising a 404-mappable "not found" error when missing
- `backend/app/services/process_service.py` — CRUD functions for processes, validating the parent factory exists
- `backend/app/services/energy_service.py` — create/list/delete for energy consumption entries, validating the parent process exists
- `backend/app/services/material_service.py` — create/list/delete for material entries, validating the parent process exists
- `backend/app/services/waste_service.py` — create/list/delete for waste entries, validating the parent process exists
- `backend/app/api/factories.py` — factory CRUD routes
- `backend/app/api/processes.py` — process CRUD routes (`factory_id` in body on create, optional `factory_id` query filter on list)
- `backend/app/api/energy.py`, `backend/app/api/materials.py`, `backend/app/api/waste.py` — create/list (`process_id` in body/query)/delete routes for each activity-data resource
- `backend/tests/test_factories_api.py` — API tests for factory CRUD (create, list, get, update, delete, 404 on missing id, validation error on bad industry)
- `backend/tests/test_processes_api.py` — API tests for process CRUD, the `factory_id` query filter, and 404 when the referenced factory doesn't exist
- `backend/tests/test_activity_data_api.py` — API tests for energy/materials/waste create+list+delete, including validation errors (negative quantity, invalid enum value, out-of-range percentage) and 404 when the referenced process doesn't exist

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

- [ ] All factory CRUD routes work end-to-end against a local PostgreSQL instance (create → list → get → update → delete)
- [ ] All process CRUD routes work end-to-end, `factory_id` is accepted in the create body and as an optional list filter, and 404 is returned when the referenced factory does not exist
- [ ] Energy, material, and waste entries can be created (with `process_id` in the body), listed (optionally filtered by `process_id`), and deleted, and return 404 when the referenced process does not exist
- [ ] Pydantic schemas reject invalid input: unsupported `industry`, unsupported `energy_type`/`disposal_method`, non-positive `quantity`, and `recycled_percentage` outside 0–100
- [ ] Deleting a factory cascades and removes its processes and all child energy/material/waste/emission_result rows (verified by a test)
- [ ] `backend/tests/test_factories_api.py`, `test_processes_api.py`, and `test_activity_data_api.py` all pass via `pytest`
- [ ] No emission-factor lookup, CO₂e calculation, or recommendation logic exists yet — confirmed by code review
