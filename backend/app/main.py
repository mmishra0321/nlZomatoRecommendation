from __future__ import annotations

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from src.phases.phase2_preferences.service import PreferenceValidationError
from src.phases.phase4_llm.dotenv import load_dotenv

from backend.app.config import (
    PIPELINE_TIMEOUT_SECONDS,
    cors_allow_origins,
    default_dataset_id,
    groq_configured,
    repo_root,
)
from backend.app.orchestrator import run_recommendation
from backend.app.schemas import RecommendationRequest

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(repo_root() / ".env")
    yield


app = FastAPI(
    title="Restaurant Recommendation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.get("/health")
def health():
    return {"status": "ok", "groq_configured": groq_configured()}


@app.get("/api/v1/meta")
def api_meta():
    from backend.app import config as cfg

    return {
        "dataset_id_default": default_dataset_id(),
        "max_top_n": cfg.MAX_TOP_N,
        "max_candidate_cap": cfg.MAX_CANDIDATE_CAP,
        "max_dataset_limit": cfg.MAX_DATASET_LIMIT,
        "min_dataset_limit": cfg.MIN_DATASET_LIMIT,
        "default_candidate_cap": cfg.DEFAULT_CANDIDATE_CAP,
        "default_dataset_limit": cfg.DEFAULT_DATASET_LIMIT,
        "pipeline_timeout_seconds": cfg.PIPELINE_TIMEOUT_SECONDS,
    }


@app.post("/api/v1/recommendations")
async def post_recommendations(request: Request, body: RecommendationRequest):
    rid = getattr(request.state, "request_id", None)
    try:
        payload = await asyncio.wait_for(
            asyncio.to_thread(run_recommendation, body),
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )
    except PreferenceValidationError as exc:
        raise HTTPException(status_code=422, detail={"errors": exc.errors}) from exc
    except asyncio.TimeoutError as exc:
        logger.warning("pipeline_timeout request_id=%s", rid)
        raise HTTPException(
            status_code=504,
            detail={"message": "Recommendation pipeline timed out."},
        ) from exc

    logger.info(
        "recommendation_ok request_id=%s source=%s matched=%s",
        rid,
        payload.get("source"),
        (payload.get("telemetry") or {}).get("matched_count"),
    )
    return payload
