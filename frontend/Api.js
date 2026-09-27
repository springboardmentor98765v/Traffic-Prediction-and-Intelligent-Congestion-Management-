const API_CONFIG = {
  baseURL: "http://127.0.0.1:8001/api/v1",
  timeoutMs: 12000,
  defaultHeaders: {
    "Content-Type": "application/json",
  },
};

class AuthManager {
  constructor(storage = typeof window !== "undefined" ? window.localStorage : null) {
    this.storage = storage;
  }

  getToken() {
    if (!this.storage) return null;
    return this.storage.getItem("auth_token") || this.storage.getItem("token") || null;
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
  const baseUrl = endpoint.startsWith("http") ? endpoint : `${API_CONFIG.baseURL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
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
    const payload = text ? JSON.parse(text) : null;

    if (!response.ok) {
      const detail = payload && typeof payload === "object" ? (payload.detail || payload.message || payload.error) : null;
      const message = typeof detail === "string" ? detail : `Request failed (${response.status})`;

      if (response.status === 401 || response.status === 403) {
        authManager.clear();
      }

      throw createApiError(message, response.status, payload);
    }

    return payload;
  } catch (error) {
    if (error && error.name === "AbortError") {
      throw createApiError("Request timed out", 408, null);
    }

    if (error instanceof SyntaxError) {
      throw createApiError("Malformed backend response", 502, null);
    }

    if (error && error.status) {
      throw error;
    }

    if (error && error.message) {
      throw createApiError(error.message, null, null);
    }

    throw createApiError("Backend unavailable", 503, null);
  } finally {
    clearTimeout(timer);
  }
}

function normalizeCongestionLevel(value) {
  const raw = String(value || "").trim().toLowerCase();
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
      throw createApiError(
        "Malformed login response",
        502,
        response
      );
    }

    // Store access token
    if (response.access_token) {
      authManager.setToken(response.access_token);
    }

    // Preserve refresh token if backend provides one
    if (response.refresh_token) {
      localStorage.setItem(
        "refresh_token",
        response.refresh_token
      );
    }

    // Preserve role/user information if provided
    if (response.role) {
      localStorage.setItem(
        "role",
        String(response.role).toUpperCase()
      );
    }

    if (response.name) {
      localStorage.setItem(
        "user_name",
        response.name
      );
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
      throw createApiError(
        "Malformed registration response",
        502,
        response
      );
    }

    return response;
  },

  async getProfile() {
    const response = await apiFetch("/auth/me");

    if (!response || typeof response !== "object") {
      throw createApiError(
        "Malformed profile response",
        502,
        response
      );
    }

    return response;
  },

  async refresh() {
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
      throw createApiError(
        "Refresh token not available",
        401,
        null
      );
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
      localStorage.setItem(
        "refresh_token",
        response.refresh_token
      );
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
    try {
      const response = await apiFetch("/traffic/live");
      if (!Array.isArray(response)) {
        throw createApiError("Malformed response: expected an array", 502, response);
      }
      return response;
    } catch (error) {
      if (error && error.status === 404) {
        return [];
      }
      return [];
    }
  },

  async getDensitySummary() {
    try {
      const response = await apiFetch("/traffic/density");
      if (!response || typeof response !== "object") {
        throw createApiError("Malformed response: expected an object", 502, response);
      }
      return response;
    } catch (error) {
      return {
        total_roads: 0,
        total_roads_monitored: 0,
        total_vehicle_count: 0,
        average_density: 0,
        average_network_density: 0,
        maximum_density: 0,
        minimum_density: 0,
        high_congestion_roads: 0,
        severe_congestion_roads: 0,
        congested_segments: 0,
        timestamp: new Date().toISOString(),
      };
    }
  },

  async getRoadTraffic(roadId) {
    if (!roadId) {
      throw createApiError("roadId is required", 400, null);
    }

    try {
      const response = await apiFetch(`/traffic/road/${encodeURIComponent(String(roadId))}`);
      if (!response || typeof response !== "object") {
        throw createApiError("Malformed response: expected an object", 502, response);
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
  async predictCongestion({ road_id, vehicle_count, average_speed, timestamp } = {}) {
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
      throw createApiError("Malformed response: expected an object", 502, response);
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
      throw createApiError("Malformed response: expected an object", 502, response);
    }
    return response;
  },

  async predictDelay({ road_id, distance_km, vehicle_count, average_speed, timestamp } = {}) {
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
      throw createApiError("Malformed response: expected an object", 502, response);
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
      throw createApiError("Malformed response: expected an array", 502, response);
    }

    return response;
  },
};

if (typeof window !== "undefined") {
  window.API_CONFIG = API_CONFIG;
  window.AuthManager = AuthManager;
  window.authManager = authManager;
  window.apiFetch = apiFetch;
  window.trafficAPI = trafficAPI;
  window.predictionAPI = predictionAPI;
  window.routeAPI = routeAPI;
  window.authAPI = authAPI;
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
    getCongestionBadgeClass,
    getCongestionLabel,
  };
}
