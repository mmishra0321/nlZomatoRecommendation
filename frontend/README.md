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

- `NEXT_PUBLIC_API_BASE_URL` (use `/api/recommendations`)
- `BACKEND_API_BASE_URL` (server-side proxy target; set to your Render backend URL)

## Deploy on Vercel

1. Import this repo in Vercel and set **Root Directory** to `frontend`.
2. Keep framework preset as **Next.js**.
3. Add project environment variable:
   - `BACKEND_API_BASE_URL=https://<your-render-service>.onrender.com`
4. Deploy.

The browser talks to `/api/recommendations` on Vercel, and the Next.js API route forwards to Render.
In production, deployment fails safely if `BACKEND_API_BASE_URL` is missing.

## UI behavior mapped to architecture

- Form fields map to Phase 6 request: `location`, `budget`, `cuisines`, `minimum_rating`, `additional_preferences`, `top_n`
- Handles `422` field validation errors and network/timeout failures separately
- Renders Phase 5 response fields: `items[]`, `source`, `user_message`, `detail`, `empty_state_code`, `telemetry`
- Uses banner variants for `ok` / `no_filter_match` / `degraded_model`
