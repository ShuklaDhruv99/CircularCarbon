# Spec: Factory Onboarding And Data Entry UI

## Overview

This step builds the first real user-facing feature: a progressive, four-step onboarding wizard (Factory → Process → Energy & Materials → Waste) that lets a user create a factory and enter its operational data through the Step 03 REST API. It implements the PRD's core entry point ("User can create a factory and enter data" — Phase 1 deliverable) and follows the UI/UX plan's onboarding UX (§10–11): a four-step progress indicator, plain-language prompts instead of technical jargon, and the ability to proceed to a confirmation screen without filling every optional field. This step also establishes the shared design system (color tokens, font, routing) that later dashboard/hotspot/recommendation screens will reuse, since this is the first screen built beyond the placeholder health-check page.

No calculation, hotspot, or recommendation UI belongs here — the wizard only collects and submits raw activity data. The completion screen shows a plain read-back of what was saved (via `GET /api/factories/{id}`), not a carbon dashboard (that's Step 05+).

## Depends on

- Step 01 — Project Foundation (Vite/React/TypeScript/Tailwind scaffold, `services/api.ts` request helper)
- Step 03 — Data Input API (`/api/factories`, `/api/processes`, `/api/energy`, `/api/materials`, `/api/waste` endpoints and their validation rules)

## API Endpoints / Routes

No new backend routes. The frontend consumes the existing Step 03 endpoints:

- `POST /api/factories`
- `POST /api/processes`
- `POST /api/energy`
- `POST /api/materials`
- `POST /api/waste`
- `GET /api/factories/{factory_id}` — used by the completion screen to read back the saved factory + its process/activity data

## Database changes

No database changes.

## Component & UI changes

**Create:**

- `frontend/src/pages/Onboarding.tsx` — the four-step wizard page, owns wizard state (current step, accumulated form data, created `factoryId`/`processId`) and step navigation
- `frontend/src/pages/OnboardingComplete.tsx` — confirmation screen; fetches and displays the created factory (name, industry, processes, and their energy/material/waste entries) with a link back to the landing page
- `frontend/src/components/onboarding/StepIndicator.tsx` — renders the 4-step progress bar (① Factory ② Production Process ③ Energy & Materials ④ Waste) per UI/UX §10
- `frontend/src/components/onboarding/FactoryStep.tsx` — form for name (required), industry (required, select of the 3 MVP industries), location, production volume, production unit, assessment period; submits via `POST /api/factories`
- `frontend/src/components/onboarding/ProcessStep.tsx` — form for process name (required), process type, production volume; allows adding one process for the MVP flow; submits via `POST /api/processes` with the `factoryId` from step 1
- `frontend/src/components/onboarding/EnergyMaterialsStep.tsx` — combined form: energy entries (type/quantity/unit/period) and material entries (name/quantity/unit/recycled %/source), each addable as a repeatable row; submits each row via `POST /api/energy` / `POST /api/materials` with the `processId` from step 2
- `frontend/src/components/onboarding/WasteStep.tsx` — form for waste entries (type/quantity/unit/disposal method as a plain-language radio group per UI/UX §39: Reused/Recycled/Sold/Landfilled/Other, recycled/landfilled/reused quantities); submits via `POST /api/waste`
- `frontend/src/components/ui/Button.tsx`, `frontend/src/components/ui/TextField.tsx`, `frontend/src/components/ui/SelectField.tsx` — small shared form primitives (label, input, inline validation-error text) reused across all four steps
- `frontend/src/services/onboarding.ts` — typed API calls for factories/processes/energy/materials/waste (`createFactory`, `createProcess`, `createEnergyEntry`, `createMaterialEntry`, `createWasteEntry`, `getFactory`), reusing the existing `request` helper from `services/api.ts`
- `frontend/src/types/domain.ts` — TypeScript interfaces mirroring the backend Pydantic schemas: `Factory`, `Process`, `EnergyConsumption`, `Material`, `Waste` (Create + Read shapes), matching field names/enums exactly (industry values, energy types, disposal methods)

**Modify:**

- `frontend/src/App.tsx` — replace the direct `<HomePage />` render with a router (`react-router-dom`) defining routes: `/` (existing `HomePage`), `/onboarding` (`Onboarding`), `/onboarding/complete/:factoryId` (`OnboardingComplete`)
- `frontend/src/pages/HomePage.tsx` — add a "Start Assessment" call-to-action button (per UI/UX §8 hero) that links to `/onboarding`; keep the existing backend health-check content
- `frontend/tailwind.config.js` — extend `theme.colors` with the CircularCarbon palette from `docs/UI_UX_Color_Palette_Plan.md` §2 (primary `#126B5A`, primary-dark `#0B4A3F`, secondary `#20A67A`, mint `#A7E8D0`, background `#F7F9F7`, text `#17211F`, muted `#66736F`, border `#DCE4E0`, success `#16865B`, warning `#D79520`, danger `#D9534F`, info `#3D73C9`); extend `theme.fontFamily.sans` to lead with `Inter`
- `frontend/src/index.css` — import the Inter font (Google Fonts `@import` or a `<link>` in `index.html`) so `font-sans` resolves to it
- `frontend/src/services/api.ts` — no functional change expected, but confirm the existing `ApiError`/`request` helper's error path is generic enough for the new endpoints (surface `response.json().detail` when available, since the backend returns `{"detail": "..."}` on 404/422, instead of only the generic status-code message)

## Files to change

- `frontend/src/App.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/services/api.ts`
- `frontend/tailwind.config.js`
- `frontend/src/index.css`
- `frontend/index.html` (add Google Fonts `<link>` for Inter, if not done via CSS `@import`)

## Files to create

- `frontend/src/pages/Onboarding.tsx`
- `frontend/src/pages/OnboardingComplete.tsx`
- `frontend/src/components/onboarding/StepIndicator.tsx`
- `frontend/src/components/onboarding/FactoryStep.tsx`
- `frontend/src/components/onboarding/ProcessStep.tsx`
- `frontend/src/components/onboarding/EnergyMaterialsStep.tsx`
- `frontend/src/components/onboarding/WasteStep.tsx`
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/TextField.tsx`
- `frontend/src/components/ui/SelectField.tsx`
- `frontend/src/services/onboarding.ts`
- `frontend/src/types/domain.ts`
- `frontend/src/components/onboarding/StepIndicator.test.tsx` and equivalent lightweight tests for the step forms (see Definition of done)

## New dependencies

- `react-router-dom` — page routing for the wizard/completion screens (no router exists yet)
- `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` (dev dependencies) — no frontend test runner exists yet; needed to satisfy this step's Definition of done via automated component tests

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only
- Gemini must never calculate or invent numerical emission values
- Gemini is used only for explanation/contextualization
- Strict input validation and type safety
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality

Additional rules specific to this step:

- The frontend must not compute or display any derived emissions/CO₂e figures — it only collects and echoes back raw input data
- Every optional backend field stays optional in the form; the wizard must let a user advance with only the required minimum (factory name + industry, process name, at least one activity entry per PRD Risk 3 / UI/UX §11 "Analyze with current data")
- Validation errors returned by the API (422 field errors, 404 not-found) must be shown inline/near the relevant field or as a form-level banner — never silently swallowed
- Use the `waste.disposal_method` plain-language options (Reused/Recycled/Sold/Landfilled/Other) exactly as specified in the UI/UX doc and the Step 03 schema enum

## Definition of done

- [ ] A user can complete the full wizard (Factory → Process → Energy & Materials → Waste) and land on the completion screen showing the created factory's saved data, using only real network calls to a running backend (manually verified in the browser with `npm run dev` + `uvicorn`)
- [ ] Submitting the Factory step with a missing name or unsupported industry shows a validation error and does not advance
- [ ] Submitting an Energy or Material row with a non-positive quantity, or a Material's recycled percentage outside 0–100, shows a validation error and does not submit that row
- [ ] The Waste step's disposal method is presented as the plain-language radio options and maps correctly to the backend's `reused/recycled/sold/landfilled/other` enum values
- [ ] A user can skip all optional fields at every step and still reach the completion screen with only the required minimum data saved
- [ ] The completion screen correctly displays the factory, its process, and all submitted energy/material/waste entries by calling `GET /api/factories/{factory_id}`
- [ ] `npm run build` (TypeScript project build) succeeds with no type errors
- [ ] `npm test` (new Vitest suite) passes, covering: `StepIndicator` renders the correct active step, `FactoryStep` blocks submission on missing required fields, `WasteStep` maps its radio selection to the correct enum value sent to the API (mocked)
- [ ] No emission calculation, hotspot, or recommendation logic exists anywhere in the new frontend code — confirmed by code review
