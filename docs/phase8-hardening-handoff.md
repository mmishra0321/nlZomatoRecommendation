# Phase 8 Hardening and Handoff

This document captures the operational and handoff details required by Phase 8.

## CI-ready test commands

Run full phase tests:

```bash
PYTHONPATH=. pytest tests/phases -q
```

Run API-focused tests:

```bash
PYTHONPATH=. pytest tests/phases/phase6_api -v
```

Run frontend production build check:

```bash
cd frontend
npm ci
npm run build
```

## Local run instructions (end-to-end)

Backend:

```bash
PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Frontend (recommended local parity path):

```bash
cd frontend
npm install
npm run build
npm run start -- --hostname 127.0.0.1 --port 3000
```

Open `http://127.0.0.1:3000`.

## Environment variables

Core:

- `GROQ_API_KEY`: required for primary LLM path.
- `BACKEND_API_BASE_URL`: used by the Next.js API proxy when running the Phase 7 frontend against a separate FastAPI process (local dev). Not used for Streamlit-only hosting (`docs/streamlit-deployment.md`).

Backend tuning:

- `REQUEST_TIMEOUT_SECONDS` (Phase 4 LLM request timeout)
- `PIPELINE_TIMEOUT_SECONDS` (Phase 6 orchestration timeout)
- `API_MAX_TOP_N`
- `API_MAX_CANDIDATE_CAP`
- `API_MAX_DATASET_LIMIT`
- `API_DEFAULT_CANDIDATE_CAP`
- `API_DEFAULT_DATASET_LIMIT`
- `CORS_ORIGINS`

## Operational notes (latency/cost tuning)

- **Candidate cap:** lower `candidate_cap` improves prompt size and cost; default `30` is a practical balance.
- **Dataset limit:** lower `dataset_limit` reduces ingestion latency; tune by locality density.
- **Fallback behavior:** LLM failures/rate limits degrade to deterministic ranking (`source=fallback`).
- **Warm cache:** first request can be slower due to dataset/cache initialization.
- **Telemetry usage:** track `latency_ms`, `matched_count`, and `capped_count` to tune limits.

## Known limitations

- Free-tier infra can sleep and cause cold starts.
- Groq token rate limits can temporarily force fallback responses.
- Hugging Face dataset access can fail in heavily sandboxed environments.
- Placeholder media is used in frontend cards (no production image CDN yet).

## Handoff checklist

- [ ] `.env` is local-only and not committed.
- [ ] `PYTHONPATH=. pytest tests/phases -q` passes.
- [ ] Frontend `npm run build` passes.
- [ ] `/health` and `/api/v1/recommendations` verified locally.
- [ ] Deployment env vars configured in target platform.
