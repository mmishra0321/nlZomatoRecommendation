import { NextRequest, NextResponse } from "next/server";

function resolveBackendBaseUrl(): string | null {
  const configured = process.env.BACKEND_API_BASE_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }
  if (process.env.NODE_ENV === "production") {
    return null;
  }
  return "http://127.0.0.1:8000";
}

export async function POST(request: NextRequest) {
  const backendBaseUrl = resolveBackendBaseUrl();
  if (!backendBaseUrl) {
    return NextResponse.json(
      {
        detail: {
          message:
            "Server misconfiguration: BACKEND_API_BASE_URL is required in production.",
        },
      },
      { status: 500 },
    );
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ detail: { message: "Invalid JSON body." } }, { status: 400 });
  }

  let response: Response;
  try {
    response = await fetch(`${backendBaseUrl}/api/v1/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { detail: { message: "Backend API is unreachable." } },
      { status: 503 },
    );
  }

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  return NextResponse.json(body ?? {}, { status: response.status });
}
