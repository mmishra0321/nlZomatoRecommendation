# Deploy frontend on Vercel

This frontend is a Next.js app in `frontend/` and uses a server-side API proxy at `/api/recommendations`.

## Setup in Vercel

1. In Vercel, click **Add New Project** and import this repository.
2. Configure project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Install Command:** `npm ci`
   - **Build Command:** `npm run build`
3. Add environment variable:
   - `BACKEND_API_BASE_URL=https://<your-railway-backend-domain>`
4. Deploy.

## Why this config

- Browser requests stay same-origin (`/api/recommendations`) on Vercel.
- The API route (`frontend/app/api/recommendations/route.ts`) forwards requests to Railway.
- In production, if `BACKEND_API_BASE_URL` is missing, the API route returns a clear configuration error instead of silently using localhost.

## Verify

1. Open the Vercel frontend URL.
2. Submit a recommendation query.
3. If you get backend errors, verify:
   - Railway API is up (`/health`).
   - `BACKEND_API_BASE_URL` in Vercel points to the correct Railway URL.
