/**
 * Typed API client for the anonymization backend.
 */

const API_BASE_URL = "http://127.0.0.1:14200";
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export interface DetectedEntity {
  entity_type: string;
  text: string;
  start: number;
  end: number;
  score: number;
}

export interface AnalyzeRequest {
  text: string;
  enabled_entities?: string[];
  score_threshold?: number;
}

export interface AnalyzeResponse {
  text: string;
  entities: DetectedEntity[];
}

export interface AnonymizeRequest {
  text: string;
  enabled_entities?: string[];
  anonymization_style?: "replace" | "mask" | "hash" | "redact";
  score_threshold?: number;
}

export interface AnonymizeResponse {
  original_text: string;
  anonymized_text: string;
  entities: DetectedEntity[];
  anonymization_style: string;
}

export interface EntityInfo {
  type: string;
  description: string;
  is_swiss: boolean;
}

export interface EntitiesResponse {
  entities: EntityInfo[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  version: string;
}

export interface ConfigResponse {
  default_entities: string[];
  spacy_model: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      let response: Response;
      try {
        response = await fetch(url, {
          ...options,
          headers: {
            "Content-Type": "application/json",
            ...options.headers,
          },
        });
      } catch (e) {
        // Network-level errors (connection refused, DNS failure, etc.)
        const errorMessage = e instanceof Error ? e.message : String(e);
        lastError = new Error(
          `Network error calling ${endpoint}: ${errorMessage}. ` +
          `Please check that the backend service is running on ${this.baseUrl}`
        );

        if (attempt < MAX_RETRIES) {
          console.log(`[API] Retry ${attempt}/${MAX_RETRIES} for ${endpoint} after network error`);
          await sleep(RETRY_DELAY_MS * attempt);
          continue;
        }
        throw lastError;
      }

      if (!response.ok) {
        let errorBody = "";
        try {
          errorBody = await response.text();
        } catch {
          errorBody = "(unable to read error response)";
        }
        // Don't retry HTTP errors (4xx, 5xx) - only network failures
        throw new Error(
          `API error on ${endpoint} (HTTP ${response.status} ${response.statusText}): ${errorBody}`
        );
      }

      try {
        return await response.json();
      } catch (e) {
        throw new Error(
          `Invalid JSON response from ${endpoint}: ${e instanceof Error ? e.message : String(e)}`
        );
      }
    }

    // Should not reach here, but just in case
    throw lastError || new Error(`Request to ${endpoint} failed after ${MAX_RETRIES} retries`);
  }

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health");
  }

  async getEntities(): Promise<EntitiesResponse> {
    console.log("[API] Fetching entities from", this.baseUrl + "/entities");
    const response = await this.request<EntitiesResponse>("/entities");
    console.log("[API] Entities response:", response);
    return response;
  }

  async analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    return this.request<AnalyzeResponse>("/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async anonymize(request: AnonymizeRequest): Promise<AnonymizeResponse> {
    return this.request<AnonymizeResponse>("/anonymize", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getConfig(): Promise<ConfigResponse> {
    return this.request<ConfigResponse>("/config");
  }

  async updateConfig(
    defaultEntities: string[]
  ): Promise<ConfigResponse> {
    return this.request<ConfigResponse>("/config", {
      method: "PUT",
      body: JSON.stringify({ default_entities: defaultEntities }),
    });
  }
}

export const api = new ApiClient();
export default api;
