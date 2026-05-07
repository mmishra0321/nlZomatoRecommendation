# Phase-Wise Architecture: AI-Powered Restaurant Recommendation System

## End-to-End Flow
User Input -> Preference Validation -> Dataset Retrieval -> Deterministic Filtering -> Prompt Assembly -> LLM Ranking -> Response Formatting -> UI Display

## Recommended Project Structure (V1)

**Core pipeline (library-style, Phases 1-5):** lives under `src/phases/` and is imported by the backend only (not by the browser).

| Path | Role |
|------|------|
| `docs/` | Problem statement, architecture, edge cases, contracts |
| `src/phases/phase1_ingestion/` | Dataset load + canonical `Restaurant` |
| `src/phases/phase2_preferences/` | `UserPreferences` + validation |
| `src/phases/phase3_integration/` | Filter + prompt payload |
| `src/phases/phase4_llm/` | Groq client + `recommend_with_llm()` |
| `src/phases/phase5_output/` | **`build_api_response()`**, `RecommendationApiResponse`, empty-state + telemetry, Markdown export (`format_recommendations_markdown`) |
| `tests/phases/` | Phase-aligned unit/integration tests |

**Application tier (after Phase 5):** separate **backend** (HTTP + secrets + orchestration) and **frontend** (browser UI only).

| Path | Role |
|------|------|
| `backend/` *(or `src/api/`)* | FastAPI (or Flask) app: HTTP API, loads `.env`, calls `src.phases.*`, never ships Groq keys to the client |
| `frontend/` | SPA or lightweight web UI: forms, results, loading/errors; calls backend over HTTPS in prod, `http://localhost:PORT` in dev |
| `.env` | Server-side secrets (`GROQ_API_KEY`, etc.); **never** committed (use `.env.example`) |
| `frontend/.env.local` *(optional)* | **Public** config only, e.g. `VITE_API_BASE_URL=http://127.0.0.1:8000` — no Groq/HF secrets |

---

## Phase 0: Scope and Foundations
### Goal
Define scope, stack, and baseline contracts before implementation.

### Components
- Technology selection (Python backend, web frontend)
- Secret management approach (`.env`, `.env.example`)
- Dataset field contract for V1
- Explicit non-goals to avoid scope creep

### Deliverables
- Scope document
- Dataset contract document
- Local run instructions

### Exit Criteria
- Team agrees on V1 boundaries
- Required fields and outputs are fixed
- Local development setup is reproducible

---

## Phase 1: Data Ingestion and Canonical Model
### Goal
Load and normalize restaurant data from Hugging Face into a reliable internal format.

### Components
- Data loader for dataset `ManikaSaini/zomato-restaurant-recommendation`
- Normalization pipeline:
  - ratings -> numeric
  - costs -> standardized band/range
  - cuisines/location -> cleaned text
- Canonical `Restaurant` model

### Deliverables
- Ingestion module and parser
- Validation checks for missing/invalid rows
- Basic ingestion smoke test

### Exit Criteria
- Data loads successfully end-to-end
- Canonical model is consistent and query-ready
- Parsing behavior is tested on sample rows

---

## Phase 2: User Preferences and Validation
### Goal
Accept user preferences and convert them into validated structured input.

### Components
- Preference schema:
  - location
  - budget
  - cuisines
  - minimum_rating
  - additional_preferences (optional)
- Input validator with actionable error messages

### Deliverables
- Typed preference object
- Validation and coercion rules
- Error response format for API/UI

### Exit Criteria
- Invalid inputs are rejected cleanly
- Valid inputs map to a stable internal format
- Same schema is used by UI and backend

---

## Phase 3: Integration Layer (Filtering + Prompt Preparation)
### Goal
Reduce dataset to relevant candidates and prepare grounded prompt context for the LLM.

### Components
- Deterministic filter engine:
  - location match
  - budget compatibility
  - cuisine overlap
  - minimum rating
- Candidate cap (for token control), e.g. top 20-50
- Prompt builder with:
  - user preferences
  - candidate list
  - strict instruction: only choose from candidates

### Deliverables
- `filter_and_rank_candidates()` logic
- Prompt payload builder
- Edge-case handling for no matches

### Exit Criteria
- Same input always produces same shortlisted candidates
- Prompt payload is deterministic and inspectable
- No-match flow is clearly identified before LLM call

---

## Phase 4: LLM Recommendation Engine (Groq)
### Goal
Use Groq-hosted LLM to rank candidates and explain recommendations.

**LLM provider for this phase:** Groq only (not OpenAI/Anthropic direct). Configure model via `GROQ_MODEL` (default in `.env.example`: `llama-3.1-8b-instant`).

### Components
- Groq client integration using `GROQ_API_KEY`
- Structured output contract (JSON preferred)
- Response parser and schema validator
- Resilience:
  - retry on transient failures
  - fallback to deterministic top-k if LLM fails

### Deliverables
- `recommend_with_llm()` service
- JSON output parser
- Fallback recommendation strategy

### Exit Criteria
- Service returns ranked recommendations with explanations
- Output is parseable and valid
- Failure scenarios degrade gracefully

---

## Phase 5: Output Formatting and UX Semantics
### Goal
Convert recommendation payload into user-friendly output.

### Components
- Response formatter for UI/API
- Distinct empty-state messaging:
  - no candidate matches
  - LLM unavailable/invalid output
- Lightweight telemetry:
  - request latency
  - candidate count
  - model usage metadata (if available)

### Deliverables
- Package `src/phases/phase5_output/`: formatters + response DTOs shared by CLI, HTTP API, and tests *(implemented)*
- Final output DTO/JSON format (`RecommendationApiResponse.to_json_dict()`)
- Reusable UI-facing response schema (`empty_state_code`, `user_message`, `detail`, `telemetry`)
- Human-readable reason text per recommendation (plus optional Markdown via `format_recommendations_markdown`)

### Exit Criteria
- Output consistently includes required fields
- Empty/error states are understandable
- Responses are presentation-ready

### Implementation note (current repo)
- Entry point: `build_api_response(integration, result, latency_ms=..., telemetry_extra=...)`.
- JSON shape is stable for **Phase 6** to return as-is and **Phase 7** to render without ad-hoc mapping.

---

## Application split (after Phase 5): Backend + Frontend

Phases **1-5** produce a **recommendation pipeline** (pure Python). Phase **5** locks the **canonical HTTP-facing JSON** (`RecommendationApiResponse`). Everything **after Phase 5** is product work: a **backend** that runs the pipeline and returns that JSON, and a **frontend** that calls only the backend.

### Why split
- **Security:** `GROQ_API_KEY` and Hugging Face access stay on the server. The browser must not call Groq or Hugging Face directly.
- **Contracts:** One stable JSON schema for the UI, contract tests, and future clients (mobile, partner APIs).
- **Operations:** Timeouts, logging, rate limits, and CORS live in the backend.

### Target runtime diagram (logical)

```text
Browser (frontend)  --HTTP JSON-->  Backend (FastAPI)  --imports-->  src.phases.*
                                              |
                                              +--> Groq API (server-side only)
                                              +--> HF dataset (server-side cache)
```

### Shared contract (Phase 2 in → Phase 5 out)

**HTTP request (Phase 6 `POST /api/v1/recommendations`):** body maps to Phase 2 `UserPreferences` + optional knobs:
- **Required / core:** `location`, `minimum_rating`
- **Optional:** `budget` (low | medium | high | numeric cost-for-two), `cuisines` (array), `additional_preferences` (string)
- **Optional API-only (with server-enforced maxima):** `top_n`, `dataset_limit`, `candidate_cap`

**HTTP response (200):** the backend returns **`RecommendationApiResponse` JSON** (same keys as `to_json_dict()`):
- **`source`:** `llm` | `fallback` | `no_candidates`
- **`items[]`:** `rank`, `restaurant_id`, `name`, `cuisines`, `rating`, `cost_for_two`, `explanation`
- **`user_message`**, **`detail`:** headline + secondary copy for banners (empty states, degraded model)
- **`empty_state_code`:** `ok` | `no_filter_match` | `degraded_model` — lets the UI pick layout/alerts without parsing prose
- **`telemetry`:** `latency_ms`, `matched_count`, `capped_count`, `candidate_cap`, plus optional non-sensitive `extra`
- **`parse_error`**, **`http_error`:** optional diagnostics (safe to expose; no secrets)

**Errors:** `422` validation (Phase 2 / request schema); `504` or structured JSON error body on upstream timeout (never echo Groq raw headers/tokens).

---

## Phase 6: Backend API Layer
### Goal
Expose the full recommendation flow through a **versioned HTTP API** that orchestrates `src.phases.*` and owns all secrets and side effects.

### Stack (recommended)
- **Python 3.10+** (align with deployment target)
- **FastAPI** + **Uvicorn** (or Flask + Gunicorn): async-friendly, automatic OpenAPI for contract checks
- Package layout options (pick one and document in README):
  - **Option A:** `backend/app/main.py` with `from src.phases...` (repo root on `PYTHONPATH` or install `src` as a package)
  - **Option B:** `src/api/` next to `src/phases/` with a thin `main.py`

### Components
- **Orchestration service** (single entry used by routes):
  1. Parse + validate body → `UserPreferences` (Phase 2)
  2. `iter_restaurants` / cache (Phase 1) with configurable dataset limit for API safety
  3. `build_integration_output` (Phase 3)
  4. `recommend_with_llm` (Phase 4) unless `no_candidates`
  5. Measure wall time → **`build_api_response(integration, result, latency_ms=..., telemetry_extra=...)`** (Phase 5) → return **`response.to_json_dict()`** as JSON body
- **Endpoints (v1)**
  - `POST /api/v1/recommendations` — main flow; **response body = Phase 5 JSON** (see contract above)
  - `GET /health` — process up; optionally `groq_configured: true` without exposing secrets
  - `GET /api/v1/meta` *(optional)* — e.g. max `top_n`, default `candidate_cap`, dataset id (no secrets)
- **Cross-cutting**
  - **CORS:** allow only dev origins (e.g. `http://localhost:5173`) and production UI origin
  - **Timeouts:** align with Phase 4 Groq client; return `504` or structured error on overrun
  - **Request limits:** max body size; max length on `additional_preferences` (reuse Phase 2 rules)
  - **Logging:** structured logs with `request_id`, `source`, counts, latency — avoid raw PII in default log level

### Deliverables
- Runnable `uvicorn backend.app.main:app` (or equivalent) from README
- OpenAPI schema checked in or generated in CI
- Contract tests: golden JSON for happy path, `no_candidates`, and Groq failure (mocked)

### Exit Criteria
- Frontend completes one full flow using **only** this API (no direct Groq/HF from browser)
- Same logical outcome as CLI for equivalent inputs (modulo caching)
- Health and error responses are safe for operators (no secret leakage)

---

## Phase 7: Frontend Web UI
### Goal
Deliver the **primary user surface**: preference capture + ranked results + clear empty/error states, consuming **only** the Phase 6 API.

### Stack (recommended)
- **Next.js (App Router) + TypeScript** for Phase 7 implementation
- **Styling:** reuse a single design system (CSS modules or Tailwind) for spacing, typography, and loading states

### Components
- **Config:** base URL from `NEXT_PUBLIC_API_BASE_URL` (Next.js) — **never** embed API keys
- **Form:** fields mapped 1:1 to Phase 6 request (`location`, `budget`, `cuisines`, `minimum_rating`, `additional_preferences`, optional `top_n`)
- **Submit:** disable while pending; show inline validation from `422` responses
- **Results:** render **`items[]`** from Phase 5 JSON (name, cuisines, rating, `cost_for_two`, explanation); optional **`source`** badge (`LLM` / `Fallback` / `No candidates`)
- **Banners:** drive hero/alert from **`user_message`**, **`detail`**, and **`empty_state_code`** (`no_filter_match` vs `degraded_model` vs `ok`) instead of hard-coded strings in the UI
- **Empty / network UX:** distinguish HTTP/network failures from API JSON errors; retry on transient failures

### Deliverables
- `frontend/` app with README: `npm install`, `npm run dev`, env example for API base URL
- E2E happy path documented: start backend + frontend, submit Bellandur-style query, see top-N

### Exit Criteria
- No Groq or Hugging Face URLs or keys in frontend bundle (verify with build search)
- Accessible loading and error states
- Demo path matches problem statement output fields

---

## Phase 8: Hardening, Testing, and Handoff
### Goal
Improve reliability, maintainability, and developer handoff quality.

### Components
- Unit tests:
  - ingestion normalization
  - preference validation
  - filtering logic
  - output parser
- Integration tests:
  - API contract
  - fallback behavior
- Documentation:
  - setup
  - run instructions
  - environment variables
  - known limitations

### Deliverables
- Test suite with CI-ready commands
- Updated README and docs
- Operational notes (latency/cost tuning, candidate cap)

### Exit Criteria
- Core flows are covered by tests
- Project is runnable by a new developer using docs
- Release-ready milestone is achieved

---

## Phase 9: Streamlit Deployment Layer
### Goal
Ship a lightweight hosted demo using Streamlit so stakeholders can interact with recommendations without running the full Next.js + FastAPI stack locally.

### Components
- Streamlit app wrapper (for example `streamlit_app.py`) that calls the same recommendation flow.
- UI inputs mapped to Phase 2 request contract:
  - location
  - budget
  - cuisines
  - minimum_rating
  - additional_preferences
  - top_n
- Response rendering based on Phase 5 canonical payload (`source`, `items`, `user_message`, `empty_state_code`, telemetry).
- Deployment config for Streamlit Community Cloud:
  - pinned Python dependencies
  - secrets managed in Streamlit secrets (no hardcoded API keys)
  - startup command and health sanity checks

### Deliverables
- `streamlit_app.py` with end-to-end recommendation flow
- Streamlit requirements file and deployment instructions
- Hosted Streamlit URL documented in README

### Exit Criteria
- Public Streamlit URL is reachable
- User can submit preferences and receive recommendations end-to-end
- Secrets are injected via deployment settings, not committed in git

---

## Cross-Cutting Architecture Decisions
- **Grounding first:** LLM only ranks pre-filtered candidate restaurants.
- **Deterministic + AI hybrid:** Deterministic filtering ensures relevance; LLM adds ranking quality and reasoning.
- **Structured outputs:** Prefer JSON to minimize parsing ambiguity.
- **Security:** API keys stay server-side; never exposed in browser code.
- **Observability:** Track performance and failures without logging sensitive user content.

## Milestone Suggestion
- **Milestone 1:** Phases **0-5** — pipeline + Phase 5 canonical response complete under `src/phases/` + CLI smoke paths *(done for Phases 1-5 code paths in repo)*
- **Milestone 2:** Phases **6-7** — **backend HTTP API** returning Phase 5 JSON + **frontend** consuming only that API (local end-to-end demo)
- **Milestone 3:** Phase **8** — CI, API contract tests, operational docs, hardening
- **Milestone 4:** Phase **9** — Streamlit hosted demo deployment for quick stakeholder access
