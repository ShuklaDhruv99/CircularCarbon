# Spec: Gemini Explanation

## Overview

This is Phase 3b of the CircularCarbon AI roadmap ("Gemini Explanation", PRD §17 FR-10 "Explainable AI", §19 "AI Architecture", §35 "Recommendation Engine — Important Design Decision"). With ranked circular recommendations already computed deterministically (Step 06), the platform now adds a natural-language explanation layer on top of that existing data. For each persisted `Recommendation`, this step generates a short, structured "why was this recommended" explanation (why / what to do / expected benefit / assumptions) using the Gemini API, grounded strictly in the verified hotspot and recommendation values already stored in the database. Gemini is never given the ability to invent or alter emission factors, costs, CO₂ reduction figures, or scores — it only narrates the numbers the deterministic engine already produced (PRD §19, §38 Risk 2). If the Gemini API key is not configured or the call fails, the service falls back to a deterministic template-based explanation built from the same verified values, so the feature degrades gracefully rather than breaking the demo.

## Depends on

- Step 02 — Database Models (`Recommendation`, `EmissionResult` tables)
- Step 05 — Carbon Calculation Engine & Hotspot Detection (`EmissionResult` hotspot rows: `category`, `activity`, `co2e`, `percentage_contribution`)
- Step 06 — Circular Recommendations Engine (`Recommendation` rows: `title`, `description`, `strategy`, `estimated_cost`, `co2_reduction`, `payback_period`, `score` — the direct input to this step)
- Step 05 — `hotspot_service.get_hotspots` (`HotspotRead.co2e`, `HotspotRead.percentage` — `RecommendationRead` only carries `hotspot_category`/`hotspot_activity`, not `co2e`/`percentage`, so `explanation_service` must independently call `hotspot_service.get_hotspots(db, factory_id)` and join each recommendation to its parent hotspot by `hotspot_id` to obtain these two fields)
- `gemini_api_key` setting already scaffolded in `backend/app/core/config.py` (Step 01), unused until now

## API Endpoints / Routes

- `POST /api/explanations/generate/{factory_id}` — generates one explanation per currently-persisted `Recommendation` for the given factory (fetched via `recommendation_service.get_for_factory`), returns them as a list ordered the same way (by `score` descending). Does not persist explanations — regenerated on each call, matching the "Generate" convention from Step 06. Raises `NotFoundError` (404) if the factory doesn't exist or has no recommendations generated yet (same precondition as `GET /api/recommendations/factory/{factory_id}`); returns `[]` if the factory has zero recommendations — no auth

## Database changes

No database changes. Explanations are computed on demand from existing `Recommendation`/`EmissionResult` rows and are not persisted, to keep this step's scope minimal for the hackathon (PRD's "store historical assessments" is a secondary goal, out of scope here).

## Component & UI changes

- **Create:**
  - `frontend/src/components/recommendations/ExplanationPanel.tsx` — renders one recommendation's explanation (Why / What to do / Expected benefit / Assumptions), with loading and error states
  - `frontend/src/services/explanations.ts` — API client function: `generateExplanations(factoryId)`
- **Modify:**
  - `frontend/src/types/domain.ts` — add `Explanation` type mirroring the new backend read schema
  - `frontend/src/pages/EmissionsDashboard.tsx` — add an "Explain Recommendations" action (mirroring the existing `handleGenerateRecommendations` pattern) that calls `generateExplanations(factoryId)`, stores the resulting list in state keyed by `recommendation_id`, and passes it down to `RecommendationList` as an `explanations` prop — `RecommendationList`/`RecommendationCard` stay presentational (props in, render out, matching their current implementation) and only render an `ExplanationPanel` under a card when a matching explanation is present in the prop map

## Files to change

- `backend/app/main.py` — register the new `explanations` router after the `recommendations` router
- `backend/app/core/config.py` — add `gemini_model` setting (default `"gemini-2.0-flash"`) alongside the existing `gemini_api_key`
- `backend/requirements.txt` — add `google-generativeai`
- `frontend/src/types/domain.ts` — add `Explanation` type
- `frontend/src/pages/EmissionsDashboard.tsx` — add "Explain Recommendations" action, explanation state, and pass explanations down to `RecommendationList`
- `frontend/src/components/recommendations/RecommendationList.tsx` — accept an `explanations` prop (map/array keyed by `recommendation_id`) and render `ExplanationPanel` under each matching `RecommendationCard`; no new state or API calls added here

## Files to create

- `backend/app/ai/gemini_client.py` — thin wrapper around the `google-generativeai` SDK: reads `settings.gemini_api_key`/`settings.gemini_model`, exposes `generate_explanation(prompt: str) -> str`, raises a dedicated `GeminiUnavailableError` if the key is unset or the API call fails/times out (caught by the service layer to trigger the fallback path) — no retries, single call, enforced via the SDK's own per-call timeout option (`request_options={"timeout": 10}` on `generate_content`, per the pinned `google-generativeai` version's API) rather than a manual thread/signal wrapper
- `backend/app/ai/prompts.py` — builds the strict, grounded prompt string from only verified inputs (hotspot `category`, `activity`, `co2e`, `percentage`; recommendation `title`, `strategy`, `description`, `estimated_cost`, `co2_reduction`, `payback_period` — rendered as "not applicable" when `None`, `score`), explicitly instructing Gemini to (a) only reference the numbers provided, (b) never invent emission factors/costs/figures, (c) respond in the four labeled sections (Why / What to do / Expected benefit / Assumptions) so the response can be parsed deterministically
- `backend/app/schemas/explanation.py` — Pydantic schemas: `ExplanationRead` (`recommendation_id: int`, `why: str`, `what_to_do: str`, `expected_benefit: str`, `assumptions: str`, `source: Literal["gemini", "fallback"]`)
- `backend/app/services/explanation_service.py` — orchestration: fetch a factory's recommendations via `recommendation_service.get_for_factory` and its hotspots via `hotspot_service.get_hotspots`, join each `RecommendationRead` to its parent `HotspotRead` by `hotspot_id`; for each pair, build the prompt via `prompts.py`, call `gemini_client.generate_explanation` (skipping the call entirely and going straight to fallback when `settings.gemini_api_key` is empty), parse the four labeled sections from the response text; on any `GeminiUnavailableError` or parse failure, build the same four sections from a deterministic Python string template using only the verified values (`source="fallback"`); returns `list[ExplanationRead]` in the same order as `recommendation_service.get_for_factory`
- `backend/app/api/explanations.py` — router exposing the endpoint above, delegating to `explanation_service`
- `backend/tests/test_explanation_service.py` — unit tests: (a) fallback-path explanation contains only values present in the input recommendation/hotspot (no network call, `gemini_client` mocked to raise `GeminiUnavailableError`), (b) Gemini-path parsing correctly splits a well-formed four-section mock response into `ExplanationRead` fields, (c) malformed/unparseable Gemini response falls back to the template path
- `backend/tests/test_explanations_api.py` — API tests: 404 when factory has no recommendations, `[]` when factory has zero recommendations, 200 with one explanation per recommendation (Gemini client mocked/patched so tests never make a real network call)
- `frontend/src/components/recommendations/ExplanationPanel.tsx`
- `frontend/src/services/explanations.ts`
- `frontend/src/components/recommendations/ExplanationPanel.test.tsx` — component test for rendering explanation sections, colocated per Step 04/05/06 convention

## New dependencies

- `google-generativeai` (backend) — official Gemini SDK, used only by `backend/app/ai/gemini_client.py`

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth — Gemini is never called before the deterministic `Recommendation`/`EmissionResult` rows already exist, and is never asked to compute anything
- Deterministic calculations only — no new numbers are computed in this step; explanations narrate existing `co2_reduction`/`score`/`co2e`/`payback_period` values verbatim
- Gemini must never calculate or invent numerical emission values — the prompt in `prompts.py` explicitly forbids inventing figures, and only the values already in the DB are interpolated into it
- Gemini is used only for explanation/contextualization — this entire step is that explanation layer; no other responsibility is added to it
- Strict input validation and type safety — reuse the existing `NotFoundError` pattern from `backend/app/services/errors.py`; `gemini_client` failures are a distinct `GeminiUnavailableError`, never allowed to propagate as a 500 to the API caller (always caught and handled via the fallback template)
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality (Steps 01-06 files stay untouched except the explicit router/config/type/component additions listed above)

## Definition of done

- [ ] `POST /api/explanations/generate/{factory_id}` returns one `ExplanationRead` per currently-persisted recommendation, in the same `score`-descending order as `GET /api/recommendations/factory/{factory_id}`
- [ ] 404 when the factory has no recommendations generated yet; `200` with `[]` when it has zero recommendations
- [ ] Every explanation's `why`/`what_to_do`/`expected_benefit`/`assumptions` text is derivable from that recommendation's/hotspot's own stored values — no fabricated numbers, verified by unit test
- [ ] When `gemini_api_key` is unset, the endpoint short-circuits straight to the fallback template with no network call attempted; when the key is set but the Gemini call fails/times out, it also falls back — both cases return a complete, correctly-shaped explanation for every recommendation (`source="fallback"`), verified by unit test with no real network call
- [ ] A well-formed Gemini response is correctly parsed into the four sections (`source="gemini"`), verified by unit test with a mocked client
- [ ] API tests verify 404, empty-list, and 200 payload shape/ordering, with `gemini_client` mocked so no real network call is made
- [ ] "Explain Recommendations" action on `RecommendationList` calls the generate endpoint and renders an `ExplanationPanel` under each matching `RecommendationCard`
- [ ] `npm run build` (frontend) and `pytest` (backend) both pass with no regressions to existing Step 01-06 functionality
