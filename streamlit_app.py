from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st

from src.phases.phase4_llm.dotenv import load_dotenv

LOCATION_OPTIONS = ["Bellandur", "Koramangala", "Indiranagar", "HSR Layout", "Basavanagudi"]
BUDGET_OPTIONS = ["", "low", "medium", "high", "500", "1000", "1500", "2000"]
CUISINE_OPTIONS = [
    "North Indian",
    "South Indian",
    "Chinese",
    "Italian",
    "Biryani",
    "Desserts",
]
RATING_OPTIONS = [0.0, 3.0, 3.5, 4.0, 4.5]
TOP_N_OPTIONS = [3, 5, 8, 10]


def _bootstrap_env() -> None:
    """Load local .env and then apply Streamlit secrets overrides."""
    load_dotenv(Path(__file__).resolve().parent / ".env")
    try:
        secrets = st.secrets  # pragma: no cover - depends on streamlit runtime
    except Exception:
        return

    if "GROQ_API_KEY" in secrets:
        os.environ["GROQ_API_KEY"] = str(secrets["GROQ_API_KEY"]).strip()
    if "DATASET_ID" in secrets:
        os.environ["DATASET_ID"] = str(secrets["DATASET_ID"]).strip()


def _render_results(payload: dict[str, Any]) -> None:
    source = payload.get("source", "unknown")
    state = payload.get("empty_state_code", "ok")
    st.subheader(payload.get("user_message", "Recommendations"))
    if payload.get("detail"):
        st.caption(str(payload["detail"]))

    st.markdown(f"**Source:** `{source}`  |  **State:** `{state}`")

    items = payload.get("items") or []
    if not items:
        st.info("No recommendations found for this query.")
    else:
        for item in items:
            cuisines = ", ".join(item.get("cuisines", []))
            rating = item.get("rating")
            cost = item.get("cost_for_two")
            st.markdown(
                f"### #{item.get('rank', '?')} - {item.get('name', 'Unknown')}\n"
                f"- **Cuisine:** {cuisines or 'N/A'}\n"
                f"- **Rating:** {rating if rating is not None else 'N/A'}\n"
                f"- **Cost for two:** {cost if cost is not None else 'N/A'}\n"
                f"- **Why:** {item.get('explanation', '')}"
            )
            st.divider()

    with st.expander("Telemetry and diagnostics"):
        st.json(
            {
                "telemetry": payload.get("telemetry"),
                "parse_error": payload.get("parse_error"),
                "http_error": payload.get("http_error"),
            }
        )


def main() -> None:
    st.set_page_config(page_title="Zomato AI Streamlit Demo", page_icon="🍽️", layout="wide")
    _bootstrap_env()

    st.title("Zomato AI - Streamlit Demo")
    st.caption("Phase 9 deployment surface (same recommendation flow as backend/API).")

    with st.form("recommendation_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            location = st.selectbox("Location", LOCATION_OPTIONS, index=0)
            selected_cuisine = st.selectbox("Cuisine", CUISINE_OPTIONS, index=0)
        with c2:
            budget = st.selectbox(
                "Budget",
                BUDGET_OPTIONS,
                index=6,  # 1500
                format_func=lambda x: "Any" if x == "" else str(x),
            )
            minimum_rating = st.selectbox("Minimum Rating", RATING_OPTIONS, index=3)
        with c3:
            top_n = st.selectbox("Top N", TOP_N_OPTIONS, index=1)
            additional_preferences = st.text_area(
                "Additional Preferences",
                value="quiet seating, family-friendly",
            )

        submitted = st.form_submit_button("Get Recommendations")

    if submitted:
        cuisines = [selected_cuisine] if selected_cuisine else []
        payload = {
            "location": location,
            "budget": budget or None,
            "cuisines": cuisines,
            "minimum_rating": float(minimum_rating),
            "additional_preferences": additional_preferences.strip() or None,
            "top_n": int(top_n),
        }

        try:
            # Import lazily so missing deployment deps surface as a user-friendly
            # Streamlit error instead of crashing at module import time.
            from backend.app.orchestrator import run_recommendation
            from backend.app.schemas import RecommendationRequest
        except ModuleNotFoundError as exc:
            st.error(
                "A required dependency is missing in the deployment environment. "
                "Ensure Streamlit uses `requirements.txt` (or `requirements-streamlit.txt`) "
                "which includes `datasets` and backend dependencies."
            )
            st.exception(exc)
            return

        try:
            body = RecommendationRequest(**payload)
            with st.spinner("Finding the best matches..."):
                response = run_recommendation(body)
            _render_results(response)
        except Exception as exc:  # pragma: no cover - runtime surfacing
            st.error("Recommendation pipeline failed.")
            st.exception(exc)


if __name__ == "__main__":
    main()
