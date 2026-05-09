# Phase 7 — Next.js Frontend

This app implements Phase 7 from `phased-architecture.md` using Next.js App Router and consumes only the Phase 6 backend API.

## Prerequisites

- Node.js 20+
- Phase 6 backend running at `http://127.0.0.1:8000` (or update env below)

## Setup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment

- `NEXT_PUBLIC_API_BASE_URL` — not used by the current client (calls `/api/recommendations` proxy); keep for reference if you extend the client.
- `BACKEND_API_BASE_URL` — where the Next.js API route proxies `POST /api/recommendations` (local backend URL for development).

## UI behavior mapped to architecture

- Form fields map to Phase 6 request: `location`, `budget`, `cuisines`, `minimum_rating`, `additional_preferences`, `top_n`
- Handles `422` field validation errors and network/timeout failures separately
- Renders Phase 5 response fields: `items[]`, `source`, `user_message`, `detail`, `empty_state_code`, `telemetry`
- Uses banner variants for `ok` / `no_filter_match` / `degraded_model`
