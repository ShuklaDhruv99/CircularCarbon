# Spec: Carbon Calculation Engine

## Overview

This is Phase 2 of the CircularCarbon AI roadmap ("Carbon Engine", PRD §30). With factory/process/energy/material/waste data already capturable (Steps 02-04), the platform now needs to turn that raw activity data into deterministic CO₂e numbers. This feature adds a versioned emission-factor dataset, a deterministic calculation pipeline (activity → emission factor → CO₂e → process total → factory total → percentage contribution), a hotspot-detection step that ranks categories/processes by contribution, and a backend API to trigger calculation and read results. On the frontend, it adds a results/dashboard page that visualizes the emissions breakdown and hotspots for a factory. All numeric calculation happens exclusively in the backend using `Decimal` arithmetic — the frontend only renders numbers the backend already computed.

## Depends on

- Step 02 — Database Models (`Factory`, `Process`, `EnergyConsumption`, `Material`, `Waste`, `EmissionResult`, `Recommendation` tables already exist and are migrated)
- Step 03 — Data Input API (factories/processes/energy/materials/waste are readable via existing service functions)
- Step 04 — Factory Onboarding & Data Entry UI (factories have process data entered before calculation can run)

## API Endpoints / Routes

- `POST /api/emissions/calculate/{factory_id}` — runs the deterministic calculation pipeline for every process under the given factory, deletes and replaces that factory's existing `emission_results` rows, and returns the full emissions breakdown — no auth (matches existing routes). The delete-old-rows + insert-new-rows + aggregate happens inside a single DB transaction (one commit) for atomicity.
- `GET /api/emissions/factory/{factory_id}` — returns the persisted emissions breakdown (per-process, per-category CO₂e, factory total, percentage contribution) for a factory; 404 if the factory itself does not exist, or if the factory has zero processes, or if the factory has processes but zero `EmissionResult` rows exist yet (not yet calculated). A factory that has been calculated and legitimately has 0 total CO₂e (e.g. 100% renewable, no waste) returns 200 with all totals at 0, not 404 — no auth
- `GET /api/emissions/hotspots/{factory_id}` — returns emission results ordered by CO₂e descending with an `is_hotspot` flag; a row is a hotspot if its cumulative percentage contribution (running sum of CO₂e-descending rows, factory-wide) is `<= 80%`, i.e. the smallest set of top contributors whose combined share reaches 80% of the factory total (the first row that pushes the cumulative sum past 80% is still included). If the factory total CO₂e is 0, no rows are flagged as hotspots. Same 404 rules as above — no auth

## Database changes

No database changes. `EmissionResult` (`backend/app/models/emission_result.py`) already has the required columns (`process_id`, `category`, `activity`, `emission_factor`, `emission_factor_source`, `co2e`, `period`). Step 05 only writes rows into the existing table; no migration is needed.

## Component & UI changes

- **Create:**
  - `frontend/src/pages/EmissionsDashboard.tsx` — factory emissions results page: total CO₂e, per-category breakdown (chart + table), per-process breakdown, hotspot list with a "Recalculate" action
  - `frontend/src/components/emissions/CategoryBreakdownChart.tsx` — bar/pie chart of CO₂e by category (energy/materials/waste), using Recharts
  - `frontend/src/components/emissions/ProcessBreakdownTable.tsx` — table of CO₂e per process with percentage-contribution column
  - `frontend/src/components/emissions/HotspotList.tsx` — ranked list of top-contributing categories/processes flagged as hotspots
  - `frontend/src/services/emissions.ts` — API client functions: `calculateEmissions(factoryId)`, `getFactoryEmissions(factoryId)`, `getHotspots(factoryId)`
- **Modify:**
  - `frontend/src/types/domain.ts` — add `EmissionResult`, `EmissionsBreakdown`, `HotspotResult` types mirroring the new backend schemas
  - `frontend/src/pages/OnboardingComplete.tsx` — add a link/button to navigate to `EmissionsDashboard` for the newly created factory
  - App router file (wherever routes are registered, e.g. `frontend/src/App.tsx`) — add a route for `/factories/:factoryId/emissions`

## Files to change

- `backend/app/main.py` — register the new `emissions` router
- `frontend/src/types/domain.ts` — add emissions-related types
- `frontend/src/pages/OnboardingComplete.tsx` — add navigation link to the emissions dashboard
- App routing file — add the new dashboard route

## Files to create

- `backend/app/data/emission_factors.py` — deterministic, versioned emission-factor lookup keyed by energy type / material / waste disposal method; each entry carries `factor`, `unit`, `source`, `version`/`effective_date` (per PRD Risk 1 traceability requirement)
- `backend/app/schemas/emission_result.py` — Pydantic read schemas: `EmissionResultRead`, `CategoryBreakdown`, `EmissionsBreakdownRead` (factory total, per-category totals, per-process totals, percentage contributions), `HotspotRead`
- `backend/app/services/emission_calculation_service.py` — deterministic pipeline: for each process under a factory, look up factors for its energy/material/waste rows, compute CO₂e (`Decimal`), persist `EmissionResult` rows, aggregate process/category/factory totals and percentage contributions
- `backend/app/services/hotspot_service.py` — ranks `EmissionResult` rows by CO₂e, computes cumulative percentage contribution, flags top contributors as hotspots (threshold-based, e.g. cumulative ≥ 80% or top N)
- `backend/app/api/emissions.py` — router exposing the three endpoints above, delegating to the two services
- `backend/tests/test_emission_calculation_service.py` — unit tests for the calculation pipeline (known inputs → expected CO₂e/totals)
- `backend/tests/test_hotspot_service.py` — unit tests for hotspot ranking/threshold logic
- `backend/tests/test_emissions_api.py` — API tests for the three new routes
- `frontend/src/pages/EmissionsDashboard.tsx`
- `frontend/src/components/emissions/CategoryBreakdownChart.tsx`
- `frontend/src/components/emissions/ProcessBreakdownTable.tsx`
- `frontend/src/components/emissions/HotspotList.tsx`
- `frontend/src/services/emissions.ts`
- `frontend/src/pages/EmissionsDashboard.test.tsx` — component tests for rendering breakdown/hotspot data, colocated next to `EmissionsDashboard.tsx` (matching Step 04's convention of colocating tests with the component they cover)

## New dependencies

- `recharts` (frontend) — for category breakdown chart, if not already installed; check `frontend/package.json` first and only add if missing
No other new dependencies. Calculation uses Python's built-in `decimal.Decimal`; no pandas/numpy needed for this deterministic, per-row arithmetic.

## Calculation determinism rules

These pin down the exact arithmetic so the pipeline is reproducible and testable (same inputs always produce the same `co2e`):

- **`EmissionResult.period` value for non-energy rows:** `EnergyConsumption` rows use their own `period` field. `Material` and `Waste` have no `period` column, so their derived `EmissionResult.period` is set to the parent `Factory.assessment_period`; if that is `null`, use the literal string `"unspecified"`.
- **Material CO₂e formula (recycled-content blending):** every material uses one generic pair of factors — `material_virgin_factor` and `material_recycled_factor` (kg CO₂e per unit) — from `emission_factors.py`, independent of the free-text `material_name`. The effective factor is:
  `effective_factor = virgin_factor * (1 - recycled_percentage / 100) + recycled_factor * (recycled_percentage / 100)`
  then `co2e = quantity * effective_factor`. (A per-`material_name` factor table is out of scope for this hackathon MVP; document this as a known simplification.)
- **Waste CO₂e formula:** use only `Waste.quantity` and `Waste.disposal_method` to look up a single disposal-method factor from `emission_factors.py` (e.g. `landfill`, `recycled`, `reused`, `incinerated` — matching whatever `disposal_method` values Step 04's form actually submits). `co2e = quantity * disposal_method_factor`. The `recycled_quantity` / `landfilled_quantity` / `reused_quantity` breakdown columns are **not** used in this step's calculation (they exist for future, more granular reporting) — this is an explicit scope decision, not an oversight.
- **Unit-matching assumption:** `emission_factors.py` factors are defined per a single canonical unit per activity type (e.g. kWh for grid electricity, litres for diesel, kg for materials/waste). The calculation assumes the user-entered `unit` on `EnergyConsumption`/`Material`/`Waste` already matches the factor's canonical unit — no unit conversion is performed in this step. This is a documented hackathon-scope limitation, not silent behavior.
- **Percentage-contribution rounding:** compute each row's/category's/process's percentage contribution as `Decimal`, round to 2 decimal places using `ROUND_HALF_UP`, and adjust the single largest-contribution row's rounded percentage by the residual (`100.00 - sum of the other rounded percentages`) so the set always sums to exactly `100.00` (skip this adjustment, returning all-zero percentages, when the factory total CO₂e is 0).

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only — same input data always produces the same `co2e` values; no randomness, no LLM involvement in this step
- Gemini must never calculate or invent numerical emission values (Gemini is out of scope for this step entirely)
- Gemini is used only for explanation/contextualization (not applicable to this step)
- All emission-factor values must carry a `source` and version/effective-date for traceability (PRD Risk 1)
- Strict input validation and type safety — reuse the existing `NotFoundError` pattern for missing factories/processes
- Use `Decimal` throughout the calculation pipeline (never `float`) to match the existing `Numeric` column convention
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality (Steps 01-04 files stay untouched except the explicit router/type/nav additions listed above)
- `transport` category is out of scope for this step (no transport input model exists yet) — only `energy`, `materials`, and `waste` categories are calculated

## Definition of done

- [ ] `emission_factors.py` contains factor entries for every `energy_type` used by the existing input form, the generic `material_virgin_factor`/`material_recycled_factor` pair, and every `waste` `disposal_method` used by the existing input form, each with `source` and version/date
- [ ] `POST /api/emissions/calculate/{factory_id}` recalculates and persists `EmissionResult` rows for all processes in a factory, replacing prior results, and returns the aggregated breakdown
- [ ] `GET /api/emissions/factory/{factory_id}` returns factory total CO₂e, per-category totals, per-process totals, and percentage contributions that sum to 100%
- [ ] `GET /api/emissions/hotspots/{factory_id}` returns results ordered by CO₂e descending with correct `is_hotspot` flags
- [ ] Unit tests verify the pipeline against hand-computed expected CO₂e for at least one energy, one material, and one waste input
- [ ] API tests verify 404 behavior for a factory with no processes/data, and 200 with correct payload shape otherwise
- [ ] `EmissionsDashboard` page renders category breakdown chart, process table, and hotspot list from live API data given a factory with entered process data
- [ ] "Recalculate" action on the dashboard calls the calculate endpoint and refreshes displayed data
- [ ] `npm run build` (frontend) and `pytest` (backend) both pass with no regressions to existing Step 01-04 functionality
