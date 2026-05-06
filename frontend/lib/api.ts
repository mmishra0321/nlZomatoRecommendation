import type { ApiErrorResponse, RecommendationRequest, RecommendationResponse } from "@/lib/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export class ApiRequestError extends Error {
  status: number;
  payload: ApiErrorResponse | null;

  constructor(message: string, status: number, payload: ApiErrorResponse | null) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

export async function fetchRecommendations(
  input: RecommendationRequest,
): Promise<RecommendationResponse> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/api/v1/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
      cache: "no-store",
    });
  } catch (error) {
    throw new ApiRequestError(
      "Unable to reach the recommendation API. Check backend status and NEXT_PUBLIC_API_BASE_URL.",
      0,
      null,
    );
  }

  if (!res.ok) {
    let payload: ApiErrorResponse | null = null;
    try {
      payload = (await res.json()) as ApiErrorResponse;
    } catch {
      payload = null;
    }
    throw new ApiRequestError(`API request failed with status ${res.status}`, res.status, payload);
  }

  return (await res.json()) as RecommendationResponse;
}
