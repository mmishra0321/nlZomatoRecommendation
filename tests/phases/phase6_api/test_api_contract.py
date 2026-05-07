from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from src.phases.phase4_llm.models import RecommendationResult


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_recommendations_contract_fields(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Contract smoke test: the HTTP API must always return Phase 5 top-level keys.
    """
    from src.phases.phase1_ingestion.loader import IngestionStats

    monkeypatch.setattr(
        "backend.app.orchestrator.load_restaurants_cached",
        lambda *a, **k: ([], IngestionStats()),
    )

    response = client.post(
        "/api/v1/recommendations",
        json={"location": "Bellandur", "minimum_rating": 4.0},
    )
    assert response.status_code == 200
    body = response.json()

    expected_keys = {
        "source",
        "items",
        "user_message",
        "detail",
        "empty_state_code",
        "telemetry",
        "parse_error",
        "http_error",
    }
    assert expected_keys.issubset(body.keys())
    assert isinstance(body["items"], list)
    assert isinstance(body["telemetry"], dict)


def test_recommendations_degraded_model_state(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    When LLM path degrades to fallback with error metadata, API should expose
    `degraded_model` empty-state code for frontend banners.
    """
    from src.phases.phase1_ingestion.models import BudgetBand, Restaurant

    restaurants = [
        Restaurant(
            id="r1",
            name="Sample Place",
            location="Bellandur",
            cuisines=["North Indian"],
            cost_for_two=1200.0,
            budget_band=BudgetBand.MEDIUM,
            rating=4.5,
            rating_count=100,
            raw_record=None,
        )
    ]

    monkeypatch.setattr(
        "backend.app.orchestrator.load_restaurants_cached",
        lambda *a, **k: (restaurants, {"mocked": True}),
    )
    monkeypatch.setattr(
        "backend.app.orchestrator.recommend_with_llm",
        lambda *a, **k: RecommendationResult(
            source="fallback",
            items=tuple(),
            http_error="simulated upstream timeout",
        ),
    )

    response = client.post(
        "/api/v1/recommendations",
        json={"location": "Bellandur", "minimum_rating": 4.0},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "fallback"
    assert body["empty_state_code"] == "degraded_model"
    assert body["http_error"] == "simulated upstream timeout"
