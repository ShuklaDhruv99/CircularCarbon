# Spec: What-If Simulation

## Overview

This is Phase 4 of the CircularCarbon AI roadmap ("What-If Simulation", PRD §14 FR-07, §23 "MVP killer feature"). With ranked, persisted `Recommendation` rows already available per factory (Step 06) and their Gemini narration layered on top (Step 07), this step lets the user select any subset of a factory's recommendations and see the deterministic combined impact of applying them: baseline vs. projected total CO2e, absolute and percentage reduction, total implementation cost, and an estimated payback period. This turns the dashboard from a static report into an interactive decision tool (PRD §14: "transforms the product from a calculator into a decision-making tool") without introducing any new emission math — every number is derived by summing/aggregating the already-verified `co2_reduction`, `estimated_cost`, and `payback_period` fields already computed and persisted by Step 06's deterministic scoring pipeline. No Gemini/LLM involvement in this step.

## Depends on

- Step 02 — Database Models (`Recommendation`, `EmissionResult` tables)
- Step 05 — Carbon Calculation Engine & Hotspot Detection (`EmissionsBreakdown.factory_total_co2e` / `emission_calculation_service` — baseline total CO2e input)
- Step 06 — Circular Recommendations Engine (`Recommendation` rows: `co2_reduction`, `estimated_cost`, `payback_period` — the direct input to this step; `recommendation_service.get_for_factory`)

## API Endpoints / Routes

- `POST /api/simulations/factory/{factory_id}` — body `{"recommendation_ids": list[int]}`; runs the deterministic what-if aggregation over the given factory's currently-persisted recommendations restricted to the requested ids (order-independent, duplicates ignored), and returns a `SimulationResult`. Raises `NotFoundError` (404) if the factory doesn't exist or has no emissions calculated yet (reuses `emission_calculation_service`'s existing precondition, same as `GET /api/emissions/factory/{factory_id}`). Raises a `ValidationError` (422) if any `recommendation_id` does not belong to a currently-persisted recommendation of that factory. An empty `recommendation_ids` list is valid and returns a zero-impact `SimulationResult` (`projected_co2e == baseline_co2e`) — no auth

## Database changes

No database changes. Simulation results are computed on demand from existing `EmissionResult`/`Recommendation` rows and are not persisted (matching the Step 07 "not persisted, regenerated on each call" convention) — a what-if run is inherently transient/exploratory, not a saved assessment.

## Component & UI changes

- **Create:**
  - `frontend/src/components/simulation/SimulationPanel.tsx` — "Run What-If Simulation" button plus results display: before/after total CO2e, absolute + percentage reduction, total implementation cost, estimated payback, and the list of applied recommendation titles
  - `frontend/src/services/simulation.ts` — API client function: `simulateFactory(factoryId, recommendationIds)`
- **Modify:**
  - `frontend/src/types/domain.ts` — add `SimulationResult` type mirroring the new backend read schema
  - `frontend/src/components/recommendations/RecommendationList.tsx` — accept optional `selectedIds: Set<number>` and `onToggle: (id: number) => void` props; when both are provided, render a checkbox on each `RecommendationCard` (via a new optional `onToggleSelect`/`selected` prop on `RecommendationCard`) — omitting both props preserves the existing read-only rendering used elsewhere/in existing tests
  - `frontend/src/components/recommendations/RecommendationCard.tsx` — accept optional `selected?: boolean` and `onToggleSelect?: () => void` props; renders a checkbox only when `onToggleSelect` is provided, otherwise renders exactly as today
  - `frontend/src/pages/EmissionsDashboard.tsx` — track `selectedRecommendationIds: Set<number>` state, pass selection props to `RecommendationList`, and render `SimulationPanel` below the recommendations section with the current selection and factory id

## Files to change

- `backend/app/main.py` — register the new `simulations` router after the `recommendations` router
- `frontend/src/types/domain.ts` — add `SimulationResult` type
- `frontend/src/components/recommendations/RecommendationList.tsx` — optional selection props (see above)
- `frontend/src/components/recommendations/RecommendationCard.tsx` — optional selection checkbox (see above)
- `frontend/src/pages/EmissionsDashboard.tsx` — add selection state and `SimulationPanel` section

## Files to create

- `backend/app/data/cost_estimates.py` — fixed, documented `CostTier -> Decimal` currency lookup used only for simulation cost aggregation (`low`, `medium`, `high`), e.g. `{"low": Decimal("50000"), "medium": Decimal("200000"), "high": Decimal("500000")}` in the same currency unit as the rest of the hackathon demo data; explicitly documented as a fixed placeholder scale, not a real cost estimate, since no per-unit energy/material currency cost exists elsewhere in the schema
- `backend/app/schemas/simulation.py` — Pydantic schemas: `SimulationRequest` (`recommendation_ids: list[int]`), `SimulationResult` (`factory_id: int`, `baseline_co2e: Decimal`, `projected_co2e: Decimal`, `co2_reduction: Decimal`, `reduction_percentage: Decimal`, `total_implementation_cost: Decimal`, `estimated_payback_months: Decimal | None`, `applied_recommendations: list[RecommendationRead]`)
- `backend/app/services/simulation_service.py` — orchestration: fetch `baseline_co2e` via `emission_calculation_service` (factory total), fetch the factory's persisted recommendations via `recommendation_service.get_for_factory`, validate every requested id is present among them (else raise a `ValidationError`), sum `co2_reduction` of the matched subset (capped so `projected_co2e` never goes below 0), sum `total_implementation_cost` via `cost_estimates.py`, compute `estimated_payback_months` as a cost-weighted average of the selected recommendations' `payback_period` (weight = each recommendation's `cost_estimates` value; `None` when the selection is empty or every selected recommendation has a null `payback_period`), compute `reduction_percentage` as `co2_reduction / baseline_co2e * 100` (0 when `baseline_co2e` is 0), all in `Decimal` rounded to 2 places
- `backend/app/api/simulations.py` — router exposing the endpoint above, delegating to `simulation_service`
- `backend/tests/test_simulation_service.py` — unit tests: (a) empty selection returns zero-impact result, (b) known subset of recommendations produces hand-computed `projected_co2e`/`co2_reduction`/`reduction_percentage`/`total_implementation_cost`/`estimated_payback_months`, (c) `co2_reduction` sum exceeding `baseline_co2e` is clamped so `projected_co2e` floors at 0, (d) unknown `recommendation_id` raises the validation error
- `backend/tests/test_simulations_api.py` — API tests: 404 when factory has no emissions calculated, 422 for an unknown recommendation id, 200 with correct payload shape for a valid subset, 200 zero-impact for an empty list
- `frontend/src/components/simulation/SimulationPanel.tsx`
- `frontend/src/services/simulation.ts`
- `frontend/src/components/simulation/SimulationPanel.test.tsx` — component test for rendering before/after/reduction/cost/payback given a mock `SimulationResult`, colocated per Step 04-07 convention

## New dependencies

No new dependencies. Aggregation is a plain deterministic weighted-sum in Python using `decimal.Decimal`, matching Steps 05-06's convention.

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only — same `recommendation_ids` selection for a factory always produces the same `SimulationResult`; no randomness, no LLM involvement in this step
- Gemini must never calculate or invent numerical emission values (Gemini is out of scope for this step entirely)
- Gemini is used only for explanation/contextualization (not applicable to this step)
- Strict input validation and type safety — reuse the existing `NotFoundError` pattern from `backend/app/services/errors.py` for the factory/not-calculated case; add/reuse a validation-error pattern for unknown recommendation ids, returned as 422
- Use `Decimal` throughout the aggregation pipeline (never `float`), matching Steps 05-06's convention
- What-If numerical results must come from the backend — the frontend only sends the selected `recommendation_ids` and renders the returned `SimulationResult` verbatim, it never recomputes totals client-side
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality (Steps 01-07 files stay untouched except the explicit router/type/component additions listed above)

## Definition of done

- [ ] `POST /api/simulations/factory/{factory_id}` with an empty `recommendation_ids` list returns a zero-impact `SimulationResult` (`projected_co2e == baseline_co2e`, `co2_reduction == 0`)
- [ ] `POST /api/simulations/factory/{factory_id}` with a valid subset of recommendation ids returns correct `baseline_co2e`, `projected_co2e`, `co2_reduction`, `reduction_percentage`, `total_implementation_cost`, and `estimated_payback_months`, verified against hand-computed values in a unit test
- [ ] Selecting recommendations whose combined `co2_reduction` exceeds `baseline_co2e` yields `projected_co2e == 0` (never negative), verified by unit test
- [ ] An unknown `recommendation_id` in the request returns 422 with no partial computation
- [ ] 404 when the factory has no emissions calculated yet
- [ ] `SimulationPanel` renders before/after CO2e, reduction (absolute + %), total implementation cost, and estimated payback from a `SimulationResult` prop
- [ ] Checkboxes on `RecommendationList`/`RecommendationCard` toggle a recommendation's selection without breaking existing read-only usage (no props passed = no checkboxes, matching current Step 06/07 tests)
- [ ] "Run What-If Simulation" action on `EmissionsDashboard` calls the simulate endpoint with the current selection and renders the result in `SimulationPanel`
- [ ] `npm run build` (frontend) and `pytest` (backend) both pass with no regressions to existing Step 01-07 functionality
