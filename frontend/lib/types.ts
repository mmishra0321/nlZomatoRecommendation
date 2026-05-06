export type Source = "llm" | "fallback" | "no_candidates";
export type EmptyStateCode = "ok" | "no_filter_match" | "degraded_model";

export type RecommendationRequest = {
  location: string;
  minimum_rating: number;
  budget?: string | number;
  cuisines?: string[];
  additional_preferences?: string;
  top_n?: number;
  dataset_limit?: number;
  candidate_cap?: number;
  split?: string;
};

export type RecommendationItem = {
  rank: number;
  restaurant_id: string;
  name: string;
  cuisines: string[];
  rating: number;
  cost_for_two: number | null;
  explanation: string;
};

export type RecommendationResponse = {
  source: Source;
  items: RecommendationItem[];
  user_message: string;
  detail: string | null;
  empty_state_code: EmptyStateCode;
  telemetry: {
    latency_ms?: number | null;
    matched_count: number;
    capped_count: number;
    candidate_cap: number;
    [key: string]: unknown;
  };
  parse_error?: string | null;
  http_error?: string | null;
};

export type ApiErrorResponse = {
  detail?: {
    errors?: Record<string, string>;
    message?: string;
  } | string;
};
