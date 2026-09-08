// TrafficVision AI - Frontend API Client

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface TrafficRoad {
  road_id: string;
  name: string;
  vehicle_count: number;
  density: number;
  congestion_level: "Low" | "Medium" | "High" | string;
  updated_at: string;
}

export interface DensityMetrics {
  average_density: number;
  total_roads: number;
  congested_roads: number;
  timestamp: string;
}

export interface PredictionResult {
  road_id: string;
  road_name?: string;
  predicted_level: "Low" | "Medium" | "High" | string;
  confidence: number;
  current_density: number;
  time_of_day: number;
  generated_by: string;
}

export interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  role: "admin" | "operator" | "public" | string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: string;
}

export const tokenStorage = {
  getToken: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("tv_access_token");
  },
  setTokens: (accessToken: string, refreshToken?: string) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("tv_access_token", accessToken);
    if (refreshToken) {
      localStorage.setItem("tv_refresh_token", refreshToken);
    }
  },
  getUser: (): UserProfile | null => {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem("tv_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser: (user: UserProfile) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("tv_user", JSON.stringify(user));
  },
  clear: () => {
    if (typeof window === "undefined") return;
    localStorage.removeItem("tv_access_token");
    localStorage.removeItem("tv_refresh_token");
    localStorage.removeItem("tv_user");
  }
};

async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = tokenStorage.getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return res.json() as Promise<T>;
}

export const api = {
  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    return apiFetch<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  async register(name: string, email: string, password: string, role: string = "public"): Promise<UserProfile> {
    return apiFetch<UserProfile>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password, role }),
    });
  },

  async getMe(): Promise<UserProfile> {
    return apiFetch<UserProfile>("/auth/me");
  },

  async getUsers(): Promise<UserProfile[]> {
    return apiFetch<UserProfile[]>("/auth/users");
  },

  // Traffic
  async getLiveTraffic(): Promise<TrafficRoad[]> {
    return apiFetch<TrafficRoad[]>("/traffic/live");
  },

  async getDensityMetrics(): Promise<DensityMetrics> {
    return apiFetch<DensityMetrics>("/traffic/density");
  },

  async getRoadDetail(roadId: string): Promise<any> {
    return apiFetch<any>(`/traffic/road/${roadId}`);
  },

  // AI Prediction
  async getPrediction(roadId: string): Promise<PredictionResult> {
    return apiFetch<PredictionResult>(`/predict/congestion?road_id=${roadId}`);
  },

  async getLivePredictions(): Promise<{ total_records: number; predictions: PredictionResult[] }> {
    return apiFetch<{ total_records: number; predictions: PredictionResult[] }>("/predict/live");
  },
};
