const API_CONFIG = {
  baseURL: "http://127.0.0.1:8000/api/v1",
  timeoutMs: 12000,
  defaultHeaders: {
    "Content-Type": "application/json",
  },
};

class AuthManager {
  constructor( storage = typeof window !== "undefined" ? window.localStorage : null ) {
    this.storage = storage;
  }

  getToken() {
    if (!this.storage) return null;
    return (
      this.storage.getItem("auth_token") ||
      this.storage.getItem("token") ||
      null
    );
  }

  setToken(token) {
    if (!this.storage) return;
    if (token) {
      this.storage.setItem("auth_token", token);
      return;
    }
    this.clear();
  }

  clear() {
    if (!this.storage) return;
    this.storage.removeItem("auth_token");
    this.storage.removeItem("token");
    this.storage.removeItem("refresh_token");
    this.storage.removeItem("role");
    this.storage.removeItem("user_name");
  }

  isAuthenticated() {
    return Boolean(this.getToken());
  }

  applyAuthHeaders(headers = {}) {
    const token = this.getToken();
    if (!token) return headers;
    return {
      ...headers,
      Authorization: `Bearer ${token}`,
    };
  }

  async refreshToken() {
    return this.getToken();
  }

  // Saves everything returned by a successful login (token, refresh token,
  // role, name) into storage in one go.
  setSession({ access_token, refresh_token, role, name } = {}) {
    this.setToken(access_token);
    if (!this.storage) return;
    if (refresh_token) this.storage.setItem("refresh_token", refresh_token);
    if (role) this.storage.setItem("role", String(role).toUpperCase());
    if (name) this.storage.setItem("user_name", name);
  }

  // Maps a user role to the dashboard page they should land on after login.
  static getDashboardUrl(role) {
    const map = {
      ADMIN: "Admin dashboard.html",
      OPERATOR: "operator dashboard.html",
      TRAFFIC_OPERATOR: "operator dashboard.html",
      PUBLIC: "public dashboard.html",
      USER: "public dashboard.html",
    };
    return map[String(role || "").toUpperCase()] || "public dashboard.html";
  }

  // Reads the saved role back out of storage.
  static getRole() {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem("role");
  }

  // Reads the saved display name back out of storage.
  static getUserName() {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem("user_name");
  }

  // Call at the top of any protected page. Sends the visitor back to
  // Login.html if they have no token, or if their role isn't in
  // allowedRoles (when a list is given).
  static guardPage(allowedRoles = null) {
    if (typeof window === "undefined") return;
    const hasToken = Boolean(
      window.localStorage.getItem("auth_token") ||
        window.localStorage.getItem("token")
    );
    const role = (AuthManager.getRole() || "").toUpperCase();

    if (!hasToken) {
      window.location.href = "Login.html";
      return;
    }

    if (Array.isArray(allowedRoles) && allowedRoles.length > 0) {
      const normalized = allowedRoles.map((r) => String(r).toUpperCase());
      if (!normalized.includes(role)) {
        window.location.href = "Login.html";
      }
    }
  }
}

const authManager = new AuthManager();

function createApiError(message, status = null, payload = null) {
  const error = new Error(message);
  error.status = status;
  error.payload = payload;
  return error;
}

function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    searchParams.append(key, String(value));
  });

  return searchParams.toString();
}

async function apiFetch(endpoint, options = {}) {
  const baseUrl = endpoint.startsWith("http")
    ? endpoint
    : `${API_CONFIG.baseURL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  const controller = new AbortController();
  const timeoutMs = options.timeout ?? API_CONFIG.timeoutMs;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const headers = authManager.applyAuthHeaders({
    ...API_CONFIG.defaultHeaders,
    ...(options.headers || {}),
  });

  try {
    const response = await fetch(baseUrl, {
      ...options,
      headers,
      signal: controller.signal,
    });

    const text = await response.text();

    let payload = null;

    if (text) {
      try {
        payload = JSON.parse(text);
      } catch {
        payload = text;
      }
    }

    if (!response.ok) {
      const detail =
        payload && typeof payload === "object"
          ? payload.detail || payload.message || payload.error
          : null;

      const message =
        typeof detail === "string"
          ? detail
          : `Request failed (${response.status})`;

      if (response.status === 401 || response.status === 403) {
        authManager.clear();
      }

      throw createApiError(message, response.status, payload);
    }

    return payload;

  } catch (error) {

    if (error?.name === "AbortError") {
      throw createApiError(
        "Backend request timed out. Make sure the TrafficVision backend is running.",
        408,
        null
      );
    }

    if (error?.status) {
      throw error;
    }

    console.error("[API NETWORK ERROR]", error);

    throw createApiError(
      `Cannot connect to backend at ${API_CONFIG.baseURL}. Make sure Uvicorn is running.`,
      503,
      null
    );

  } finally {
    clearTimeout(timer);
  }
}

function normalizeCongestionLevel(value) {
  const raw = String(value || "")
    .trim()
    .toLowerCase();
  if (!raw) return "Low";
  if (raw.includes("severe")) return "Severe";
  if (raw.includes("high")) return "High";
  if (raw.includes("medium") || raw.includes("med")) return "Medium";
  return "Low";
}

function getCongestionBadgeClass(level) {
  const normalized = normalizeCongestionLevel(level);
  const map = {
    Low: "badge-success",
    Medium: "badge-warning",
    High: "badge-danger",
    Severe: "badge-danger",
  };
  return map[normalized] || "badge-secondary";
}

function getCongestionLabel(value) {
  return normalizeCongestionLevel(value);
}

const authAPI = {
  async login(email, password) {
    if (!email || !password) {
      throw createApiError("Email and password are required", 400, null);
    }

    const response = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
      }),
    });

    if (!response || typeof response !== "object") {
      throw createApiError("Malformed login response", 502, response);
    }

    // Store access token
    if (response.access_token) {
      authManager.setToken(response.access_token);
    }

    // Preserve refresh token if backend provides one
    if (response.refresh_token) {
      localStorage.setItem("refresh_token", response.refresh_token);
    }

    // Preserve role/user information if provided
    if (response.role) {
      localStorage.setItem("role", String(response.role).toUpperCase());
    }

    if (response.name) {
      localStorage.setItem("user_name", response.name);
    }

    return response;
  },

  async register(name, email, password, role = "user") {
    let backendRole = String(role || "user").toLowerCase();

    if (backendRole === "public") {
      backendRole = "user";
    } else if (backendRole === "traffic_operator") {
      backendRole = "operator";
    }

    const response = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name,
        email,
        password,
        role: backendRole,
      }),
    });

    if (!response || typeof response !== "object") {
      throw createApiError("Malformed registration response", 502, response);
    }

    return response;
  },

  async getProfile() {
    const response = await apiFetch("/auth/me");

    if (!response || typeof response !== "object") {
      throw createApiError("Malformed profile response", 502, response);
    }

    return response;
  },

  async refresh() {
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
      throw createApiError("Refresh token not available", 401, null);
    }

    const response = await apiFetch("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (response?.access_token) {
      authManager.setToken(response.access_token);
    }

    if (response?.refresh_token) {
      localStorage.setItem("refresh_token", response.refresh_token);
    }

    return response;
  },

  logout() {
    authManager.clear();
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    localStorage.removeItem("user_name");
  },
};

const trafficAPI = {
  async getLiveTraffic() {
    const response = await apiFetch("/traffic/live");
    if (!Array.isArray(response)) {
      throw createApiError("Malformed traffic response", 502, response);
    }
    return response;
  },

  async getDensitySummary() {
    const response = await apiFetch("/traffic/density");
    if (!response || typeof response !== "object") {
      throw createApiError("Malformed density response", 502, response);
    }
    return response;
  },

  async getRoadTraffic(roadId) {
    if (!roadId) {
      throw createApiError("roadId is required", 400, null);
    }

    try {
      const response = await apiFetch(
        `/traffic/road/${encodeURIComponent(String(roadId))}`
      );
      if (!response || typeof response !== "object") {
        throw createApiError(
          "Malformed response: expected an object",
          502,
          response
        );
      }
      return response;
    } catch (error) {
      if (error && error.status === 404) {
        throw createApiError(`Road ${roadId} not found`, 404, null);
      }
      throw error;
    }
  },
};

const predictionAPI = {
  async predictCongestion({ road_id, vehicle_count, average_speed, timestamp, } = {}) {
    if (!road_id) {
      throw createApiError("road_id is required", 400, null);
    }

    const query = buildQueryString({
      road_id,
      vehicle_count,
      average_speed,
      timestamp,
    });

    const response = await apiFetch(`/predict/congestion?${query}`);
    if (!response || typeof response !== "object") {
      throw createApiError(
        "Malformed response: expected an object",
        502,
        response
      );
    }
    return response;
  },

  async getPeakHours(roadId) {
    if (!roadId) {
      throw createApiError("road_id is required", 400, null);
    }

    const query = buildQueryString({ road_id: roadId });
    const response = await apiFetch(`/predict/peak-hours?${query}`);
    if (!response || typeof response !== "object") {
      throw createApiError(
        "Malformed response: expected an object",
        502,
        response
      );
    }
    return response;
  },

  async predictDelay({ road_id, distance_km, vehicle_count, average_speed, timestamp, } = {}) {
    if (!road_id) {
      throw createApiError("road_id is required", 400, null);
    }

    const query = buildQueryString({
      road_id,
      distance_km,
      vehicle_count,
      average_speed,
      timestamp,
    });

    const response = await apiFetch(`/predict/delay?${query}`);
    if (!response || typeof response !== "object") {
      throw createApiError(
        "Malformed response: expected an object",
        502,
        response
      );
    }
    return response;
  },
};

const routeAPI = {
  async rankRoutes(routes) {
    if (!Array.isArray(routes) || routes.length === 0) {
      return [];
    }

    const payload = {
      routes: routes.map((route) => ({
        route_id: route.route_id,
        distance_km: route.distance_km,
        roads: Array.isArray(route.roads) ? route.roads : [],
        base_duration_minutes: route.base_duration_minutes ?? null,
      })),
    };

    const response = await apiFetch("/route/rank", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (!Array.isArray(response)) {
      throw createApiError(
        "Malformed response: expected an array",
        502,
        response
      );
    }

    return response;
  },
};

/* Compatibility facade for the existing HTML screens.  Every value below is
 * obtained from a supported API response; no traffic or prediction fallback is
 * manufactured in the browser. */
const predictAPI = {
  getCongestion(roadId) {
    return predictionAPI.predictCongestion({ road_id: roadId });
  },

  async getPeakHourPrediction(roadId) {
    const result = await predictionAPI.getPeakHours(roadId);
    return { ...result, peak_hours: result.peak_windows || [] };
  },

  async getAllDelayEstimates() {
    const roads = await trafficAPI.getLiveTraffic();
    return Promise.all(roads.map(async (road) => {
      const result = await predictionAPI.predictDelay({
        road_id: road.road_id,
        distance_km: 1,
        vehicle_count: road.vehicle_count,
        average_speed: road.avg_speed_kmph,
        timestamp: road.updated_at,
      });
      return { ...result, road_name: road.road_name, delay_minutes: result.estimated_delay_minutes };
    }));
  },

  async getAllRoadForecasts() {
    const roads = await trafficAPI.getLiveTraffic();
    return Promise.all(roads.map(async (road) => {
      const forecast = await predictionAPI.predictCongestion({
        road_id: road.road_id,
        vehicle_count: road.vehicle_count,
        average_speed: road.avg_speed_kmph,
        timestamp: road.updated_at,
      });
      return {
        ...forecast,
        road_name: road.road_name,
        current_density: road.density,
        predicted_density: forecast.density,
        predicted_speed: "—",
        trend: "Not supplied by API",
      };
    }));
  },

  async getTemporalForecast(roadId) {
    const road = await trafficAPI.getRoadTraffic(roadId);
    const forecast = await predictionAPI.predictCongestion({ road_id: roadId });
    return {
      ...forecast,
      road_name: road.road_name,
      current_density: road.density,
      predicted_density: forecast.density,
      predicted_speed: "—",
      trend: "Not supplied by API",
    };
  },

  async downloadPredictionReport(format = "csv") {
    const forecasts = await this.getAllRoadForecasts();
    if (!forecasts.length) throw createApiError("No prediction data is available for export", 404, null);
    const fields = ["road_id", "road_name", "predicted_level", "confidence", "model_version", "observed_at", "current_density", "predicted_density"];
    const type = format === "json" ? "application/json" : "text/csv";
    const content = format === "json"
      ? JSON.stringify(forecasts, null, 2)
      : [fields.join(","), ...forecasts.map((row) => fields.map((field) => JSON.stringify(row[field] ?? "")).join(","))].join("\n");
    const filename = `trafficvision-predictions-${new Date().toISOString().slice(0, 10)}.${format === "json" ? "json" : "csv"}`;
    const url = URL.createObjectURL(new Blob([content], { type }));
    const link = document.createElement("a");
    link.href = url; link.download = filename; link.click();
    URL.revokeObjectURL(url);
    return { filename, count: forecasts.length };
  },
};

// There is no operator-management route in the verified backend.  This keeps
// the legacy admin screen from throwing ReferenceError while ensuring a write
// is never represented as successful.
const operatorAPI = {
  getOperators() { return []; },
  async addOperator() { throw createApiError("Operator management is not available from the connected backend", 501, null); },
  async removeOperator() { throw createApiError("Operator management is not available from the connected backend", 501, null); },
};

function logout() {
  authAPI.logout();
  if (typeof window !== "undefined") window.location.href = "Login.html";
}

if (typeof window !== "undefined") {
  window.API_CONFIG = API_CONFIG;
  window.AuthManager = AuthManager;
  window.authManager = authManager;
  window.apiFetch = apiFetch;
  window.trafficAPI = trafficAPI;
  window.predictionAPI = predictionAPI;
  window.routeAPI = routeAPI;
  window.predictAPI = predictAPI;
  window.operatorAPI = operatorAPI;
  window.authAPI = authAPI;
  window.logout = logout;
  window.getCongestionBadgeClass = getCongestionBadgeClass;
  window.getCongestionLabel = getCongestionLabel;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    API_CONFIG,
    AuthManager,
    authManager,
    apiFetch,
    trafficAPI,
    predictionAPI,
    routeAPI,
    predictAPI,
    operatorAPI,
    getCongestionBadgeClass,
    getCongestionLabel,
  };
}
