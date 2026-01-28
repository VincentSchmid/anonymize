/**
 * Typed API client for the anonymization backend.
 */

const API_BASE_URL = "http://127.0.0.1:14200";

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
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API error (${response.status}): ${error}`);
    }

    return response.json();
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
