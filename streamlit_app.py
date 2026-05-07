from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st

from backend.app.orchestrator import run_recommendation
from backend.app.schemas import RecommendationRequest
from src.phases.phase4_llm.dotenv import load_dotenv


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
            location = st.text_input("Location", value="Bellandur")
            cuisines_raw = st.text_input("Cuisines (comma-separated)", value="North Indian")
        with c2:
            budget = st.text_input("Budget (low/medium/high or number)", value="1500")
            minimum_rating = st.number_input(
                "Minimum Rating",
                min_value=0.0,
                max_value=5.0,
                value=4.0,
                step=0.1,
            )
        with c3:
            top_n = st.number_input("Top N", min_value=1, max_value=20, value=5, step=1)
            additional_preferences = st.text_area(
                "Additional Preferences",
                value="quiet seating, family-friendly",
            )

        submitted = st.form_submit_button("Get Recommendations")

    if submitted:
        cuisines = [part.strip() for part in cuisines_raw.split(",") if part.strip()]
        payload = {
            "location": location,
            "budget": budget.strip() or None,
            "cuisines": cuisines,
            "minimum_rating": float(minimum_rating),
            "additional_preferences": additional_preferences.strip() or None,
            "top_n": int(top_n),
        }

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
