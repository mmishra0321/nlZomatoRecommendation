# Streamlit Deployment (Phase 9)

This document explains how to run and deploy the Phase 9 Streamlit app.

## Local run

```bash
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

Open the URL shown by Streamlit (typically `http://localhost:8501`).

## Streamlit Community Cloud deployment

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, create a new app:
   - **Repository:** this repo
   - **Main file path:** `streamlit_app.py`
3. In **App settings -> Advanced settings** set:
   - **Python dependencies file:** `requirements-streamlit.txt`
   - If you leave this default, Streamlit will use root `requirements.txt` (also supported in this repo).
4. Add secrets in Streamlit (Settings -> Secrets):

```toml
GROQ_API_KEY = "your-groq-key"
DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
```

5. Deploy and confirm:
   - App loads
   - Submitting preferences returns recommendations
   - Secrets are not committed in git

## Notes

- `streamlit_app.py` uses the same orchestration flow as Phase 6 (`run_recommendation`).
- The app renders Phase 5-compatible fields (`source`, `items`, `user_message`, `empty_state_code`, telemetry).
- For production-like stability, avoid exposing extremely large dataset limits.
