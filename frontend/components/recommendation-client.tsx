"use client";

import { FormEvent, useMemo, useState } from "react";

import { ApiRequestError, fetchRecommendations } from "@/lib/api";
import type { RecommendationResponse } from "@/lib/types";

type FieldErrors = Record<string, string>;
const LOCATION_OPTIONS = ["Basavanagudi", "Bellandur", "Koramangala", "Indiranagar", "HSR Layout"];
const CUISINE_OPTIONS = ["North Indian", "South Indian", "Chinese", "Italian", "Biryani", "Desserts"];
const BUDGET_OPTIONS = ["", "low", "medium", "high", "500", "1000", "1500", "2000"];
const RATING_OPTIONS = ["0", "3", "3.5", "4", "4.5"];
const TOP_N_OPTIONS = ["3", "5", "8", "10"];

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
  const [location, setLocation] = useState("Basavanagudi");
  const [budget, setBudget] = useState("");
  const [cuisinesInput, setCuisinesInput] = useState("North Indian");
  const [minimumRating, setMinimumRating] = useState("3.5");
  const [specificCravings, setSpecificCravings] = useState("Biryani, Butter Chicken");
  const [additionalPreferences, setAdditionalPreferences] = useState("");
  const [topN, setTopN] = useState("5");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const topItems = useMemo(() => result?.items ?? [], [result]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setFieldErrors({});
    setResult(null);
    setIsSubmitting(true);

    const notes = [specificCravings.trim(), additionalPreferences.trim()].filter(Boolean).join(". ");
    const payload = {
      location: location.trim(),
      minimum_rating: Number(minimumRating),
      budget: parseBudgetInput(budget),
      cuisines: parseCuisineInput(cuisinesInput),
      additional_preferences: notes || undefined,
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
            setErrorMessage("Please fix highlighted fields and retry.");
          } else {
            setErrorMessage("Request validation failed.");
          }
        } else if (error.status === 504) {
          setErrorMessage("The backend timed out. Try again with fewer constraints.");
        } else if (error.status === 0) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage(`Unexpected API error (${error.status}).`);
        }
      } else {
        setErrorMessage("Unexpected client error. Please retry.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="screenRoot">
      <header className="mainHeader">
        <div className="logoText">Zomato AI</div>
        <div className="headerTitle">Recommendations</div>
      </header>

      <section className="recommendationsSection">
        <aside className="leftFilters">
          <h2>Refine Preferences</h2>
          <form onSubmit={onSubmit} className="filterForm">
            <label>
              Location
              <select value={location} onChange={(e) => setLocation(e.target.value)} required>
                {LOCATION_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Budget
              <select value={budget} onChange={(e) => setBudget(e.target.value)}>
                {BUDGET_OPTIONS.map((option) => (
                  <option key={option || "any"} value={option}>
                    {option || "Any"}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Cuisine
              <select value={cuisinesInput} onChange={(e) => setCuisinesInput(e.target.value)}>
                {CUISINE_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Minimum Rating
              <select value={minimumRating} onChange={(e) => setMinimumRating(e.target.value)}>
                {RATING_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}+
                  </option>
                ))}
              </select>
            </label>
            <label>
              Top N
              <select value={topN} onChange={(e) => setTopN(e.target.value)}>
                {TOP_N_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    Top {option}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Additional Preferences
              <textarea
                rows={3}
                value={additionalPreferences}
                onChange={(e) => setAdditionalPreferences(e.target.value)}
                placeholder="Family-friendly, low noise, outdoor seating"
              />
            </label>
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Loading..." : "Get Picks"}
            </button>
          </form>
        </aside>
        <div className="rightResults">
          <h2>Zomato AI&apos;s Top Picks for You</h2>
          {errorMessage && <p className="error">{errorMessage}</p>}
          {isSubmitting ? (
            <div className="recGrid">
              {new Array(4).fill(null).map((_, idx) => (
                <article key={`loading-${idx}`} className="recCard loadingCard">
                  <div className="recPhoto shimmer" />
                  <div className="recBody">
                    <div className="line shimmer short" />
                    <div className="line shimmer medium" />
                    <div className="line shimmer long" />
                    <div className="line shimmer long" />
                    <div className="btnSkeleton shimmer" />
                  </div>
                </article>
              ))}
            </div>
          ) : topItems.length > 0 ? (
            <div className="recGrid">
              {topItems.map((item) => (
                <article key={item.restaurant_id} className="recCard">
                  <div className="recPhoto" />
                  <div className="recBody">
                    <h3>{item.name}</h3>
                    <p className="muted">
                      {item.cuisines.join(" • ")} • {item.rating.toFixed(1)} miles away
                    </p>
                    <p className="insight">{item.explanation}</p>
                    <button type="button">View Full Menu</button>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <p className="emptyState">Set filters and click Get Picks to see recommendations.</p>
          )}
        </div>
      </section>

      <footer className="mainFooter">
        <strong>Zomato AI</strong>
        <span>AI Privacy Policy</span>
        <span>Smart Search FAQ</span>
        <span>Help Center</span>
      </footer>
    </div>
  );
}
