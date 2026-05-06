from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.cache import clear_restaurant_cache
from backend.app.main import app


@pytest.fixture
def client():
    clear_restaurant_cache()
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "groq_configured" in body


def test_meta(client: TestClient) -> None:
    r = client.get("/api/v1/meta")
    assert r.status_code == 200
    meta = r.json()
    assert meta["max_top_n"] >= 1
    assert meta["default_candidate_cap"] >= 1


def test_x_request_id_roundtrip(client: TestClient) -> None:
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers.get("X-Request-ID") == "abc-123"


def test_recommendations_body_validation(client: TestClient) -> None:
    r = client.post("/api/v1/recommendations", json={})
    assert r.status_code == 422


def test_no_candidates_json_shape(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.phases.phase1_ingestion.loader import IngestionStats

    monkeypatch.setattr(
        "backend.app.orchestrator.load_restaurants_cached",
        lambda *a, **k: ([], IngestionStats()),
    )

    r = client.post(
        "/api/v1/recommendations",
        json={
            "location": "Bellandur",
            "minimum_rating": 4.0,
            "dataset_limit": 500,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["source"] == "no_candidates"
    assert data["empty_state_code"] == "no_filter_match"
    assert "items" in data
    assert "telemetry" in data
    assert data["telemetry"]["matched_count"] == 0


def test_preference_validation_phase2(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 2 rejects budget garbage after Pydantic accepts the body shape."""
    from src.phases.phase1_ingestion.loader import IngestionStats

    monkeypatch.setattr(
        "backend.app.orchestrator.load_restaurants_cached",
        lambda *a, **k: ([], IngestionStats()),
    )

    r = client.post(
        "/api/v1/recommendations",
        json={
            "location": "Koramangala",
            "budget": "not-a-real-band",
            "minimum_rating": 3.0,
        },
    )
    assert r.status_code == 422
    assert "budget" in r.json()["detail"]["errors"]
