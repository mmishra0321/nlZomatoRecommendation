# Unified deployment: Streamlit (UI + backend)

The hosted demo runs **one** Streamlit process. It renders the UI and calls `run_recommendation()` from the same codebase as the FastAPI backend (`backend/app/orchestrator.py`). No separate Vercel/Railway services are required for this path.

## Plan (high level)

1. **Repository**: main file `streamlit_app.py` at repo root; Python deps via root `requirements.txt` → `requirements-streamlit.txt`.
2. **Secrets**: `GROQ_API_KEY` (and optionally `DATASET_ID`) in Streamlit Community Cloud **Secrets**, never in git.
3. **Runtime**: `runtime.txt` pins Python 3.11 for reproducible builds. First cold start may download the Hugging Face dataset; in-process cache helps subsequent requests.
4. **Optional local FastAPI**: You can still run `uvicorn backend.app.main:app` for API testing; it is not required for Streamlit-only hosting.

## Local run

From the **repository root**:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-streamlit.txt
cp .env.example .env        # add GROQ_API_KEY
streamlit run streamlit_app.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

## Streamlit Community Cloud (implementation checklist)

| Step | Action |
|------|--------|
| 1 | Push this repo to GitHub. |
| 2 | [Streamlit Cloud](https://streamlit.io/cloud) → **New app** → connect the repo. |
| 3 | **Main file path:** `streamlit_app.py` |
| 4 | **Branch:** `main` (or your default branch). |
| 5 | **Python version:** uses `runtime.txt` at repo root (`python-3.11.10`). |
| 6 | **Dependencies:** set app to use **`requirements.txt`** at repo root (it includes `requirements-streamlit.txt`). |

### Secrets (Settings → Secrets)

Use TOML format:

```toml
GROQ_API_KEY = "your-groq-key"
DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
```

### Optional environment variables (same as Phase 6 tuning)

If the app hits memory limits on free tier, add variables in the app dashboard (not secrets file) as needed:

- `API_DEFAULT_DATASET_LIMIT=1200`
- `API_MAX_DATASET_LIMIT=3000`
- `API_DEFAULT_CANDIDATE_CAP=20`
- `PIPELINE_TIMEOUT_SECONDS=90`

### Smoke test after deploy

1. Open the public Streamlit URL.
2. Leave defaults or set filters → **Get Recommendations**.
3. Expect ranked items or a clear empty state — not `ModuleNotFoundError`.
4. If telemetry expander shows `groq_configured`-style issues, verify `GROQ_API_KEY` in Secrets and redeploy.

## Notes

- **Dark theme:** `.streamlit/config.toml` + inline styles in `streamlit_app.py`.
- **Imports:** `streamlit_app.py` prepends the repo root to `sys.path` so `backend` and `src` resolve on Cloud.
- **Module errors:** If `ModuleNotFoundError: datasets` (or similar), confirm Cloud is using **root** `requirements.txt`, not a missing path.

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| `No module named 'datasets'` | Dependencies file = root `requirements.txt`; redeploy. |
| `No module named 'backend'` | Ensure main file is repo-root `streamlit_app.py` and latest commit includes `sys.path` bootstrap. |
| Slow first request | Normal — HF dataset download; wait or lower `API_DEFAULT_DATASET_LIMIT`. |
| OOM / crash | Lower `API_DEFAULT_DATASET_LIMIT` and `API_DEFAULT_CANDIDATE_CAP`; upgrade instance if available. |
