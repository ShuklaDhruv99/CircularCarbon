# Spec: Report Export

## Overview

This feature closes out the CircularCarbon AI hackathon MVP by giving the SME user a single downloadable PDF report (PRD FR-11) that compiles everything the platform has already computed for a factory: factory information, current emissions, emission breakdown, top hotspots, ranked recommendations, cost/CO₂ estimates, and the prioritized action plan (Step 09). It exists at this stage because it is the natural final output of the pipeline in CLAUDE.md — the report is a presentation layer over already-computed deterministic data, not a new calculation. It requires no new numeric computation: it strictly re-renders values already returned by Steps 05, 06, and 09.

## Depends on

- Step 02 — Database Models (`Factory`, `Process` and related tables)
- Step 05 — Carbon Calculation Engine (`emission_calculation_service.get_breakdown`)
- Step 06 — Circular Recommendations Engine (`recommendation_service.get_for_factory`)
- Step 09 — Prioritized Action Plan (`action_plan_service.get_action_plan`)

Gemini explanations (Step 07) are explicitly **out of scope** for v1: `explanation_service.generate_for_factory` is call-on-demand only, not persisted, and calls Gemini live on every invocation. Including it would make report generation slow, non-deterministic across repeated downloads, and would risk exposing an LLM in a "final record" document. The report includes only deterministic data already sourced from Steps 05/06/09.

## API Endpoints / Routes

- `GET /api/report/factory/{factory_id}` — generates and streams a PDF report for the given factory, computed on demand from current data (not cached/persisted) — no auth (matches existing endpoints); returns `application/pdf` with `Content-Disposition: attachment; filename="<factory-name>-carbon-report.pdf"`

## Database changes

No database changes. The report is generated on demand from existing data and is not persisted.

## Component & UI changes

- **Create:** `frontend/src/components/report/ReportDownloadButton.tsx` — a simple anchor-style download button pointing at the report endpoint (`<a href={reportUrl(factoryId)} download>`), disabled until the factory has calculated emissions (mirrors the existing disabled-until-ready convention used by the Action Plan section)
- **Modify:** `frontend/src/pages/EmissionsDashboard.tsx` — add a new "Download Report" section after the Prioritized Action Plan section, rendering `ReportDownloadButton`

## Files to change

- `backend/requirements.txt` — add `reportlab`
- `backend/app/main.py` — register the new report router
- `frontend/src/pages/EmissionsDashboard.tsx` — add Download Report section

## Files to create

- `backend/app/services/report_service.py` — orchestrates `factory_service.get`, `emission_calculation_service.get_breakdown`, `hotspot_service.get_hotspots`, `recommendation_service.get_for_factory`, and `action_plan_service.get_action_plan` (in that order, letting `NotFoundError` propagate unchanged), then renders a PDF via `reportlab` with these sections in order: factory information → current total emissions → emission breakdown (by category and by process) → top hotspots → ranked recommendations (with cost tier, CO₂ reduction, payback) → prioritized action plan (Now/Next/Later with phase totals). Cost figures must carry the same "placeholder estimate" caveat text already used elsewhere for `COST_TIER_ESTIMATES`. Note: each downstream service independently re-validates factory/emissions existence, so a single report request re-fetches/re-checks that state up to 4-5 times — this redundancy is an accepted hackathon-scope tradeoff (no shared "load once" context object) and should not be optimized away in v1. Each action-plan phase (Now/Next/Later) must render its heading even when empty, with an explicit "no recommendations in this phase" note — mirroring the "no recommendations generated yet" rule for the recommendations section. Sanitize/slugify the factory name before using it in the `Content-Disposition` filename (strip/replace characters unsafe for filenames or HTTP headers, e.g. `/`, `\`, quotes).
- `backend/app/api/report.py` — `GET /api/report/factory/{factory_id}` route, thin, delegating to `report_service.generate_report_pdf`, returning a `fastapi.responses.Response` with `media_type="application/pdf"`
- `backend/tests/test_report_service.py` — unit tests verifying the service produces non-empty PDF bytes and raises `NotFoundError` when upstream preconditions aren't met. Verifying PDF text content requires a test-only PDF-reading library (`pypdf`) since `reportlab` has no built-in text extraction — add `pypdf` to `backend/requirements.txt` (or a dev-only requirements file if one exists) alongside `reportlab`.
- `backend/tests/test_report_api.py` — API tests: 200 with correct `Content-Type`/`Content-Disposition` headers and non-empty PDF body for a fully-populated factory, 404 for a factory without calculated emissions, 404 for a nonexistent factory
- `frontend/src/services/report.ts` — exports a pure helper `reportUrl(factoryId: number): string` building the endpoint URL from the existing API base URL constant (no fetch/blob handling needed since the browser handles the download natively via the anchor tag)
- `frontend/src/components/report/ReportDownloadButton.tsx`
- `frontend/src/components/report/ReportDownloadButton.test.tsx` — colocated component test verifying the link renders with the correct `href` and is disabled when no emissions are calculated yet

## New dependencies

- `reportlab` (backend, Python) — pure-Python PDF generation library, no system-level dependencies (e.g. no Pango/Cairo/wkhtmltopdf), appropriate for a Windows-based hackathon environment.
- `pypdf` (backend, Python, test-only) — used solely in tests to extract text from generated PDFs for content assertions; not imported by application code.
- No frontend dependency is added since the download is a plain anchor tag.

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth — the report renders only values already returned by existing services; it performs no new arithmetic
- Deterministic calculations only — no LLM involvement anywhere in report generation
- Gemini must never calculate or invent numerical emission values — Gemini is not called at all by this feature
- Gemini is used only for explanation/contextualization (not applicable here — explanations are explicitly excluded from v1, see Depends on)
- Strict input validation and type safety
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality
- Reuse `NotFoundError`/`ValidationError` and the existing FastAPI exception handlers verbatim — no new error types
- Compute on demand, not cached/persisted, matching the convention established in Steps 07–09
- Any cost figures in the report must carry the existing "placeholder estimate, not a real financial figure" caveat already documented alongside `COST_TIER_ESTIMATES`

## Definition of done

- [ ] `GET /api/report/factory/{factory_id}` returns 404 when the factory does not exist
- [ ] Returns 404 when the factory exists but has no calculated emissions (mirrors the precondition already enforced by `emission_calculation_service.get_breakdown`/`action_plan_service.get_action_plan`)
- [ ] Returns 200 with `Content-Type: application/pdf` and a `Content-Disposition: attachment` header containing a filename derived from the factory name
- [ ] The returned PDF is non-empty and contains, at minimum, the factory name, total CO₂e, each hotspot's category/activity, each recommendation's title, and each action-plan phase name — verified in tests via `reportlab`'s own text extraction or by asserting on byte length/PDF magic bytes plus a text-layer check
- [ ] A factory with zero recommendations still produces a valid PDF (report shows emissions/hotspots sections with an explicit "no recommendations generated yet" note in the recommendations section, and each action-plan phase heading renders with an explicit "no recommendations in this phase" note when empty)
- [ ] Unit tests cover: full pipeline success, 404 propagation from each upstream service (factory missing, emissions not calculated)
- [ ] API tests cover: 200 with headers/body assertions, 404 missing factory, 404 uncalculated factory
- [ ] Frontend `ReportDownloadButton` renders a disabled state before emissions are calculated and an enabled download link afterward, verified via component test
- [ ] `EmissionsDashboard.tsx` "Download Report" section appears after the Action Plan section without breaking existing sections (manually verified in the running app — clicking the link downloads a valid PDF)
- [ ] All new and existing backend tests pass (`pytest`)
- [ ] All new and existing frontend tests pass (`npm test` / vitest)
