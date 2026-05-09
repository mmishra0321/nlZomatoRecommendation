# Deploy backend on Railway

This API must run from the repository root so `PYTHONPATH=.` resolves `src.phases.*` and `backend.app`.

## Setup in Railway

1. Create a new Railway project and link this GitHub repository.
2. In service settings, keep the root as repository root (default).
3. Configure commands:
   - **Build Command:** `pip install --upgrade pip && pip install -r backend/requirements.txt`
   - **Start Command:** `PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'`
   - Alternative: keep the Railway start command empty and use root `Procfile` (`web: ...`) from this repo.
4. Add Railway variables:
   - `GROQ_API_KEY` (required)
   - `CORS_ORIGINS=https://<your-vercel-domain>`
   - `GROQ_MODEL=llama-3.1-8b-instant` (optional)
   - `DATASET_ID=ManikaSaini/zomato-restaurant-recommendation` (optional)
   - `PIPELINE_TIMEOUT_SECONDS=90` (optional)
5. Deploy and copy the generated Railway public domain.

## Verify

```bash
curl -s "https://<your-railway-domain>/health"
curl -s "https://<your-railway-domain>/api/v1/meta"
```

## Connect to Vercel frontend

Set this on Vercel frontend project:

- `BACKEND_API_BASE_URL=https://<your-railway-domain>`

The browser calls Vercel's `/api/recommendations`; that route forwards server-side to Railway.
