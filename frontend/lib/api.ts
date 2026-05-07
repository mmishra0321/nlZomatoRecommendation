import type { ApiErrorResponse, RecommendationRequest, RecommendationResponse } from "@/lib/types";

const API_PATH = "/api/recommendations";

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
    res = await fetch(API_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
      cache: "no-store",
    });
  } catch (error) {
    throw new ApiRequestError("Unable to reach the local frontend API route.", 0, null);
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
