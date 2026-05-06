# Problem Statement: AI-Powered Restaurant Recommendation System

## Overview
Build an AI-powered restaurant recommendation system inspired by Zomato.  
The application should combine structured restaurant data with an LLM to provide relevant, explainable, and user-friendly recommendations.

## Objective
Design and implement an application that:
- Accepts user preferences (location, budget, cuisine, minimum rating, optional notes)
- Uses a real restaurant dataset for candidate retrieval
- Applies deterministic filtering before LLM reasoning
- Returns ranked recommendations with clear explanations
- Presents results in a simple and readable interface

## Data Source
- Dataset: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Core fields to use:
  - Restaurant name
  - Location
  - Cuisines
  - Cost/Budget indicator
  - Rating

## Functional Requirements

### 1) User Input
Collect user preferences:
- Location (e.g., Delhi, Bangalore)
- Budget (e.g., low/medium/high or numeric range)
- Preferred cuisine(s)
- Minimum rating
- Optional additional preferences (e.g., family-friendly, quick service)

### 2) Data Ingestion and Preparation
- Load and preprocess the dataset
- Normalize important fields (rating, cost, cuisines, location names)
- Handle missing values and remove invalid/duplicate records when necessary
- Map data into a clean internal schema

### 3) Integration Layer
- Apply deterministic filters using user preferences
- Limit shortlisted restaurants to a manageable candidate set for the LLM
- Build a structured prompt that includes:
  - User preferences
  - Candidate restaurant list
  - Clear output constraints (recommend only from shortlisted candidates)

### 4) Recommendation Engine (LLM)
- Use an LLM to rank shortlisted restaurants
- Generate a short explanation for each recommendation
- Return structured output (preferred: JSON) for reliable downstream rendering
- Implement fallback behavior if the LLM call fails

### 5) Output Display
Display top recommendations with:
- Restaurant name
- Cuisines
- Rating
- Estimated cost
- AI-generated reason for recommendation

## Non-Functional Requirements
- Response should be understandable and actionable for end users
- Recommendations should be grounded in dataset candidates (no hallucinated restaurants)
- System should handle empty or no-match scenarios gracefully
- API keys and secrets must be stored securely (e.g., `.env`, never committed)

## Success Criteria
The solution is successful when:
- A user submits preferences and receives relevant top-N recommendations
- Each recommendation includes an explanation tied to user preferences
- No-match and error states are clearly communicated
- The full flow works end-to-end: input -> filtering -> LLM ranking -> output display

## Out of Scope (V1)
- User accounts and personalization history
- Live integration with external restaurant APIs
- Maps, booking, or payment integrations
Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)
You are tasked with building an AI-powered restaurant recommendation service inspired by Zomato. The system should intelligently suggest restaurants based on user preferences by combining structured data with a Large Language Model (LLM).
Objective
Design and implement an application that:
Takes user preferences (such as location, budget, cuisine, and ratings)
Uses a real-world dataset of restaurants
Leverages an LLM to generate personalized, human-like recommendations
Displays clear and useful results to the user
System Workflow
Data Ingestion
Load and preprocess the Zomato dataset from Hugging Face (https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation )
Extract relevant fields such as restaurant name, location, cuisine, cost, rating, etc.
User Input
Collect user preferences:
Location (e.g., Delhi, Bangalore)
Budget (low, medium, high)
Cuisine (e.g., Italian, Chinese)
Minimum rating
Any additional preferences (e.g., family-friendly, quick service)
Integration Layer
Filter and prepare relevant restaurant data based on user input
Pass structured results into an LLM prompt
Design a prompt that helps the LLM reason and rank options
Recommendation Engine
Use the LLM to:
Rank restaurants
Provide explanations (why each recommendation fits)
Optionally summarize choices
Output Display
Present top recommendations in a user-friendly format:
Restaurant Name
Cuisine
Rating
Estimated Cost
AI-generated explanation

Diagram → 
Architecture

Phase-wise architecture: restaurant recommendation system
This document breaks the build into phases that map to the workflow in problemstatement.md: data ingestion → user input → integration (filter + prompt prep) → LLM recommendation → output display.
Phase 0 — Scope and foundations
Item
Outcome
Product slice
Basic web UI — source of user input and primary presentation of results for milestone 1 (see phase0-scope.md); CLI remains for dev/diagnostics.
Stack
Language/runtime, dependency manager, where secrets live (e.g. .env for API keys, never committed).
Dataset contract
Confirm Hugging Face dataset fields you will support in v1; document column → internal field mapping.
Non-goals
Explicitly defer (e.g. user accounts, live Zomato API, maps) to avoid scope creep.

Exit criteria: written assumptions (stack, v1 UI, supported preference fields) and a local way to run the app end-to-end once later phases exist.
Implemented artifacts: package src/milestone1/phase0/ (paths, scope, info/doctor commands), phase0-scope.md, dataset-contract.md, repo README.md, .env.example. CLI: milestone1 info / milestone1 doctor.

Phase 1 — Data ingestion and canonical model
Layer
Responsibility
Acquisition
Download or stream ManikaSaini/zomato-restaurant-recommendation; cache locally if useful for iteration.
Normalization
Clean types (ratings as numbers, cost as enum or numeric band), handle missing values, dedupe rows if needed.
Canonical schema
Internal Restaurant (or equivalent) with: name, location, cuisines, cost, rating, plus any extra columns you keep for prompts.

Exit criteria: a single module (or package) that loads data and returns a typed in-memory collection or queryable table; unit tests on parsing for a few sample rows.
Implemented: package src/milestone1/phase1_ingestion/ (Restaurant, load_restaurants / iter_restaurants, normalization, Hub revision pin, schema assertion). CLI: milestone1 ingest-smoke --limit N. Hub integration tests: RUN_HF_INTEGRATION=1 pytest -m integration.

Phase 2 — User preferences and validation
Component
Responsibility
Preference model
Structured fields: location, budget band, cuisine(s), minimum rating; optional free-text for “additional preferences.”
Validation
Reject or coerce invalid input (unknown location, rating out of range); clear error messages for the UI/CLI.

Exit criteria: preferences deserialize from form/API/CLI args into one object used by the filter layer; validation errors are user-visible.
Implemented: package src/milestone1/phase2_preferences/ (UserPreferences, preferences_from_mapping, optional allowed_city_names corpus check, allowed_cities_from_restaurants). CLI: milestone1 prefs-parse ... (prints JSON or field errors on stderr).

Phase 3 — Integration layer (retrieval + prompt assembly)
Component
Responsibility
Deterministic filter
Apply hard filters first: location, min rating, budget, cuisine overlap—reduce to top N candidates (cap for LLM context, e.g. 15–50).
Ranking hint (optional)
Pre-sort by rating or composite score so the LLM sees a sensible default order even before reasoning.
Prompt builder
System + user messages (or single structured prompt) including: user preferences as JSON or bullets; candidate table as markdown/JSON; instructions to only recommend from the list; output format (see Phase 4).

Exit criteria: given preferences + loaded dataset, produce a stable (candidates[], prompt_payload) without calling the LLM yet; tests for filter edge cases (no matches, too many matches).
Implemented: package src/milestone1/phase3_integration/ (filter_and_rank, build_prompt_payload, build_integration_output). CLI: milestone1 prompt-build.

Phase 4 — Recommendation engine (LLM)
Concern
Approach
Model I/O
Thin client: temperature, max tokens, timeout; inject API key from environment.
Grounding
Prompt requires the model to cite restaurant names from the candidate list only; refuse or return empty if nothing fits.
Structured output
Ask for JSON (e.g. rankings[] with restaurant_id, rank, explanation) or strict markdown sections—then parse and validate.
Resilience
Retry on transient errors; fallback: return deterministic top-k with template explanations if the LLM fails.

Exit criteria: end-to-end call returns ranked items with explanations; parser validates structure; failures degrade gracefully.
Implemented: package src/milestone1/phase4_llm/ (Groq OpenAI-compatible client, JSON rankings parse, deterministic fallback, recommend_with_groq). CLI: milestone1 recommend. Secrets: GROQ_API_KEY (see .env.example).

Phase 5 — Output and experience
Surface
Responsibility
Rendering
For each recommendation: name, cuisine, rating, estimated cost, AI explanation (per problem statement).
Empty states
“No restaurants match filters” vs “LLM could not justify picks”—different copy.
Observability (light)
Log latency, token usage if available, and filter counts (no PII in logs unless required).

Exit criteria: demo path from user input to readable results in one run; copy and layout match the minimum fields in the problem statement.
Implemented: package src/milestone1/phase5_output/ (markdown/plain rendering, empty-state copy, stderr telemetry JSON). CLI: milestone1 recommend-run (end-to-end readable output + telemetry).

Phase 6 — Backend (HTTP API)
Concern
Approach
Role
Thin HTTP service that owns server-side secrets (GROQ_API_KEY), dataset access, and orchestration. The browser must not call Groq or Hugging Face directly.
Contract
Stable JSON request/response for “recommend”: preferences body aligned with Phase 2 keys; response carries ranked items (ids + display fields + explanations), source (llm / fallback / no_candidates), filter/candidate counts, and optional non-sensitive telemetry fields for the UI.
Endpoints (v1 intent)
POST /api/v1/recommendations (or equivalent) — validate input, run load_restaurants (with limits/caching policy), recommend_with_groq, return DTOs. GET /health — process up, keys configured (without exposing values). Optional: GET /api/v1/meta — e.g. sample allowed_cities cap for form hints.
Cross-cutting
Timeouts aligned with Phase 4; structured server logs (counts, latency, token totals—no raw user notes in info-level logs unless you explicitly choose to); CORS restricted to the dev frontend origin; request size limits on free-text fields (reuse Phase 2 max length).
Stack
Python-first is natural: e.g. FastAPI or Flask in src/ or a sibling package, sharing the installed milestone1 library. Alternative stacks (Node, etc.) are possible only if they duplicate contracts and call a Python sidecar—avoid unless required.

Exit criteria: frontend can complete one recommendation flow using only the API; API returns the same logical outcomes as milestone1 recommend / recommend-run for the same inputs (modulo caching).
Implemented: pending — document target layout here when added (e.g. src/milestone1/api/ or apps/api/).

Phase 7 — Frontend (web UI)
Concern
Approach
Role
Primary user-facing surface: preference form + results list, per phase0-scope.md.
Data flow
Browser only talks to the Phase 6 API. Map form fields to the API JSON schema (location, budget band, cuisines, minimum rating, optional additional text).
UI
Results show name, cuisines, rating, estimated cost, AI explanation for each row; reuse Phase 5 empty-state semantics (“no filter match” vs “model returned no grounded picks”) with clear, distinct copy.
UX
Loading states, validation errors inline, disabled submit while pending; optional “copy as Markdown” for demo.
Stack
Choose one and stay consistent: e.g. React + Vite (SPA) or HTMX + server templates (minimal JS). Host locally for milestone 1; no production SLA required in Phase 0.

Exit criteria: one demo path in the README: start API + UI, submit preferences, see ranked results or an intentional empty state.
Implemented: pending — e.g. apps/web/ or frontend/ + README section “Run the web app”.

Phase 8 — Hardening and handoff (optional but recommended)
Automated tests for filters, prompt shape, JSON parsing (fixtures with fake LLM responses), and API contract tests (golden JSON for happy/empty/error paths).
README: install, set GROQ_API_KEY, run API + UI, CLI fallbacks, and limitations (dataset revision, rate limits, candidate cap).
Cost/latency notes: candidate cap, model id, when to raise load limits, caching strategy for repeated queries (optional in-process LRU of recent Hub windows—only if measured need).


STEPS
STEP 1 → Created a doc folder inside which we added a problemstatement.md 
STEP 2 → Generating the architecture 
STEP 3 → Generating the edge cases 

Prompts
Prompt 1 → Write @docs/problemstatement.md in better way  

Prompt 2 → Create a phase wise architecture for this @docs/problemstatement.md  

Prompt 3 → Generate the detailed edge cases for this project using @docs/problemstatement.md and @docs/phased-architecture.md 

Prompt 4 → Implement phase0 as per the @docs/phased-architecture.md  

Prompt 5 → In phase0 we can update that basic web UI will be the source of input

Prompt 6 → Implement phase1 in the separate folder as per the @docs/phased-architecture.md  

Prompt 7 → run phase1 so that data is downloaded  

Prompt 8 → Implement phase2 in the separate folder as per the @docs/phased-architecture.md 

Prompt 9 → Implement phase3 as per the @docs/phased-architecture.md in the seperate folder

Prompt 10 → Implement phase4 as per the @docs/phased-architecture.md in the seperate folder, LLM used in this phase will be Groq.  

STEPs for creating API KEY on GROQ → 
Create account on Groq https://groq.com/ 
Created an API KEY on https://console.groq.com/keys
Add API key in ENV file 

Create an .env file YOURSELF 
GROK_API_KEY = <api-key> 

Prompt 11 → Test phase4 will a live example like this below - Input is Bellandur, Budget is 2000, rating is 4.0 
Get the top5 restaurants from the LLM

Prompt 12 → Run the above command and tell me exact output from LLM  

Prompt 13 → Update the architecture after phase5 so that proper backend and frontend we have for this project 

Prompt 14 → Implement phase6 as per the @docs/phased-architecture.md  


OTHER AI TOOLS
(If limits are exhausted) 
Google Antigravity 
Windsurf 
Qoder 
