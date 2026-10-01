const API_CONFIG = {
  baseURL: (typeof window !== "undefined" && window.TRAFFICVISION_API_BASE_URL) || "http://127.0.0.1:8001/api/v1",
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
      ADMIN: "dashboard.html",
      OPERATOR: "dashboard.html",
      TRAFFIC_OPERATOR: "dashboard.html",
      PUBLIC: "dashboard.html",
      USER: "dashboard.html",
    };
    return map[String(role || "").toUpperCase()] || "dashboard.html";
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
      window.localStorage.getItem("auth_token") || window.localStorage.getItem("token")
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

async function apiFetch(endpoint, options = {}, retryAfterRefresh = true) {
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

    const contentType = response.headers.get("content-type") || "";
    if (response.ok && (contentType.includes("text/csv") || contentType.includes("application/octet-stream"))) {
      const blob = await response.blob();
      const disposition = response.headers.get("content-disposition") || "";
      const filename = disposition.match(/filename\*?=(?:UTF-8''|\")?([^\";]+)/i)?.[1] || "traffic-report.csv";
      return { blob, filename: decodeURIComponent(filename.replace(/"/g, "")) };
    }

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
      const detail = payload && typeof payload === "object" ? (payload.detail || payload.message || payload.error) : payload;
      const message = typeof detail === "string" ? detail : `Request failed (${response.status})`;

      const isAuthEndpoint = endpoint.includes("/auth/login") || endpoint.includes("/auth/refresh") || endpoint.includes("/auth/logout");
      if (response.status === 401 && retryAfterRefresh && !isAuthEndpoint && typeof localStorage !== "undefined" && localStorage.getItem("refresh_token")) {
        try {
          const refreshed = await apiFetch("/auth/refresh", {
            method: "POST",
            body: JSON.stringify({ refresh_token: localStorage.getItem("refresh_token") }),
          }, false);
          authManager.setToken(refreshed.access_token);
          if (refreshed.refresh_token) localStorage.setItem("refresh_token", refreshed.refresh_token);
          return await apiFetch(endpoint, options, false);
        } catch {
          authManager.clear();
          if (typeof localStorage !== "undefined") localStorage.removeItem("refresh_token");
        }
      }

      if (response.status === 401 && !isAuthEndpoint) {
        authManager.clear();
        if (typeof localStorage !== "undefined") localStorage.removeItem("refresh_token");
      }

      throw createApiError(message, response.status, payload);
    }

    return payload;
  } catch (error) {
    if (error && error.name === "AbortError") {
      throw createApiError("Request timed out", 408, null);
    }

    if (error && error.status) {
      throw error;
    }

    if (error instanceof TypeError) {
      throw createApiError(`Cannot reach the TrafficVision backend at ${API_CONFIG.baseURL}. Start the backend and try again.`, 503, null);
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
  async getCaptcha() {
    return apiFetch("/auth/captcha");
  },

  async login(email, password, challengeId, captchaResponse) {
    if (!email || !password || !challengeId || !captchaResponse) {
      throw createApiError("Email, password, and CAPTCHA are required", 400, null);
    }

    const response = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        challenge_id: challengeId,
        captcha_response: captchaResponse,
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

  async register(name, email, password, challengeId, captchaResponse, role = "user") {
    if (!challengeId || !captchaResponse) {
      throw createApiError("CAPTCHA is required", 400, null);
    }
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
        challenge_id: challengeId,
        captcha_response: captchaResponse,
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

    if (response?.refresh_token) localStorage.setItem("refresh_token", response.refresh_token);

    return response;
  },

  async logout() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      try {
        await apiFetch("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) }, false);
      } catch {
      }
    }
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
      throw createApiError("Malformed response: expected a traffic array", 502, response);
    }
    return response;
  },

  async getDensitySummary() {
    const response = await apiFetch("/traffic/density");
    if (!response || typeof response !== "object") {
      throw createApiError("Malformed response: expected a density summary", 502, response);
    }
    return response;
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

  async getHistory({ road_id, start, end, limit = 100 } = {}) {
    return apiFetch(`/traffic/history?${buildQueryString({ road_id, start, end, limit })}`);
  },

  async getAggregate({ road_id, granularity = "hour" } = {}) {
    return apiFetch(`/traffic/aggregate?${buildQueryString({ road_id, granularity })}`);
  },

  async getRoadCondition(roadId) {
    if (!roadId) throw createApiError("road_id is required", 400, null);
    return apiFetch(`/traffic/road-condition/${encodeURIComponent(String(roadId))}`);
  },
};

const dashboardAPI = {
  async getAnalytics() {
    return apiFetch("/analytics");
  },
  async getAlerts() {
    return apiFetch("/alerts");
  },
  async getRecommendations() {
    return apiFetch("/recommendations");
  },
  async getAnomalies(limit = 20) {
    return apiFetch(`/ai/anomalies?${buildQueryString({ limit })}`);
  },
  async getMyAlerts(limit = 50) {
    return apiFetch(`/alerts/my?${buildQueryString({ limit })}`);
  },
  async getActiveAlerts({ road_id, limit = 50 } = {}) {
    return apiFetch(`/alerts/active?${buildQueryString({ road_id, limit })}`);
  },
  async markAlertRead(alertId) {
    return apiFetch(`/alerts/${encodeURIComponent(String(alertId))}/read`, { method: "POST" });
  },
  async createAlert(alert) {
    return apiFetch("/alerts", { method: "POST", body: JSON.stringify(alert) });
  },
  async syncAnomalyAlerts(minimum_score = 0.3) {
    return apiFetch(`/alerts/sync-ai-anomalies?${buildQueryString({ minimum_score })}`, { method: "POST" });
  },
  async getTrends(roadId, range = "day") {
    return apiFetch(`/analytics/trends?${buildQueryString({ road_id: roadId, range })}`);
  },
  async getHeatmap(range = "day") {
    return apiFetch(`/analytics/heatmap?${buildQueryString({ range })}`);
  },
  async downloadReport(range = "week", format = "csv") {
    return apiFetch(`/analytics/reports?${buildQueryString({ range, format })}`);
  },
  async getHistoricalReport(roadId) {
    if (!roadId) throw createApiError("road_id is required", 400, null);
    return apiFetch(`/reports/historical/${encodeURIComponent(String(roadId))}`);
  },
  async getModelMetrics() {
    return apiFetch("/model/metrics");
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
  async optimizeRoute(origin, destination) {
    return apiFetch(`/route/optimize?${buildQueryString({ origin, destination })}`);
  },
  async getAlternateRoutes(origin, destination) {
    return apiFetch(`/route/alternate?${buildQueryString({ origin, destination })}`);
  },
  async getTravelTime(routeId) {
    return apiFetch(`/route/travel-time?${buildQueryString({ route_id: routeId })}`);
  },
  async getRoadConditions(roadId) {
    return apiFetch(`/route/conditions?${buildQueryString({ road_id: roadId })}`);
  },
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
  window.dashboardAPI = dashboardAPI;
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
    dashboardAPI,
    getCongestionBadgeClass,
    getCongestionLabel,
  };
}