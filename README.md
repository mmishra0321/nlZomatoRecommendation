# AI-Powered Restaurant Recommendation System

This repository contains planning and foundational setup for an AI-powered restaurant recommendation system (Zomato-inspired), using deterministic filtering plus LLM ranking.

## Phase 0 Artifacts
- `problemStatement.md` - product and requirement definition
- `phased-architecture.md` - implementation roadmap by phase
- `edge-cases.md` - phase-wise edge-case catalog
- `phase0-scope.md` - V1 scope and non-goals
- `dataset-contract.md` - canonical data schema and normalization rules
- `.env.example` - required environment variables

## Project Skeleton
- `src/phases/` - phase-wise implementation modules (library-style pipeline)
- `tests/phases/` - phase-wise tests
- `frontend/` - web UI (Phase 7)
- `backend/` - Phase 6 FastAPI service (`PYTHONPATH=. uvicorn backend.app.main:app`)

## Local Setup (Phase 0 Baseline)
1. Create a local environment file:
   - Copy `.env.example` to `.env`
2. Add your Groq key in `.env`:
   - `GROQ_API_KEY=<your-key>`
3. Keep `.env` private and never commit it.

## Next Step (Phase 1)
Implement data ingestion and canonical modeling:
- load dataset from Hugging Face
- normalize fields into canonical schema from `dataset-contract.md`
- add ingestion smoke test and row-level validation stats

## Current Status
- Phase 0: completed (scope + contracts + setup artifacts)
- Phase 1: implemented in `src/phases/phase1_ingestion/`
- Phase 2: implemented in `src/phases/phase2_preferences/`
- Phase 3: implemented in `src/phases/phase3_integration/`
- Phase 4: implemented in `src/phases/phase4_llm/` (Groq + parser + fallback)
- Phase 5: implemented in `src/phases/phase5_output/` (API DTO, empty states, telemetry, Markdown)
- Phase 6: implemented in `backend/` (FastAPI + orchestration; see `backend/README.md`)
- Phase 7: implemented in `frontend/` (Next.js UI consuming backend API)
- Phase 8: hardening + handoff artifacts implemented (`.github/workflows/ci.yml`, docs, expanded API contract tests)

## Phase 8 Quickstart (quality gates)
- Run tests: `PYTHONPATH=. pytest tests/phases -q`
- Build frontend: `cd frontend && npm ci && npm run build`
- CI workflow: `.github/workflows/ci.yml`
- Handoff/ops notes: `docs/phase8-hardening-handoff.md`
- Backend hosting (Render): `docs/render-deployment.md` + `render.yaml`
- Frontend hosting (Vercel): `docs/vercel-deployment.md`
