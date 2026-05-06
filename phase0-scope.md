# Phase 0 Scope and Foundations

## Purpose
Define the minimum viable scope, contracts, and setup needed before implementation begins.

## Product Slice (V1)
- Primary interface: basic web UI for user input and recommendation display
- Supporting interface: CLI for local diagnostics and smoke runs
- Data source: Hugging Face dataset `ManikaSaini/zomato-restaurant-recommendation`
- Recommendation strategy: deterministic filtering followed by LLM ranking

## In-Scope (V1)
- Input collection for location, budget, cuisines, minimum rating, optional notes
- Dataset loading and normalization pipeline
- Grounded prompt construction from shortlisted candidates
- Groq-based ranking with structured output and fallback behavior
- Backend API for recommendation workflow
- Basic frontend to submit preferences and display results

## Out of Scope (V1)
- User accounts, authentication, saved preferences, recommendation history
- Live third-party integrations (maps, reservations, payments)
- Production-grade infra (autoscaling, multi-region, SSO, advanced observability)

## Tech and Runtime Baseline
- Backend: Python (FastAPI preferred)
- Frontend: React + Vite (or equivalent simple SPA setup)
- Environment and secrets: `.env` (never committed), template in `.env.example`
- Data handling: local cached copy for development when practical

## Success Criteria for Phase 0
- Scope is explicit and agreed
- Field contracts are documented
- Local setup steps are reproducible for a new developer
- Required environment variables are defined

## Deliverables
- `phase0-scope.md` (this file)
- `dataset-contract.md`
- `.env.example`
- `README.md` local setup instructions
- Initial folder skeleton: `backend/`, `frontend/`
