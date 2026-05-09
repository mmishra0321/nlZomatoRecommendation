from __future__ import annotations

import os
from pathlib import Path

from src.phases.phase1_ingestion.loader import DEFAULT_DATASET_ID

_REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    return _REPO_ROOT


def default_dataset_id() -> str:
    return os.environ.get("DATASET_ID", DEFAULT_DATASET_ID)


# Tunables (env overrides)
MAX_TOP_N = int(os.environ.get("API_MAX_TOP_N", "20"))
MAX_CANDIDATE_CAP = int(os.environ.get("API_MAX_CANDIDATE_CAP", "100"))
MAX_DATASET_LIMIT = int(os.environ.get("API_MAX_DATASET_LIMIT", "10000"))
MIN_DATASET_LIMIT = int(os.environ.get("API_MIN_DATASET_LIMIT", "100"))
DEFAULT_DATASET_LIMIT = int(os.environ.get("API_DEFAULT_DATASET_LIMIT", "5000"))
DEFAULT_CANDIDATE_CAP = int(os.environ.get("API_DEFAULT_CANDIDATE_CAP", "30"))
PIPELINE_TIMEOUT_SECONDS = float(os.environ.get("PIPELINE_TIMEOUT_SECONDS", "90"))


def groq_configured() -> bool:
    return bool(os.environ.get("GROQ_API_KEY", "").strip())


def cors_allow_origins() -> list[str]:
    """Parse CORS_ORIGINS as a comma-separated list (production deployment)."""
    raw = os.environ.get("CORS_ORIGINS", "")
    if raw.strip():
        return [p.strip() for p in raw.split(",") if p.strip()]
    # Local dev defaults (Vite + Next.js)
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
