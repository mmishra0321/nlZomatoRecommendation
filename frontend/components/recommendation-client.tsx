"use client";

import { FormEvent, useMemo, useState } from "react";

import { ApiRequestError, fetchRecommendations } from "@/lib/api";
import type { RecommendationResponse } from "@/lib/types";

type FieldErrors = Record<string, string>;

const SOURCE_LABEL: Record<string, string> = {
  llm: "AI ranked",
  fallback: "Fallback",
  no_candidates: "No candidates",
};

function parseCuisineInput(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseBudgetInput(value: string): string | number | undefined {
  const trimmed = value.trim();
  if (!trimmed) {
    return undefined;
  }
  const asNumber = Number(trimmed);
  if (!Number.isNaN(asNumber) && asNumber > 0) {
    return asNumber;
  }
  return trimmed;
}

export default function RecommendationClient() {
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState("");
  const [cuisinesInput, setCuisinesInput] = useState("");
  const [minimumRating, setMinimumRating] = useState("4.0");
  const [additionalPreferences, setAdditionalPreferences] = useState("");
  const [topN, setTopN] = useState("5");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [result, setResult] = useState<RecommendationResponse | null>(null);

  const bannerClass = useMemo(() => {
    if (!result) return "banner";
    if (result.empty_state_code === "degraded_model") return "banner bannerWarning";
    if (result.empty_state_code === "no_filter_match") return "banner bannerMuted";
    return "banner bannerSuccess";
  }, [result]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setFieldErrors({});
    setResult(null);
    setIsSubmitting(true);

    const payload = {
      location: location.trim(),
      minimum_rating: Number(minimumRating),
      budget: parseBudgetInput(budget),
      cuisines: parseCuisineInput(cuisinesInput),
      additional_preferences: additionalPreferences.trim() || undefined,
      top_n: Number(topN),
    };

    try {
      const response = await fetchRecommendations(payload);
      setResult(response);
    } catch (error) {
      if (error instanceof ApiRequestError) {
        if (error.status === 422) {
          const maybeDetail = error.payload?.detail;
          if (
            maybeDetail &&
            typeof maybeDetail === "object" &&
            "errors" in maybeDetail &&
            maybeDetail.errors
          ) {
            setFieldErrors(maybeDetail.errors);
            setErrorMessage("Please fix the highlighted fields.");
          } else {
            setErrorMessage("Request validation failed.");
          }
        } else if (error.status === 504) {
          setErrorMessage("The backend timed out. Try a smaller query and retry.");
        } else if (error.status === 0) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage(`Unexpected API error (${error.status}). Please retry.`);
        }
      } else {
        setErrorMessage("Unexpected client error. Please retry.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="container">
      <section className="panel">
        <h1 className="title">AI Restaurant Recommender</h1>
        <p className="subtitle">
          Enter preferences, call Phase 6 API, and render Phase 5 response fields.
        </p>

        <form onSubmit={onSubmit} className="formGrid">
          <label>
            Location *
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
              placeholder="Bellandur"
            />
            {fieldErrors.location && <span className="fieldError">{fieldErrors.location}</span>}
          </label>

          <label>
            Budget (low/medium/high or number)
            <input
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="2000 or high"
            />
            {fieldErrors.budget && <span className="fieldError">{fieldErrors.budget}</span>}
          </label>

          <label>
            Cuisines (comma-separated)
            <input
              value={cuisinesInput}
              onChange={(e) => setCuisinesInput(e.target.value)}
              placeholder="North Indian, Chinese"
            />
            {fieldErrors.cuisines && <span className="fieldError">{fieldErrors.cuisines}</span>}
          </label>

          <label>
            Minimum rating (0-5)
            <input
              type="number"
              min="0"
              max="5"
              step="0.1"
              value={minimumRating}
              onChange={(e) => setMinimumRating(e.target.value)}
            />
            {fieldErrors.minimum_rating && (
              <span className="fieldError">{fieldErrors.minimum_rating}</span>
            )}
          </label>

          <label>
            Top N
            <input
              type="number"
              min="1"
              max="20"
              value={topN}
              onChange={(e) => setTopN(e.target.value)}
            />
          </label>

          <label className="fullWidth">
            Additional preferences
            <textarea
              rows={3}
              value={additionalPreferences}
              onChange={(e) => setAdditionalPreferences(e.target.value)}
              placeholder="Family-friendly, quick service, veg options..."
            />
            {fieldErrors.additional_preferences && (
              <span className="fieldError">{fieldErrors.additional_preferences}</span>
            )}
          </label>

          <button type="submit" disabled={isSubmitting || !location.trim()}>
            {isSubmitting ? "Loading recommendations..." : "Get recommendations"}
          </button>
        </form>

        {errorMessage && <p className="errorBanner">{errorMessage}</p>}
      </section>

      {result && (
        <section className="panel">
          <div className={bannerClass}>
            <strong>{result.user_message}</strong>
            {result.detail ? <p>{result.detail}</p> : null}
            <div className="badgeRow">
              <span className="badge">{SOURCE_LABEL[result.source] || result.source}</span>
              <span className="badge">State: {result.empty_state_code}</span>
            </div>
          </div>

          <h2>Results</h2>
          {result.items.length === 0 ? (
            <p>No recommendations returned for this query.</p>
          ) : (
            <div className="cardGrid">
              {result.items.map((item) => (
                <article key={item.restaurant_id} className="card">
                  <div className="cardHeader">
                    <span className="rank">#{item.rank}</span>
                    <h3>{item.name}</h3>
                  </div>
                  <p>
                    <strong>Rating:</strong> {item.rating.toFixed(1)}
                  </p>
                  <p>
                    <strong>Cost for two:</strong>{" "}
                    {item.cost_for_two == null ? "N/A" : `₹${item.cost_for_two}`}
                  </p>
                  <p className="cuisineTags">
                    {item.cuisines.map((cuisine) => (
                      <span key={`${item.restaurant_id}-${cuisine}`} className="tag">
                        {cuisine}
                      </span>
                    ))}
                  </p>
                  <p>{item.explanation}</p>
                </article>
              ))}
            </div>
          )}

          <details>
            <summary>Telemetry</summary>
            <pre>{JSON.stringify(result.telemetry, null, 2)}</pre>
          </details>
        </section>
      )}
    </main>
  );
}
