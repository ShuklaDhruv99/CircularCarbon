# Spec: Circular Recommendations Engine

## Overview

This is Phase 3 of the CircularCarbon AI roadmap ("Ranked Circular Recommendations", PRD §11-13). With deterministic CO₂e calculation and hotspot detection already in place (Step 05), the platform now needs to turn each emission hotspot into concrete, ranked circular-economy interventions. This step adds a deterministic recommendation-generation service that maps each hotspot's category/activity to a fixed set of candidate strategies (reduce, reuse, recycle, substitute, recover, process_optimization), computes an estimated CO₂e reduction for each candidate using the existing `emission_factors.py` tables (e.g. virgin→recycled material swap, landfill→recycled waste swap, grid→renewable energy swap), scores every candidate with a fixed weighted formula (Impact 35% + Cost 20% + Feasibility 20% + Circularity 15% + Payback 10%, per PRD §13), persists them as `Recommendation` rows linked to their hotspot, and exposes them via API. On the frontend, it adds a recommendations panel to the existing emissions dashboard showing ranked cards per hotspot. No Gemini/LLM involvement in this step — all scoring and CO₂e-reduction estimates are pure deterministic Python, matching the project's numerical-truth rule.

## Depends on

- Step 02 — Database Models (`Recommendation` table already exists and is migrated, unused until now)
- Step 03 — Data Input API
- Step 05 — Carbon Calculation Engine & Hotspot Detection (`hotspot_service.get_hotspots`, `emission_factors.py` factor tables, `EmissionResult` rows are the direct input to this step)

## API Endpoints / Routes

- `POST /api/recommendations/generate/{factory_id}` — runs the deterministic recommendation engine over every hotspot (`is_hotspot=True` rows from `hotspot_service.get_hotspots`) for the given factory, deletes and replaces that factory's existing recommendations (scoped via their linked `hotspot_id`s), and returns the full ranked list. Raises the same `NotFoundError` cases as `hotspot_service.get_hotspots` (factory missing / no processes / not yet calculated) — no auth
- `GET /api/recommendations/factory/{factory_id}` — returns the persisted recommendations for a factory, ordered by `score` descending, each including its parent hotspot's category/activity for display context. 404 if the factory doesn't exist or has no hotspots calculated yet; 200 with an empty list if the factory has been calculated with zero hotspots (e.g. total CO₂e is 0) — no auth

## Database changes

No database changes. `Recommendation` (`backend/app/models/recommendation.py`) already has the required columns (`hotspot_id`, `title`, `description`, `strategy`, `estimated_cost`, `co2_reduction`, `payback_period`, `score`, `created_at`) from the Step 02 migration. Step 06 only writes rows into the existing table; no migration is needed.

## Component & UI changes

- **Create:**
  - `frontend/src/components/recommendations/RecommendationList.tsx` — ranked list of recommendation cards (title, strategy badge, estimated CO₂e reduction, cost, payback, score) grouped/sorted by score descending
  - `frontend/src/components/recommendations/RecommendationCard.tsx` — single recommendation card showing strategy, description, and the four scoring inputs
  - `frontend/src/services/recommendations.ts` — API client functions: `generateRecommendations(factoryId)`, `getRecommendations(factoryId)`
- **Modify:**
  - `frontend/src/types/domain.ts` — add `Recommendation` type mirroring the new backend read schema
  - `frontend/src/pages/EmissionsDashboard.tsx` — render `RecommendationList` below the hotspot list, with a "Generate Recommendations" action that calls the generate endpoint and refreshes the list

## Files to change

- `backend/app/main.py` — register the new `recommendations` router after the `emissions` router
- `frontend/src/types/domain.ts` — add `Recommendation` type
- `frontend/src/pages/EmissionsDashboard.tsx` — add recommendations section and generate action

## Files to create

- `backend/app/data/recommendation_rules.py` — deterministic, versioned mapping from `(category, activity)` to candidate strategies; each candidate carries `strategy` (Literal), `title`, `description` template, a fixed `estimated_cost` tier (`low`/`medium`/`high`), a fixed `feasibility` weight, a fixed `payback_months` estimate, and — for material/waste/energy swaps — the alternate factor key in `emission_factors.py` to compute the CO₂e delta against (e.g. waste `landfilled` → candidate using the `recycled` factor)
- `backend/app/schemas/recommendation.py` — Pydantic schemas: `RecommendationRead` (`ConfigDict(from_attributes=True)`, `Literal` types for `strategy`/`estimated_cost`, includes nested hotspot `category`/`activity` for display context)
- `backend/app/services/recommendation_service.py` — deterministic pipeline: for each hotspot, look up candidate strategies from `recommendation_rules.py`, compute `co2_reduction` (Decimal, using `emission_factors.py`), compute `score` via the fixed weighted formula (Impact 35% + Cost 20% + Feasibility 20% + Circularity 15% + Payback 10%, each sub-score normalized 0-100 per rules below), persist `Recommendation` rows, return them ordered by `score` descending
- `backend/app/api/recommendations.py` — router exposing the two endpoints above, delegating to `recommendation_service`
- `backend/tests/test_recommendation_service.py` — unit tests for the scoring/ranking pipeline (known hotspot inputs → expected candidate set, expected `co2_reduction`, expected relative ordering by `score`)
- `backend/tests/test_recommendations_api.py` — API tests for the two new routes (generate, get, 404 cases, empty-list case)
- `frontend/src/components/recommendations/RecommendationList.tsx`
- `frontend/src/components/recommendations/RecommendationCard.tsx`
- `frontend/src/services/recommendations.ts`
- `frontend/src/components/recommendations/RecommendationList.test.tsx` — component test for rendering ranked recommendation data, colocated next to the component per Step 04/05 convention

## New dependencies

No new dependencies. Scoring is a plain deterministic weighted-sum in Python using `decimal.Decimal`; scikit-learn (mentioned in CLAUDE.md architecture) is deferred — not needed for this hackathon-scope rule-based ranker.

## Scoring determinism rules

These pin down the exact scoring formula so it is reproducible and testable (same hotspot inputs always produce the same `score`):

- **Impact score (35%):** `co2_reduction / hotspot.co2e * 100`, capped at 100, rounded to 2 decimal places (`Decimal`, `ROUND_HALF_UP`).
- **Cost score (20%):** fixed lookup from `estimated_cost` tier — `low` → 100, `medium` → 60, `high` → 30 (lower cost scores higher, since cost is a barrier).
- **Feasibility score (20%):** fixed per-candidate value from `recommendation_rules.py` (0-100), reflecting how straightforward the intervention is for an SME (documented per-strategy in the rules file, not invented per-call).
- **Circularity score (15%):** fixed lookup from `strategy` — `recycle`/`reuse`/`recover` → 100 (closes the loop), `substitute` → 70, `reduce`/`process_optimization` → 50 (efficiency, not circularity).
- **Payback score (10%):** fixed lookup from `payback_months` bands — `<= 6` → 100, `<= 12` → 70, `<= 24` → 40, `> 24` → 10.
- **Final score:** `Impact*0.35 + Cost*0.20 + Feasibility*0.20 + Circularity*0.15 + Payback*0.10`, rounded to 2 decimal places.
- **`co2_reduction` unit:** stored as absolute CO₂e (same unit as `EmissionResult.co2e`), not a percentage, computed as `hotspot.co2e - candidate_co2e` where `candidate_co2e` is recomputed using the alternate factor from `emission_factors.py` (e.g. swapping `MATERIAL_VIRGIN_FACTOR` for `MATERIAL_RECYCLED_FACTOR`, or `WASTE_DISPOSAL_FACTORS['landfilled']` for `WASTE_DISPOSAL_FACTORS['recycled']`). For `reduce`/`process_optimization` candidates with no factor swap (pure consumption reduction), use a fixed documented reduction percentage from `recommendation_rules.py` (e.g. 8% per PRD §12 example) applied to the hotspot's `co2e`.
- **Candidates per hotspot:** each hotspot yields at least one candidate strategy (never zero) so every hotspot gets at least one recommendation; `recommendation_rules.py` must therefore define a fallback `process_optimization` candidate for any `(category, activity)` combination not otherwise mapped.

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only — same hotspot inputs always produce the same `co2_reduction`/`score`; no randomness, no LLM involvement in this step
- Gemini must never calculate or invent numerical emission values (Gemini is out of scope for this step entirely — explanation of recommendations is Step 07)
- Gemini is used only for explanation/contextualization (not applicable to this step)
- Strict input validation and type safety — reuse the existing `NotFoundError` pattern from `backend/app/services/errors.py`
- Use `Decimal` throughout the scoring/CO₂e-delta pipeline (never `float`), matching Step 05's convention
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality (Steps 01-05 files stay untouched except the explicit router/type/dashboard additions listed above)

## Definition of done

- [ ] `recommendation_rules.py` maps every `(category, activity)` combination reachable from `emission_factors.py` to at least one candidate strategy, plus a fallback `process_optimization` candidate for unmapped combinations
- [ ] `POST /api/recommendations/generate/{factory_id}` recalculates and persists `Recommendation` rows for all current hotspots in a factory, replacing prior recommendations, and returns them ordered by `score` descending
- [ ] `GET /api/recommendations/factory/{factory_id}` returns the persisted, ranked recommendation list with hotspot context, 404 when not yet calculated, and `[]` when calculated with zero hotspots
- [ ] Unit tests verify the scoring formula against hand-computed expected sub-scores and final `score` for at least one material, one waste, and one energy hotspot
- [ ] API tests verify 404 behavior and the empty-list case, and 200 with correct payload shape/ordering otherwise
- [ ] `RecommendationList`/`RecommendationCard` render ranked recommendation data on `EmissionsDashboard` given a factory with calculated hotspots
- [ ] "Generate Recommendations" action on the dashboard calls the generate endpoint and refreshes displayed data
- [ ] `npm run build` (frontend) and `pytest` (backend) both pass with no regressions to existing Step 01-05 functionality
