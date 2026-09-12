# Spec: Prioritized Action Plan

## Overview

This feature is the final stage of the CircularCarbon AI roadmap: turning the ranked circular recommendations (Step 06) into a practical, phased action plan (PRD FR-08). Instead of presenting SMEs with an undifferentiated list of interventions, the backend deterministically buckets each factory's current recommendations into three implementation horizons — **Now** (0–3 months), **Next** (3–12 months), and **Later** (12+ months) — based on fixed, documented thresholds over `estimated_cost` and `payback_period`. Each phase reports its aggregate CO₂e reduction and implementation cost so the dashboard can show "what you get by executing each phase." As with Steps 06–08, all numbers are computed by the deterministic backend; no LLM is involved in bucketing or numeric aggregation.

## Depends on

- Step 05 — Carbon Calculation Engine (emission totals/hotspots must exist)
- Step 06 — Circular Recommendations Engine (`Recommendation` rows, `recommendation_service.get_for_factory`)
- Step 08 — What-If Simulation (`cost_estimates.COST_TIER_ESTIMATES` reused for phase cost aggregation)

## API Endpoints / Routes

- `GET /api/action-plan/factory/{factory_id}` — computes and returns the prioritized action plan (phases with bucketed recommendations + per-phase aggregates) for the given factory, on demand from current recommendations — no auth (matches existing endpoints)

## Database changes

No database changes. The action plan is computed on demand from existing `Recommendation` rows and is not persisted (matches the non-persisted convention established in Steps 07 and 08).

## Component & UI changes

- **Create:** `frontend/src/components/action-plan/ActionPlanPanel.tsx` — renders the three phases (Now/Next/Later) as sections, each listing its recommendations plus phase-level totals (CO₂ reduction, implementation cost)
- **Create:** `frontend/src/components/action-plan/ActionPlanPanel.test.tsx` — colocated component test
- **Modify:** `frontend/src/pages/EmissionsDashboard.tsx` — add a new "Prioritized Action Plan" section after the What-If Simulator section, with its own `useState` + `handleGenerateActionPlan` handler following the existing per-feature pattern
- **Modify:** `frontend/src/types/domain.ts` — add `ActionPlanPhase` and `ActionPlan` types
- **Create:** `frontend/src/services/actionPlan.ts` — thin wrapper calling the new endpoint

## Files to change

- `backend/app/main.py` — register the new action-plan router
- `frontend/src/pages/EmissionsDashboard.tsx` — add Action Plan section
- `frontend/src/types/domain.ts` — add Action Plan types

## Files to create

- `backend/app/data/action_plan_rules.py` — fixed phase-bucketing thresholds (documented constants, no magic numbers inline)
- `backend/app/schemas/action_plan.py` — Pydantic schemas:
  - `ActionPlanPhaseRead`: `phase: Literal["now", "next", "later"]`, `recommendations: list[RecommendationRead]`, `total_co2_reduction: Decimal`, `total_implementation_cost: Decimal`
  - `ActionPlanRead`: `factory_id: int`, `now: ActionPlanPhaseRead`, `next: ActionPlanPhaseRead`, `later: ActionPlanPhaseRead` (matches `SimulationResult`'s inclusion of `factory_id` for consistency)
- `backend/app/services/action_plan_service.py` — bucketing + aggregation logic, reusing `recommendation_service.get_for_factory` and `cost_estimates.COST_TIER_ESTIMATES`
- `backend/app/api/action_plan.py` — `GET /api/action-plan/factory/{factory_id}` route
- `backend/tests/test_action_plan_service.py` — unit tests for bucketing/aggregation logic
- `backend/tests/test_action_plan_api.py` — API-level tests (200/404/empty cases)
- `frontend/src/services/actionPlan.ts`
- `frontend/src/components/action-plan/ActionPlanPanel.tsx`
- `frontend/src/components/action-plan/ActionPlanPanel.test.tsx`

## New dependencies

No new dependencies.

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only — phase bucketing uses fixed, pinned thresholds (no LLM involvement in bucketing, scoring, or aggregation)
- Gemini must never calculate or invent numerical emission values — this feature does not call Gemini at all
- Gemini is used only for explanation/contextualization (not applicable to this step — no narration added here; Step 07 already covers per-recommendation explanation)
- Strict input validation and type safety
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality
- Reuse `NotFoundError`/`ValidationError` and the existing FastAPI exception handlers verbatim — no new error types
- Compute on demand from current `recommendation_service.get_for_factory` data; do not cache or persist, since recommendations are deleted/regenerated on each `generate` call and stale action plans would silently diverge

## Definition of done

- [ ] `GET /api/action-plan/factory/{factory_id}` returns 404 when the factory has no calculated emissions (mirrors `get_hotspots`/`get_for_factory` precondition)
- [ ] Returns an action plan with all three phases present (each possibly empty) when the factory has zero recommendations
- [ ] Every recommendation returned by `recommendation_service.get_for_factory` appears in exactly one phase (Now/Next/Later), with no duplicates and no omissions
- [ ] Phase assignment follows fixed, non-overlapping rules, evaluated in this order (a high-cost or long-payback recommendation always lands in the more conservative phase even if the other dimension is favorable — intentional worst-of bucketing for an MVP): Later = `estimated_cost == "high"` or `payback_period > 24` months; Now = `estimated_cost == "low"` and (`payback_period` is null or `<= 6` months); Next = everything else (i.e. `estimated_cost == "medium"`, or `payback_period > 6 and <= 24` months)
- [ ] Each phase reports `total_co2_reduction` (sum of `co2_reduction` of its recommendations) and `total_implementation_cost` (sum of `COST_TIER_ESTIMATES[estimated_cost]`), matching manual calculation in unit tests
- [ ] Recommendations within each phase remain ordered by `score` desc (tie-break `id` asc), consistent with Step 06 ordering
- [ ] Unit tests cover: empty recommendations, single-phase-only recommendations, mixed-phase recommendations, null `payback_period` handling (construct a `Recommendation`/`RecommendationRead` directly with `payback_period=None` for this case — Step 06's generation pipeline always populates `payback_period`, so this path is unreachable end-to-end and must be tested at the service/unit level)
- [ ] API tests cover: 200 with populated plan, 200 with empty plan (0 recommendations), 404 for factory without calculated emissions
- [ ] Frontend `ActionPlanPanel` renders three phase sections with recommendation titles and phase totals, verified via component test
- [ ] `EmissionsDashboard.tsx` "Generate Action Plan" button fetches and displays the plan without breaking existing sections (manually verified in the running app)
- [ ] All new and existing backend tests pass (`pytest`)
- [ ] All new and existing frontend tests pass (`npm test` / vitest)
