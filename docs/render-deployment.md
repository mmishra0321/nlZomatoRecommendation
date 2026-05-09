# Deploy backend on Render

This API must run from the **repository root** so `PYTHONPATH=.` resolves `src.phases.*` and `backend.app`.

## One-click blueprint (recommended)

1. Push this repo to GitHub.
2. In [Render](https://render.com): **New** → **Blueprint**.
3. Select the repo and apply `render.yaml` (Render detects it at the repo root).
4. In the web service **Environment**, set:
   - **`GROQ_API_KEY`** — your Groq API key (secret).
   - **`CORS_ORIGINS`** — comma-separated allowed browser origins for direct API calls, e.g.  
     `https://your-project.vercel.app,https://your-custom-domain.com`  
     For local dev you can omit this and rely on backend defaults (`localhost` ports).
5. Deploy and wait for the build to finish. Open **Logs** if the service fails health checks.

## Manual web service (no Blueprint)

Create a **Web Service** linked to this repo:

| Setting | Value |
|--------|--------|
| Root directory | *(empty / repo root)* |
| Runtime | Python |
| Build command | `pip install --upgrade pip && pip install -r backend/requirements.txt` |
| Start command | `PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'` |
| Health check path | `/health` |

Set the same environment variables as above. Optional: **Python version** `3.11` (matches `runtime.txt`).

## Environment variables (reference)

| Variable | Required | Notes |
|----------|----------|--------|
| `GROQ_API_KEY` | Yes (for LLM path) | Server-side only; never put in frontend. |
| `CORS_ORIGINS` | Yes for browser → Render | Comma-separated list, no spaces after commas is fine. |
| `DATASET_ID` | No | Defaults to `ManikaSaini/zomato-restaurant-recommendation`. |
| `GROQ_MODEL` | No | Default in app: `llama-3.1-8b-instant`. |
| `PIPELINE_TIMEOUT_SECONDS` | No | Default `90`. |

## Verify after deploy

```bash
curl -s "https://<your-service>.onrender.com/health"
curl -s "https://<your-service>.onrender.com/api/v1/meta"
```

## Vercel + CORS

If the Next.js app uses the **API route proxy** (`/api/recommendations`), the browser talks to Vercel only; Vercel’s server calls Render. You may still want `CORS_ORIGINS` set to your Vercel URL for any direct client calls or debugging.

## Hugging Face dataset cache

The first recommendation after a cold start may be slow while the dataset downloads. Optional: set `HF_HOME` to a persistent disk path only if you add a Render disk (not required for the free web service).
