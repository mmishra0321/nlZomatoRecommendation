# Phase 6 — HTTP API (FastAPI)

Serves the Phases 1–5 pipeline over JSON. The browser and frontend (Phase 7) should call **only** this service; `GROQ_API_KEY` stays server-side.

## Layout (Option A from `phased-architecture.md`)

- `app/main.py` — FastAPI app, CORS, routes
- `app/orchestrator.py` — `run_recommendation()` → Phase 5 `to_json_dict()` payload
- `app/schemas.py` — request body validation (Pydantic)
- `app/cache.py` — in-process dataset slice cache (dev-friendly)
- `app/config.py` — limits, timeouts, CORS defaults

## Run locally

From the **repository root** (so `src.phases` resolves):

```bash
pip install -r backend/requirements.txt
# Optional: datasets + pytest already used by phase1; ensure HF dataset deps installed per repo docs.
PYTHONPATH=. uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Loads `.env` from the repo root on startup (same pattern as Phase 4 CLI — Groq key aliases supported).

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | `{"status":"ok","groq_configured":bool}` |
| GET | `/api/v1/meta` | Limits and defaults (no secrets) |
| POST | `/api/v1/recommendations` | Phase 5 JSON response body |

### Example request

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"location":"Bellandur","minimum_rating":4.0,"top_n":5}'
```

## Configuration (environment)

| Variable | Meaning |
|----------|---------|
| `GROQ_API_KEY` | Groq API key (required for LLM path) |
| `CORS_ORIGINS` | Comma-separated allowed origins (defaults include `http://localhost:5173`) |
| `PIPELINE_TIMEOUT_SECONDS` | Wall-clock cap for the sync pipeline (default `90`) |
| `API_MAX_TOP_N`, `API_MAX_DATASET_LIMIT`, … | See `/api/v1/meta` and `app/config.py` |

## Deploy on Railway

Use the repo root as the service root; `PYTHONPATH` must include the repo root.

- Step-by-step: `docs/railway-deployment.md`.

**Start command:**

```bash
PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'
```

Set **`GROQ_API_KEY`** and **`CORS_ORIGINS`** (your Vercel URL) in the Railway service variables. Health check: **`GET /health`**.

## Tests

```bash
PYTHONPATH=. pytest tests/phases/phase6_api -v
```
