# Google Stitch prompt — Next.js UI (restaurant recommender)

Use the **prompt below** as a single message (or split into “design system” + “screens”) in [Google Stitch](https://stitch.withgoogle.com/) to generate UI mockups, flows, or component frames for the frontend.

**Implementation stack:** **Next.js** (App Router), TypeScript, calling a **backend-only** REST API (`POST /api/v1/recommendations`). No API keys in the client; use env e.g. `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`.

---

## Copy-paste prompt (full)

```
You are designing a web app UI for an AI-powered restaurant recommendation product (Zomato-style). The frontend is Next.js (App Router). The app talks ONLY to our backend HTTP API; never show Groq/Hugging Face keys or URLs in the UI.

PRODUCT GOAL
- User enters dining preferences and gets a ranked list of restaurants with short AI explanations, grounded in a real dataset.

KEY USER FLOWS
1) Home / search: a clear form to submit preferences.
2) Loading: accessible loading state while the API runs (may take a few seconds).
3) Results: ranked cards/table with rich detail.
4) Empty / edge states: friendly messaging when no restaurants match filters, or when the model degrades to a fallback.
5) Errors: validation errors (422), network failure, and timeout — distinct visuals and retry where sensible.

FORM FIELDS (map 1:1 to API request body)
- Location (text, required) — e.g. city or area (Bangalore, Bellandur, Koramangala).
- Budget — optional: low / medium / high OR a numeric “cost for two” style number.
- Cuisines — optional multiselect or comma-separated chips (e.g. North Indian, Italian).
- Minimum rating — number 0–5 (slider or stepper).
- Additional preferences — optional textarea (e.g. family-friendly, quick service); character limit implied.
- Top N — optional small control (e.g. 3–10) for how many results to request.

API RESPONSE (what the UI must render; design for this JSON shape conceptually)
- source: one of "llm" | "fallback" | "no_candidates"
- items[]: each row has rank, name, cuisines (tags), rating, cost_for_two, explanation (the “why this pick” text)
- user_message + detail: primary headline and secondary text for banners/alerts
- empty_state_code: "ok" | "no_filter_match" | "degraded_model" — drive banner style (success vs warning vs empty) from this code, not only from prose
- telemetry.latency_ms and matched counts may appear in a subtle footer or “debug” panel for demos (optional, non-blocking)

VISUAL & UX REQUIREMENTS
- Modern, clean SaaS aesthetic; strong typography hierarchy.
- Mobile-first responsive layout; comfortable tap targets.
- Show a small badge for source: “AI ranked”, “Fallback”, or “No matches” where appropriate.
- Cuisine tags as pills/chips; rating as stars or bold number; cost clearly labeled (e.g. “₹ for two” or “Cost for two”).
- Explanations readable: short paragraph under each restaurant.
- Use banners for empty_state_code: 
  - no_filter_match: supportive empty state (illustration or icon + CTA to widen filters)
  - degraded_model: non-alarming warning that results may be less personalized
  - ok: subtle success or neutral confirmation
- Accessibility: visible focus states, sufficient contrast, don’t rely on color alone for errors.
- Dark mode optional but if shown, provide both light and dark frames.

DELIVERABLES FROM STITCH
- Generate high-fidelity frames or a flow: (1) form, (2) loading, (3) results list, (4) empty state, (5) error state.
- Name components in a Next.js-friendly way: e.g. PreferenceForm, ResultsList, RestaurantCard, StateBanner, ApiErrorPanel.
- Do NOT include real API keys or vendor logos that imply partnership; generic “AI recommendations” is fine.

TECH CONTEXT (for annotations only; Stitch may show as notes)
- Framework: Next.js App Router; fetch from NEXT_PUBLIC_API_BASE_URL + /api/v1/recommendations
- Styling direction: Tailwind CSS or CSS Modules — consistent spacing scale (4/8/12), one accent color + neutral grays.
```

---

## Shorter prompt (wireframes only)

If Stitch has token limits, use this:

```
Next.js restaurant recommender UI: single-page flow with (1) preference form — location, optional budget & cuisines, minimum rating, optional notes, top-N; (2) loading state; (3) results — cards with name, cuisine tags, rating, cost for two, AI explanation, rank, and a badge for llm vs fallback vs no matches; (4) banners driven by empty_state_code: no_filter_match, degraded_model, ok. Mobile-first, modern SaaS, accessible. No API keys in UI. Output multiple screens for Google Stitch.
```

---

## After you export from Stitch

- Map frames to routes under `app/` (e.g. `app/page.tsx` for the main flow).
- Replace placeholder text with fields wired to `POST {NEXT_PUBLIC_API_BASE_URL}/api/v1/recommendations`.
- Align with `phased-architecture.md` Phase 7 and `backend/README.md` for the HTTP contract.
