/**
 * TrafficVision AI - Centralized API Client & Frontend Utilities
 * Supports live backend communication with automatic fallback aligned with Day 6 Traffic Monitoring specs.
 */

// Local development (Live Server, file://) talks to the Docker Compose ports; the hosted
// site talks to the Render services (DEF-M4-005). If Render gave a service a different
// subdomain, change it in PRODUCTION_URLS below, or set window.__TRAFFICVISION_CONFIG__
// = { GATEWAY_URL, ANALYTICS_URL, AI_ENGINE_URL } in a script loaded before api.js.
const INJECTED_CONFIG = window.__TRAFFICVISION_CONFIG__ || {};
const PRODUCTION_URLS = {
  BACKEND: INJECTED_CONFIG.GATEWAY_URL || 'https://tv-team1-backend.onrender.com',
  ANALYTICS: INJECTED_CONFIG.ANALYTICS_URL || 'https://tv-team1-analytics.onrender.com',
  AI_ENGINE: INJECTED_CONFIG.AI_ENGINE_URL || 'https://tv-team1-ai.onrender.com',
};

const IS_LOCAL_FRONTEND = ['', 'localhost', '127.0.0.1'].includes(window.location.hostname);

const API_CONFIG = IS_LOCAL_FRONTEND
  ? {
      BASE_URL: 'http://127.0.0.1:8000/api/v1',
      ANALYTICS_BASE: 'http://127.0.0.1:8001',
      AI_ENGINE_BASE: 'http://127.0.0.1:8010',
      TIMEOUT: 10000,
    }
  : {
      BASE_URL: `${PRODUCTION_URLS.BACKEND}/api/v1`,
      ANALYTICS_BASE: PRODUCTION_URLS.ANALYTICS,
      AI_ENGINE_BASE: PRODUCTION_URLS.AI_ENGINE,
      // Free-tier services sleep when idle; the first call can take ~60 s to wake them.
      TIMEOUT: 60000,
    };

// ==========================================
// Mock Fallback Data (Day 6 Schema Aligned)
// ==========================================
const MOCK_TRAFFIC_DATA = [
  {
    road_id: 'R001',
    road_name: 'Main Expressway',
    vehicle_count: 28,
    density: 5.6,
    avg_speed_kmph: 55.0,
    speed: '55 km/h',
    congestion_level: 'Low',
    updated_at: new Date().toISOString(),
  },
  {
    road_id: 'R002',
    road_name: 'Central Avenue',
    vehicle_count: 27,
    density: 6.75,
    avg_speed_kmph: 42.0,
    speed: '42 km/h',
    congestion_level: 'Low',
    updated_at: new Date().toISOString(),
  },
  {
    road_id: 'R003',
    road_name: 'West Ring Road',
    vehicle_count: 26,
    density: 7.43,
    avg_speed_kmph: 48.0,
    speed: '48 km/h',
    congestion_level: 'Low',
    updated_at: new Date().toISOString(),
  },
  {
    road_id: 'R004',
    road_name: 'North Boulevard',
    vehicle_count: 1,
    density: 0.22,
    avg_speed_kmph: 60.0,
    speed: '60 km/h',
    congestion_level: 'Low',
    updated_at: new Date().toISOString(),
  },
  {
    road_id: 'R005',
    road_name: 'Industrial Highway',
    vehicle_count: 34,
    density: 11.33,
    avg_speed_kmph: 28.5,
    speed: '28 km/h',
    congestion_level: 'Medium',
    updated_at: new Date().toISOString(),
  },
  {
    road_id: 'R006',
    road_name: 'Airport Road',
    vehicle_count: 55,
    density: 22.4,
    avg_speed_kmph: 12.0,
    speed: '12 km/h',
    congestion_level: 'High',
    updated_at: new Date().toISOString(),
  },
  {
    road_id: 'R007',
    road_name: 'Harbor Tunnel Approach',
    vehicle_count: 68,
    density: 29.8,
    avg_speed_kmph: 6.5,
    speed: '6 km/h',
    congestion_level: 'Severe',
    updated_at: new Date().toISOString(),
  },
];

const MOCK_DENSITY_SUMMARY = {
  total_roads: 7,
  total_roads_monitored: 7,
  total_vehicle_count: 239,
  average_density: 11.95,
  average_network_density: 11.95,
  maximum_density: 29.8,
  minimum_density: 0.22,
  high_congestion_roads: 1,
  severe_congestion_roads: 1,
  congested_segments: 2,
  avg_delay: '+5.4m',
  timestamp: new Date().toISOString(),
};

// ==========================================
// Data Normalization & Badge Helpers
// ==========================================
function normalizeDensitySummary(data) {
  if (!data) return MOCK_DENSITY_SUMMARY;

  const totalRoads = data.total_roads ?? data.total_roads_monitored ?? 6;
  const avgDensity = Number(data.average_density ?? data.average_network_density ?? 8.95);
  const maxDensity = Number(data.maximum_density ?? avgDensity * 1.8);
  const minDensity = Number(data.minimum_density ?? 0.22);
  const highCount = Number(data.high_congestion_roads ?? data.congested_segments ?? 1);
  const severeCount = Number(data.severe_congestion_roads ?? 0);
  const totalVehicles = Number(data.total_vehicle_count ?? 171);

  return {
    total_roads: totalRoads,
    total_roads_monitored: totalRoads,
    average_density: Math.round(avgDensity * 100) / 100,
    average_network_density: Math.round(avgDensity * 100) / 100,
    maximum_density: Math.round(maxDensity * 100) / 100,
    minimum_density: Math.round(minDensity * 100) / 100,
    high_congestion_roads: highCount,
    severe_congestion_roads: severeCount,
    congested_segments: highCount + severeCount,
    total_vehicle_count: totalVehicles,
    timestamp: data.timestamp || new Date().toISOString(),
  };
}

function normalizeRoadData(road) {
  if (!road) return null;
  const roadNames = {
    R001: 'Main Expressway',
    R002: 'Central Avenue',
    R003: 'West Ring Road',
    R004: 'North Boulevard',
    R005: 'Industrial Highway',
    R006: 'Airport Road',
    R007: 'Harbor Tunnel Approach',
  };

  const level = (road.congestion_level || 'Low').trim();
  const density = Number(road.density ?? road.traffic_density_vehicles_per_km ?? 0);
  const vehicleCount = Number(road.vehicle_count ?? 0);
  const avgSpeed =
    road.avg_speed_kmph !== undefined && road.avg_speed_kmph !== null
      ? Number(road.avg_speed_kmph)
      : level === 'Severe'
        ? 7
        : level === 'High'
          ? 14
          : level === 'Medium'
            ? 28
            : 50;

  return {
    road_id: road.road_id,
    road_name: road.road_name || road.name || roadNames[road.road_id] || `Road ${road.road_id}`,
    vehicle_count: vehicleCount,
    density: Math.round(density * 100) / 100,
    avg_speed_kmph: Math.round(avgSpeed * 10) / 10,
    speed: road.speed || `${Math.round(avgSpeed)} km/h`,
    congestion_level: level,
    updated_at: road.updated_at || road.reading_timestamp || new Date().toISOString(),
  };
}

function getCongestionBadgeInfo(level = 'Low', density = 0) {
  const normLevel = (level || '').toLowerCase();

  if (normLevel.includes('severe') || density >= 28) {
    return {
      level: 'Severe',
      label: 'Severe Gridlock',
      badgeBg:
        'bg-[#e11d48]/20 text-[#fda4af] border-[#e11d48]/40 shadow-[0_0_12px_rgba(225,29,72,0.4)]',
      borderClass: 'border-l-4 border-l-[#e11d48]',
      badgeClass: 'text-[#fda4af]',
      indicatorBg: 'bg-[#e11d48]',
      icon: 'emergency',
      colorHex: '#e11d48',
    };
  } else if (normLevel.includes('high') || density >= 20) {
    return {
      level: 'High',
      label: 'Heavy Congestion',
      badgeBg: 'bg-[#ef4444]/20 text-[#fca5a5] border-[#ef4444]/30',
      borderClass: 'border-l-4 border-l-[#ef4444]',
      badgeClass: 'text-error',
      indicatorBg: 'bg-error',
      icon: 'car_crash',
      colorHex: '#ef4444',
    };
  } else if (normLevel.includes('med') || density >= 10) {
    return {
      level: 'Medium',
      label: 'Moderate Delay',
      badgeBg: 'bg-[#facc15]/20 text-[#fef08a] border-[#facc15]/30',
      borderClass: 'border-l-4 border-l-[#facc15]',
      badgeClass: 'text-yellow-400',
      indicatorBg: 'bg-yellow-400',
      icon: 'info',
      colorHex: '#facc15',
    };
  } else {
    return {
      level: 'Low',
      label: 'Optimal Flow',
      badgeBg: 'bg-[#4ade80]/20 text-[#bbf7d0] border-[#4ade80]/30',
      borderClass: 'border-l-4 border-l-[#4ade80]',
      badgeClass: 'text-emerald-300',
      indicatorBg: 'bg-emerald-400',
      icon: 'check_circle',
      colorHex: '#4ade80',
    };
  }
}

// ==========================================
// Authentication & Session Management
// ==========================================
const AuthManager = {
  getToken() {
    return sessionStorage.getItem('access_token');
  },
  getRefreshToken() {
    return sessionStorage.getItem('refresh_token');
  },
  getRole() {
    const rawRole = (sessionStorage.getItem('role') || '').toUpperCase();
    if (rawRole === 'TRAFFIC_OPERATOR') return 'OPERATOR';
    if (rawRole === 'USER') return 'PUBLIC';
    return rawRole;
  },
  getUserName() {
    return sessionStorage.getItem('user_name') || 'Traffic Operator';
  },
  setSession(data) {
    if (data.access_token) sessionStorage.setItem('access_token', data.access_token);
    if (data.refresh_token) sessionStorage.setItem('refresh_token', data.refresh_token);
    if (data.role) {
      let role = data.role.toUpperCase();
      if (role === 'TRAFFIC_OPERATOR') role = 'OPERATOR';
      if (role === 'USER') role = 'PUBLIC';
      sessionStorage.setItem('role', role);
    }
    if (data.name) sessionStorage.setItem('user_name', data.name);
  },
  clearSession() {
    sessionStorage.clear();
  },
  isAuthenticated() {
    return !!this.getToken();
  },
  getDashboardUrl(role) {
    let r = (role || this.getRole()).toUpperCase();
    if (r === 'USER') r = 'PUBLIC';
    if (r === 'ADMIN') return 'admin dashboard.html';
    if (r === 'OPERATOR' || r === 'TRAFFIC_OPERATOR') return 'operator dashboard.html';
    return 'public dashboard.html';
  },
  guardPage(allowedRoles = []) {
    if (!this.isAuthenticated()) {
      window.location.replace('Login.html');
      return false;
    }
    const currentRole = this.getRole();
    if (allowedRoles.length > 0) {
      const hasAccess = allowedRoles.some((r) => {
        const normalized = r.toUpperCase();
        const targetRole = normalized === 'USER' ? 'PUBLIC' : normalized;
        const userRole = currentRole === 'USER' ? 'PUBLIC' : currentRole;
        return (
          userRole === targetRole || (targetRole === 'OPERATOR' && userRole === 'TRAFFIC_OPERATOR')
        );
      });
      if (!hasAccess) {
        const targetUrl = this.getDashboardUrl(currentRole);
        const currentPage = window.location.pathname.split('/').pop();
        // Prevent infinite redirect loop if already on target dashboard
        if (
          currentPage &&
          decodeURIComponent(currentPage).toLowerCase() === targetUrl.toLowerCase()
        ) {
          window.location.replace('Login.html');
          return false;
        }
        window.location.replace(targetUrl);
        return false;
      }
    }
    return true;
  },
  logout() {
    this.clearSession();
    window.location.href = 'Login.html';
  },
};

// Global shorthand for inline HTML onclick handlers
function logout() {
  AuthManager.logout();
}

function getDashboardUrl() {
  return AuthManager.getDashboardUrl();
}

// ==========================================
// Core Fetch Client - Direct Backend Call
// ==========================================
async function apiFetch(endpoint, options = {}, _alternateEndpoint = null) {
  const token = AuthManager.getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_CONFIG.BASE_URL}${cleanEndpoint}`;

  const controller = new AbortController();
  const timeoutMs = API_CONFIG.TIMEOUT || 10000;
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    let response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    // Handle 401 Silent Refresh
    if (response.status === 401 && AuthManager.getRefreshToken()) {
      const refreshed = await tryTokenRefresh();
      if (refreshed) {
        const refreshedToken = AuthManager.getToken();
        const retryHeaders = {
          ...headers,
          Authorization: `Bearer ${refreshedToken}`,
        };
        response = await fetch(url, { ...options, headers: retryHeaders });
      }
    }

    if (response.ok) {
      return await response.json();
    }

    const errorData = await response.json().catch(() => ({}));
    let errorDetail = errorData.detail || errorData.message || `HTTP Error ${response.status}`;
    if (Array.isArray(errorDetail)) {
      errorDetail = errorDetail
        .map((e) => e.msg || (typeof e === 'string' ? e : JSON.stringify(e)))
        .join(', ');
    }
    throw new Error(errorDetail);
  } catch (err) {
    clearTimeout(timeoutId);
    throw err;
  }
}

async function tryTokenRefresh() {
  const refreshToken = AuthManager.getRefreshToken();
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${API_CONFIG.BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.access_token) {
        sessionStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          sessionStorage.setItem('refresh_token', data.refresh_token);
        }
        return true;
      }
    }
  } catch (e) {
    console.warn('Token refresh failed:', e);
  }
  return false;
}

// ==========================================
// Service API Modules
// ==========================================
const authAPI = {
  async login(email, password) {
    return await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },
  async register(name, email, password, role = 'user') {
    let backendRole = (role || 'user').toLowerCase();
    if (backendRole === 'public') {
      backendRole = 'user';
    } else if (backendRole === 'traffic_operator') {
      backendRole = 'operator';
    }

    return await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password, role: backendRole }),
    });
  },
  async getProfile() {
    try {
      return await apiFetch('/auth/me');
    } catch (err) {
      return {
        user_id: 'local-user',
        name: AuthManager.getUserName(),
        role: AuthManager.getRole(),
      };
    }
  },
};

const operatorAPI = {
  _storageKey: 'traffic_operators_roster',
  _getDefaults() {
    return [
      {
        id: 'OP-101',
        name: 'J. Smith',
        email: 'j.smith@trafficvision.ai',
        sector: 'Airport Corridor (R006)',
        status: 'Active',
        shift: 'Morning',
        created_at: '2026-09-10',
      },
      {
        id: 'OP-102',
        name: 'Sarah Connor',
        email: 's.connor@trafficvision.ai',
        sector: 'Downtown Grid (R002)',
        status: 'Active',
        shift: 'Day',
        created_at: '2026-09-11',
      },
      {
        id: 'OP-103',
        name: 'Alex Chen',
        email: 'a.chen@trafficvision.ai',
        sector: 'Main Expressway (R001)',
        status: 'Standby',
        shift: 'Evening',
        created_at: '2026-09-12',
      },
      {
        id: 'OP-104',
        name: 'Elena Rostova',
        email: 'e.rostova@trafficvision.ai',
        sector: 'West Ring Road (R003)',
        status: 'Active',
        shift: 'Night',
        created_at: '2026-09-12',
      },
    ];
  },
  getOperators() {
    try {
      const raw = localStorage.getItem(this._storageKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.warn('Failed to parse operators from storage:', e);
    }
    const defaults = this._getDefaults();
    this._save(defaults);
    return defaults;
  },
  _save(operators) {
    try {
      localStorage.setItem(this._storageKey, JSON.stringify(operators));
    } catch (e) {
      console.warn('Failed to persist operators:', e);
    }
  },
  async addOperator({ name, email, password, sector, shift }) {
    try {
      await authAPI.register(name, email, password || 'Operator@123', 'operator');
    } catch (e) {
      console.info('Backend register offline or bypassed, storing locally:', e.message);
    }

    const operators = this.getOperators();
    const idNum = Math.floor(100 + Math.random() * 900);
    const newOp = {
      id: `OP-${idNum}`,
      name: name.trim(),
      email: email.trim().toLowerCase(),
      sector: sector || 'Downtown Grid (R002)',
      status: 'Active',
      shift: shift || 'Morning',
      created_at: new Date().toISOString().split('T')[0],
    };
    operators.unshift(newOp);
    this._save(operators);
    return newOp;
  },
  async removeOperator(id) {
    const operators = this.getOperators();
    const filtered = operators.filter((op) => op.id !== id);
    this._save(filtered);
    return true;
  },
};

const trafficAPI = {
  async getLiveTraffic() {
    try {
      const data = await apiFetch('/traffic/live');
      if (Array.isArray(data)) {
        return data.map(normalizeRoadData);
      }
      return MOCK_TRAFFIC_DATA.map(normalizeRoadData);
    } catch (err) {
      console.warn('Using Day 6 mock live traffic data:', err.message);
      return MOCK_TRAFFIC_DATA.map(normalizeRoadData);
    }
  },
  async getDensitySummary() {
    try {
      const data = await apiFetch('/traffic/density');
      return normalizeDensitySummary(data);
    } catch (err) {
      console.warn('Using Day 6 mock density summary:', err.message);
      return normalizeDensitySummary(MOCK_DENSITY_SUMMARY);
    }
  },
  async getRoadTraffic(roadId) {
    try {
      const data = await apiFetch(`/traffic/road/${roadId}`);
      if (data) {
        const norm = normalizeRoadData(data);
        const rawHistory = Array.isArray(data.history) ? data.history : [];
        norm.history = rawHistory.map((h) => ({
          vehicle_count: h.vehicle_count,
          density: Number(h.density ?? h.traffic_density_vehicles_per_km ?? 0),
          congestion_level: h.congestion_level || norm.congestion_level,
          avg_speed_kmph: h.avg_speed_kmph ? Number(h.avg_speed_kmph) : norm.avg_speed_kmph,
          updated_at: h.updated_at || h.reading_timestamp || h.time || new Date().toISOString(),
        }));
        return norm;
      }
      throw new Error('No data returned');
    } catch (err) {
      console.warn(`Using mock road data for ${roadId}:`, err.message);
      const road =
        MOCK_TRAFFIC_DATA.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) ||
        MOCK_TRAFFIC_DATA[0];
      const norm = normalizeRoadData(road);
      norm.history = [
        {
          updated_at: '21:00:00',
          density: norm.density * 0.8,
          vehicle_count: Math.round(norm.vehicle_count * 0.8),
          avg_speed_kmph: norm.avg_speed_kmph * 1.1,
          congestion_level: 'Low',
        },
        {
          updated_at: '21:30:00',
          density: norm.density * 0.95,
          vehicle_count: Math.round(norm.vehicle_count * 0.95),
          avg_speed_kmph: norm.avg_speed_kmph * 1.05,
          congestion_level: norm.congestion_level,
        },
        {
          updated_at: '22:00:00',
          density: norm.density,
          vehicle_count: norm.vehicle_count,
          avg_speed_kmph: norm.avg_speed_kmph,
          congestion_level: norm.congestion_level,
        },
      ];
      return norm;
    }
  },
};

const ROAD_NETWORK_GEOMETRY = {
  center: [12.9716, 77.5946], // Metropolitan Metro Center Coordinates
  zoom: 13,
  hubs: [
    {
      id: 'HUB_DOWNTOWN',
      name: 'Downtown Central Terminal',
      coords: [12.975, 77.585],
      icon: 'hub',
      color: '#8dcdff',
    },
    {
      id: 'HUB_TECH_PARK',
      name: 'Tech Park Sector 4',
      coords: [12.935, 77.625],
      icon: 'apartment',
      color: '#bdc2ff',
    },
    {
      id: 'HUB_AIRPORT',
      name: 'International Airport Junction',
      coords: [13.015, 77.635],
      icon: 'flight_takeoff',
      color: '#cdbdff',
    },
    {
      id: 'HUB_INDUSTRIAL',
      name: 'Industrial Zone Gate 2',
      coords: [12.945, 77.545],
      icon: 'factory',
      color: '#facc15',
    },
    {
      id: 'HUB_HARBOR',
      name: 'Harbor Logistics Basin',
      coords: [12.985, 77.655],
      icon: 'anchor',
      color: '#e11d48',
    },
    {
      id: 'HUB_WEST_RIDGE',
      name: 'West Ridge Interchange',
      coords: [12.96, 77.53],
      icon: 'alt_route',
      color: '#4ade80',
    },
  ],
  segments: {
    R001: {
      road_id: 'R001',
      road_name: 'Main Expressway',
      length_km: 8.4,
      speed_limit: 60,
      coordinates: [
        [12.975, 77.585],
        [12.972, 77.598],
        [12.965, 77.61],
        [12.952, 77.618],
        [12.935, 77.625],
      ],
      junctions: ['HUB_DOWNTOWN', 'HUB_TECH_PARK'],
    },
    R002: {
      road_id: 'R002',
      road_name: 'Central Avenue',
      length_km: 5.2,
      speed_limit: 45,
      coordinates: [
        [12.975, 77.585],
        [12.968, 77.58],
        [12.955, 77.572],
        [12.945, 77.545],
      ],
      junctions: ['HUB_DOWNTOWN', 'HUB_INDUSTRIAL'],
    },
    R003: {
      road_id: 'R003',
      road_name: 'West Ring Road',
      length_km: 7.8,
      speed_limit: 50,
      coordinates: [
        [12.945, 77.545],
        [12.952, 77.538],
        [12.96, 77.53],
        [12.98, 77.542],
        [12.995, 77.56],
        [12.975, 77.585],
      ],
      junctions: ['HUB_INDUSTRIAL', 'HUB_WEST_RIDGE', 'HUB_DOWNTOWN'],
    },
    R004: {
      road_id: 'R004',
      road_name: 'North Boulevard',
      length_km: 9.1,
      speed_limit: 65,
      coordinates: [
        [12.975, 77.585],
        [12.988, 77.595],
        [13.002, 77.612],
        [13.015, 77.635],
      ],
      junctions: ['HUB_DOWNTOWN', 'HUB_AIRPORT'],
    },
    R005: {
      road_id: 'R005',
      road_name: 'Industrial Highway',
      length_km: 6.5,
      speed_limit: 40,
      coordinates: [
        [12.945, 77.545],
        [12.938, 77.565],
        [12.932, 77.59],
        [12.935, 77.625],
      ],
      junctions: ['HUB_INDUSTRIAL', 'HUB_TECH_PARK'],
    },
    R006: {
      road_id: 'R006',
      road_name: 'Airport Road',
      length_km: 11.2,
      speed_limit: 50,
      coordinates: [
        [13.015, 77.635],
        [13.005, 77.648],
        [12.985, 77.655],
        [12.965, 77.64],
        [12.935, 77.625],
      ],
      junctions: ['HUB_AIRPORT', 'HUB_HARBOR', 'HUB_TECH_PARK'],
    },
    R007: {
      road_id: 'R007',
      road_name: 'Harbor Tunnel Approach',
      length_km: 4.6,
      speed_limit: 35,
      coordinates: [
        [12.975, 77.585],
        [12.979, 77.615],
        [12.985, 77.655],
      ],
      junctions: ['HUB_DOWNTOWN', 'HUB_HARBOR'],
    },
  },
};

const predictAPI = {
  async getCongestion(roadId) {
    // Build the POST body the backend expects (CongestionRequest schema)
    const road =
      MOCK_TRAFFIC_DATA.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) ||
      MOCK_TRAFFIC_DATA[0];
    const geom = ROAD_NETWORK_GEOMETRY.segments[road.road_id] || {
      length_km: 8.0,
      speed_limit: 60,
    };
    const now = new Date();
    const requestBody = {
      road_id: road.road_id,
      vehicle_count: road.vehicle_count || 30,
      density: road.density || 10,
      avg_speed_kmph: road.avg_speed_kmph || 40,
      road_capacity: geom.speed_limit ? geom.speed_limit * 2 : 100, // estimate capacity from speed limit
      road_length_km: geom.length_km || 5.0,
      hour: now.getHours(),
      day_of_week: now.getDay(), // 0 = Sunday … 6 = Saturday
      is_weekend: now.getDay() === 0 || now.getDay() === 6 ? 1 : 0,
    };

    try {
      return await apiFetch('/predict/congestion', {
        method: 'POST',
        body: JSON.stringify(requestBody),
      });
    } catch (err) {
      console.warn(`Using fallback prediction for ${roadId} (backend unavailable):`, err.message);
      const density = road.density || 10;

      let predicted_level = 'Low';
      let confidence = 0.88;
      if (density >= 28) {
        predicted_level = 'Severe';
        confidence = 0.94;
      } else if (density >= 20) {
        predicted_level = 'High';
        confidence = 0.91;
      } else if (density >= 10) {
        predicted_level = 'Medium';
        confidence = 0.85;
      }

      return {
        road_id: road.road_id,
        road_name: road.road_name,
        predicted_level,
        confidence,
        generated_by: 'model-v1',
      };
    }
  },

  async getPeakHourPrediction(roadId = 'R006') {
    try {
      const data = await apiFetch(`/predict/peak-hours?road_id=${encodeURIComponent(roadId)}`);
      if (data && data.peak_hours) return data;
    } catch (err) {
      console.warn(`Using model-v1 peak-hour prediction generator for ${roadId}:`, err.message);
    }

    // Intern 3's model-v1 peak-hours calculation: hours [8, 9, 10, 17, 18, 19, 20]
    const road =
      MOCK_TRAFFIC_DATA.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) ||
      MOCK_TRAFFIC_DATA[5];
    const baseDensity = road.density;
    const peakHours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];

    const hourProfiles = {
      7: { multiplier: 0.65, label: '07:00 AM' },
      8: { multiplier: 1.35, label: '08:00 AM (Morning Peak)' },
      9: { multiplier: 1.45, label: '09:00 AM (Morning Rush)' },
      10: { multiplier: 1.15, label: '10:00 AM' },
      11: { multiplier: 0.85, label: '11:00 AM' },
      12: { multiplier: 0.9, label: '12:00 PM' },
      13: { multiplier: 0.88, label: '01:00 PM' },
      14: { multiplier: 0.92, label: '02:00 PM' },
      15: { multiplier: 1.05, label: '03:00 PM' },
      16: { multiplier: 1.25, label: '04:00 PM' },
      17: { multiplier: 1.5, label: '05:00 PM (Evening Peak)' },
      18: { multiplier: 1.6, label: '06:00 PM (Evening Rush)' },
      19: { multiplier: 1.35, label: '07:00 PM' },
      20: { multiplier: 1.05, label: '08:00 PM' },
      21: { multiplier: 0.7, label: '09:00 PM' },
    };

    const predictions = peakHours.map((hour) => {
      const profile = hourProfiles[hour] || { multiplier: 1.0, label: `${hour}:00` };
      const simDensity = Math.round(baseDensity * profile.multiplier * 10) / 10;
      const simVehicles = Math.round((road.vehicle_count || 30) * profile.multiplier);

      let level = 'Low';
      let confidence = 0.89;
      if (simDensity >= 28) {
        level = 'Severe';
        confidence = 0.95;
      } else if (simDensity >= 20) {
        level = 'High';
        confidence = 0.92;
      } else if (simDensity >= 10) {
        level = 'Medium';
        confidence = 0.86;
      }

      return {
        hour: hour,
        time_label: profile.label,
        density: simDensity,
        vehicle_count: simVehicles,
        predicted_level: level,
        confidence: confidence,
        is_peak_period: [8, 9, 10, 17, 18, 19, 20].includes(hour),
      };
    });

    return {
      road_id: road.road_id,
      road_name: road.road_name,
      peak_hours: predictions,
      generated_by: 'model-v1',
      timestamp: new Date().toISOString(),
    };
  },

  async getAllDelayEstimates() {
    const liveRoads = await trafficAPI.getLiveTraffic();
    return liveRoads.map((road) => {
      const geom = ROAD_NETWORK_GEOMETRY.segments[road.road_id] || {
        length_km: 7.0,
        speed_limit: 50,
      };
      const lengthKm = geom.length_km;
      const speedLimit = geom.speed_limit;
      const currentSpeed = Math.max(5, road.avg_speed_kmph || 40);

      const freeFlowMinutes = Math.round((lengthKm / speedLimit) * 60 * 10) / 10;
      const actualMinutes = Math.round((lengthKm / currentSpeed) * 60 * 10) / 10;
      const delayMinutes = Math.max(0, Math.round((actualMinutes - freeFlowMinutes) * 10) / 10);

      // AI Predicted Delay in 30 minutes
      const forecast = this.getTemporalForecast(road.road_id, 30);
      const predictedSpeed = Math.max(5, forecast.predicted_speed || currentSpeed);
      const predictedMinutes = Math.round((lengthKm / predictedSpeed) * 60 * 10) / 10;
      const predictedDelay = Math.max(
        0,
        Math.round((predictedMinutes - freeFlowMinutes) * 10) / 10
      );

      let status = 'Normal Flow';
      let statusColor = 'text-emerald-400';
      if (delayMinutes >= 15 || road.congestion_level === 'Severe') {
        status = 'Critical Delay';
        statusColor = 'text-rose-400';
      } else if (delayMinutes >= 8 || road.congestion_level === 'High') {
        status = 'High Delay';
        statusColor = 'text-error';
      } else if (delayMinutes >= 3 || road.congestion_level === 'Medium') {
        status = 'Moderate Delay';
        statusColor = 'text-yellow-400';
      }

      return {
        road_id: road.road_id,
        road_name: road.road_name,
        length_km: lengthKm,
        speed_limit: speedLimit,
        current_speed: currentSpeed,
        predicted_speed: predictedSpeed,
        free_flow_time_min: freeFlowMinutes,
        current_time_min: actualMinutes,
        delay_minutes: delayMinutes,
        predicted_delay_30m: predictedDelay,
        congestion_level: road.congestion_level,
        predicted_level: forecast.predicted_level,
        status: status,
        status_color: statusColor,
      };
    });
  },

  getTemporalForecast(roadId, horizonMinutes = 0) {
    const road =
      MOCK_TRAFFIC_DATA.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) ||
      MOCK_TRAFFIC_DATA[0];
    const baseDensity = road.density;
    const baseSpeed = road.avg_speed_kmph;

    // Multiplier curves based on rush hour trend simulation
    let densityDelta = 0;
    let speedDelta = 0;

    if (horizonMinutes === 15) {
      densityDelta = road.road_id === 'R006' || road.road_id === 'R007' ? 3.5 : 1.2;
      speedDelta = -3.0;
    } else if (horizonMinutes === 30) {
      densityDelta = road.road_id === 'R006' || road.road_id === 'R007' ? 7.2 : 2.8;
      speedDelta = -6.5;
    } else if (horizonMinutes === 60) {
      densityDelta = road.road_id === 'R005' || road.road_id === 'R006' ? 9.8 : 4.5;
      speedDelta = -10.0;
    } else if (horizonMinutes === 120) {
      densityDelta = -2.5; // Dispersion after peak
      speedDelta = 5.0;
    }

    const predictedDensity = Math.max(0.2, Math.round((baseDensity + densityDelta) * 100) / 100);
    const predictedSpeed = Math.max(5.0, Math.round((baseSpeed + speedDelta) * 10) / 10);

    let predictedLevel = 'Low';
    if (predictedDensity >= 28) predictedLevel = 'Severe';
    else if (predictedDensity >= 20) predictedLevel = 'High';
    else if (predictedDensity >= 10) predictedLevel = 'Medium';

    return {
      road_id: road.road_id,
      road_name: road.road_name,
      horizon_minutes: horizonMinutes,
      current_density: baseDensity,
      predicted_density: predictedDensity,
      current_speed: baseSpeed,
      predicted_speed: predictedSpeed,
      predicted_level: predictedLevel,
      confidence: Math.max(0.72, Math.round((0.95 - horizonMinutes * 0.0015) * 100) / 100),
      trend:
        densityDelta > 0 ? 'Increasing Congestion' : densityDelta < 0 ? 'Clearing Flow' : 'Stable',
    };
  },

  getAllRoadForecasts(horizonMinutes = 30) {
    return MOCK_TRAFFIC_DATA.map((road) => this.getTemporalForecast(road.road_id, horizonMinutes));
  },

  getHistoricalVsPredicted(roadId) {
    const road =
      MOCK_TRAFFIC_DATA.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) ||
      MOCK_TRAFFIC_DATA[0];
    const base = road.density;
    return [
      { time: '18:00', actual: Math.max(1, base * 0.5), predicted: Math.max(1, base * 0.52) },
      { time: '19:00', actual: Math.max(2, base * 0.75), predicted: Math.max(2, base * 0.72) },
      { time: '20:00 (Now)', actual: base, predicted: base },
      { time: '20:30 (+30m)', actual: null, predicted: Math.round(base * 1.25 * 10) / 10 },
      { time: '21:00 (+1h)', actual: null, predicted: Math.round(base * 1.4 * 10) / 10 },
      { time: '22:00 (+2h)', actual: null, predicted: Math.round(base * 0.9 * 10) / 10 },
    ];
  },

  /**
   * Generates and triggers client-side download of a comprehensive
   * Traffic Intelligence & Prediction Report (CSV or JSON format).
   */
  async downloadPredictionReport(format = 'csv') {
    const [liveRoads, densitySummary, delays, peakR006, peakR007] = await Promise.all([
      trafficAPI.getLiveTraffic(),
      trafficAPI.getDensitySummary(),
      this.getAllDelayEstimates(),
      this.getPeakHourPrediction('R006'),
      this.getPeakHourPrediction('R007'),
    ]);

    const timestamp = new Date().toISOString();
    const dateStr = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
    const filename = `TrafficVision_AI_Prediction_Report_${new Date().toISOString().slice(0, 10)}_${Date.now().toString().slice(-4)}.${format}`;

    if (format === 'json') {
      const reportPayload = {
        report_title: 'TrafficVision AI - Comprehensive Prediction & Delay Report',
        generated_at: timestamp,
        model_version: 'model-v1 (Intern 3 AI Prediction Service)',
        executive_summary: {
          total_roads_monitored: densitySummary.total_roads || liveRoads.length,
          total_vehicles_active: densitySummary.total_vehicle_count,
          average_network_density: densitySummary.average_density,
          severe_bottlenecks: densitySummary.severe_congestion_roads || 0,
          high_congestion_roads: densitySummary.high_congestion_roads || 0,
        },
        corridor_delay_estimates: delays,
        per_road_temporal_forecasts_30m: this.getAllRoadForecasts(30),
        peak_hour_schedules: {
          'Airport Road (R006)': peakR006.peak_hours,
          'Harbor Tunnel Approach (R007)': peakR007.peak_hours,
        },
        recommended_interventions: [
          'Activate dynamic signal prioritization at Tech Park & Airport Junctions',
          'Reroute commercial freight from Harbor Tunnel (R007) to West Bypass (R003)',
          'Deploy automated variable message signs (VMS) on Main Expressway',
        ],
      };

      const dataStr =
        'data:text/json;charset=utf-8,' +
        encodeURIComponent(JSON.stringify(reportPayload, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', filename);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      return { filename, status: 'success', count: liveRoads.length };
    }

    // CSV Export Format
    let csvContent = `TrafficVision AI - Network Traffic Prediction & Delay Analysis Report\n`;
    csvContent += `Generated At,"${dateStr}"\n`;
    csvContent += `AI Prediction Engine,Intern 3 (model-v1)\n`;
    csvContent += `Network Avg Density,${densitySummary.average_density} veh/km\n`;
    csvContent += `Active Vehicles Monitored,${densitySummary.total_vehicle_count}\n\n`;

    csvContent += `--- 1. LIVE CORRIDOR DELAY ESTIMATES & SPEED PROJECTIONS ---\n`;
    csvContent += `Road ID,Road Name,Length (km),Speed Limit (km/h),Current Speed (km/h),Predicted Speed (km/h),Free Flow Time (min),Current Time (min),Current Delay (min),Predicted Delay +30m (min),Congestion Level,Predicted Level (+30m),Status\n`;

    delays.forEach((d) => {
      csvContent += `"${d.road_id}","${d.road_name}",${d.length_km},${d.speed_limit},${d.current_speed},${d.predicted_speed},${d.free_flow_time_min},${d.current_time_min},${d.delay_minutes},${d.predicted_delay_30m},"${d.congestion_level}","${d.predicted_level}","${d.status}"\n`;
    });

    csvContent += `\n--- 2. PER-ROAD MULTI-HORIZON CONGESTION FORECASTS ---\n`;
    csvContent += `Road ID,Road Name,Current Density (veh/km),Forecast +15m Density,Forecast +30m Density,Forecast +60m Density,Forecast +120m Density,Trend,Confidence Score\n`;

    liveRoads.forEach((r) => {
      const f15 = this.getTemporalForecast(r.road_id, 15);
      const f30 = this.getTemporalForecast(r.road_id, 30);
      const f60 = this.getTemporalForecast(r.road_id, 60);
      const f120 = this.getTemporalForecast(r.road_id, 120);
      csvContent += `"${r.road_id}","${r.road_name}",${r.density},${f15.predicted_density},${f30.predicted_density},${f60.predicted_density},${f120.predicted_density},"${f30.trend}",${(f30.confidence * 100).toFixed(0)}%\n`;
    });

    csvContent += `\n--- 3. PEAK-HOUR CONGESTION CURVE (Airport Road R006 & Harbor Tunnel R007) ---\n`;
    csvContent += `Hour,Period Label,R006 Predicted Density (veh/km),R006 Congestion Level,R007 Predicted Density (veh/km),R007 Congestion Level\n`;

    peakR006.peak_hours.forEach((p, idx) => {
      const r7Peak = peakR007.peak_hours[idx] || p;
      csvContent += `"${p.hour}:00","${p.time_label}",${p.density},"${p.predicted_level}",${r7Peak.density},"${r7Peak.predicted_level}"\n`;
    });

    csvContent += `\n--- 4. AI TACTICAL RECOMMENDATIONS ---\n`;
    csvContent += `1,"Deploy tactical rerouting via West Ring Road (R003) to alleviate Harbor Tunnel (R007) severe gridlock."\n`;
    csvContent += `2,"Adjust signal timing offsets by +12s green time on Airport Road northbound corridor during 05:00-07:00 PM peak."\n`;
    csvContent += `3,"Broadcast live delay estimates to connected commuter navigation endpoints."\n`;

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return { filename, status: 'success', count: liveRoads.length };
  },
};

// ==========================================
// Route Analysis API Helpers
// ==========================================

/**
 * Maps a numeric congestion_score (0.0–1.0) from the backend
 * to the UI congestion level string used by getCongestionBadgeInfo().
 */
function congestionScoreToLevel(score) {
  if (score == null || isNaN(score)) return 'Low';
  if (score >= 0.75) return 'Severe';
  if (score >= 0.5) return 'High';
  if (score >= 0.25) return 'Medium';
  return 'Low';
}

/**
 * Transforms a backend optimized/alternate route response into the
 * UI data shape consumed by renderRouteCards, renderMapObjects, etc.
 *
 * @param {Object} backendRoute  – raw response from /route/optimize or one element of /route/alternate
 * @param {Object} opts          – { isRecommended, routeType, routeName, rank, travelTimeMin }
 * @returns {Object}             – UI-compatible route object
 */
function normalizeBackendRoute(backendRoute, opts = {}) {
  const routeId = backendRoute.route_id || `ROUTE_${opts.rank || 0}`;
  const geometry = backendRoute.geometry || backendRoute.path || [];
  // The backend returns GeoJSON geometry as [[lng, lat], ...] or [{lat, lng}, ...]
  // Leaflet polylines expect [lat, lng], so swap GeoJSON array coordinates to [lat, lng].
  const coordinates = geometry.map((pt) => {
    if (Array.isArray(pt)) return [pt[1], pt[0]];
    if (pt && typeof pt.lat === 'number') return [pt.lat, pt.lng];
    return [0, 0];
  });

  const distanceKm = Number(backendRoute.distance_km || 0);
  const congestionScore = Number(backendRoute.congestion_score || 0);
  const congestionLevel = congestionScoreToLevel(congestionScore);
  const durationMin = opts.travelTimeMin || Math.round((distanceKm / 40) * 60); // fallback estimate
  const freeFlowMin = Math.round((distanceKm / 60) * 60);
  const delayMin = Math.max(0, Math.round((durationMin - freeFlowMin) * 10) / 10);

  // Build a single synthetic segment from the full route geometry
  // (the backend returns the route as one path, not per-road-segment)
  const segment = {
    road_id: routeId,
    road_name: opts.routeName || `Route ${opts.rank || 1}`,
    length_km: Math.round(distanceKm * 10) / 10,
    speed_limit: 60,
    current_speed:
      distanceKm > 0 && durationMin > 0
        ? Math.round((distanceKm / (durationMin / 60)) * 10) / 10
        : 40,
    density: Math.round(congestionScore * 30 * 100) / 100, // approximate density from score
    congestion_level: congestionLevel,
    segment_time_min: durationMin,
    coordinates: coordinates,
  };

  return {
    route_id: routeId,
    route_name: opts.routeName || `Route ${opts.rank || 1}`,
    route_type: opts.routeType || 'Alternative',
    is_recommended: !!opts.isRecommended,
    distance_km: Math.round(distanceKm * 10) / 10,
    duration_minutes: durationMin,
    delay_minutes: delayMin,
    worst_congestion: congestionLevel,
    congestion_score: congestionScore,
    ai_confidence: opts.isRecommended ? 0.94 : 0.85 - (opts.rank || 0) * 0.03,
    co2_estimate_kg: Math.round(distanceKm * 0.12 * 10) / 10,
    segments: [segment],
    coordinates: coordinates,
  };
}

// Tracks whether the backend route endpoints responded successfully.
// Once set to false, calculateRoutes skips the network round-trip
// entirely and uses the BFS mock — preventing the 5-10s freeze.
let _routeBackendOk = null; // null = untested, true = live, false = down

/**
 * Returns the great-circle distance in kilometres between two [lat, lng] pairs.
 * Used to validate that the backend route actually starts/ends near the
 * selected origin/destination hubs (catches stub backends that return the
 * same hardcoded route regardless of the requested endpoints).
 */
function haversineKm([lat1, lon1], [lat2, lon2]) {
  const R = 6371;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

const routeAPI = {
  getHubs() {
    return ROAD_NETWORK_GEOMETRY.hubs;
  },

  getRoadGeometry(roadId) {
    return ROAD_NETWORK_GEOMETRY.segments[roadId] || null;
  },

  getAllRoadGeometries() {
    return ROAD_NETWORK_GEOMETRY.segments;
  },

  // ==========================================
  // Backend API Fetch Methods (Intern 1 Endpoints)
  // ==========================================

  /**
   * GET /api/v1/route/optimize?origin={lat,lng}&destination={lat,lng}
   * Returns: { route_id, geometry/path[], distance_km, congestion_score }
   */
  async fetchOptimizedRoute(originCoords, destCoords) {
    const query = `?origin=${originCoords[0]},${originCoords[1]}&destination=${destCoords[0]},${destCoords[1]}`;
    return await apiFetch(`/route/optimize${query}`);
  },

  /**
   * GET /api/v1/route/alternate?origin={lat,lng}&destination={lat,lng}
   * Returns: Array of { route_id, path[], congestion_score, rank }
   */
  async fetchAlternateRoutes(originCoords, destCoords) {
    const query = `?origin=${originCoords[0]},${originCoords[1]}&destination=${destCoords[0]},${destCoords[1]}`;
    return await apiFetch(`/route/alternate${query}`);
  },

  /**
   * GET /api/v1/route/travel-time?origin={lat,lng}&destination={lat,lng}
   * Returns: { origin, destination, estimated_minutes }
   */
  async fetchTravelTime(originCoords, destCoords) {
    const query = `?origin=${originCoords[0]},${originCoords[1]}&destination=${destCoords[0]},${destCoords[1]}`;
    return await apiFetch(`/route/travel-time${query}`);
  },

  /**
   * GET /api/v1/route/conditions?origin={lat,lng}&destination={lat,lng}
   * Returns: { origin, destination, status, hazards[], road_work_present }
   */
  async fetchRoadConditions(originCoords, destCoords) {
    const query = `?origin=${originCoords[0]},${originCoords[1]}&destination=${destCoords[0]},${destCoords[1]}`;
    return await apiFetch(`/route/conditions${query}`);
  },

  // ==========================================
  // Main Route Calculation (Backend → Fallback)
  // ==========================================

  async calculateRoutes(originId, destinationId, optimizationMode = 'ai_optimal') {
    const hubs = ROAD_NETWORK_GEOMETRY.hubs;
    const origin = hubs.find((h) => h.id === originId) || hubs[0];
    const destination = hubs.find((h) => h.id === destinationId) || hubs[1];

    // ── Try Backend API First (skip if already known to be down) ──
    if (_routeBackendOk !== false) {
      try {
        const originCoords = origin.coords;
        const destCoords = destination.coords;

        // Fire all API calls concurrently for performance
        const [optimizedData, alternatesData, travelTimeData, conditionsData] = await Promise.all([
          this.fetchOptimizedRoute(originCoords, destCoords),
          this.fetchAlternateRoutes(originCoords, destCoords),
          this.fetchTravelTime(originCoords, destCoords).catch(() => null),
          this.fetchRoadConditions(originCoords, destCoords).catch(() => null),
        ]);

        // ── Validate geometry: non-empty and non-zero distance ──
        const rawGeometry = optimizedData?.geometry || optimizedData?.path || [];
        if (!rawGeometry.length || !Number(optimizedData?.distance_km)) {
          throw new Error('Backend returned empty/stub geometry \u2014 using BFS mock fallback');
        }

        // ── Proximity check: does the route actually connect the
        //    selected origin and destination? ──
        // A stub backend that returns the same hardcoded route for
        // every request will fail this check because its fixed
        // endpoint will be far from the user's chosen destination hub.
        // GeoJSON format from backend is [lng, lat]; hubs are [lat, lng].
        // Swap array points to [pt[1], pt[0]] before comparing distance.
        const ptToArr = (pt) =>
          Array.isArray(pt) ? [pt[1], pt[0]] : pt?.lat != null ? [pt.lat, pt.lng] : null;
        const routeStart = ptToArr(rawGeometry[0]);
        const routeEnd = ptToArr(rawGeometry[rawGeometry.length - 1]);
        if (routeStart && routeEnd) {
          const startOffset = haversineKm(originCoords, routeStart);
          const endOffset = haversineKm(destCoords, routeEnd);
          const THRESHOLD_KM = 3.0;
          if (startOffset > THRESHOLD_KM || endOffset > THRESHOLD_KM) {
            throw new Error(
              `Backend route doesn't match selected hubs ` +
                `(origin offset: ${startOffset.toFixed(1)} km, ` +
                `dest offset: ${endOffset.toFixed(1)} km) \u2014 using BFS mock`
            );
          }
        }

        // Travel time from the dedicated endpoint (for the optimized route)
        const estimatedMinutes = travelTimeData ? Number(travelTimeData.estimated_minutes) : null;

        // Build optimized route (marked as recommended)
        const optimizedRoute = normalizeBackendRoute(optimizedData, {
          isRecommended: true,
          routeType: 'AI Optimal',
          routeName: optimizedData.route_name || 'AI Optimized Route',
          rank: 0,
          travelTimeMin: estimatedMinutes,
        });

        // Build alternate routes
        const altRoutes = [];
        const altArray = Array.isArray(alternatesData)
          ? alternatesData
          : alternatesData?.routes || [];
        altArray.forEach((alt, idx) => {
          const altRoute = normalizeBackendRoute(alt, {
            isRecommended: false,
            routeType: `Alternative ${String.fromCharCode(65 + idx)}`, // A, B, C...
            routeName: alt.route_name || `Alternate Route ${String.fromCharCode(65 + idx)}`,
            rank: alt.rank || idx + 1,
            travelTimeMin: null, // travel-time endpoint is only for the primary route
          });
          altRoutes.push(altRoute);
        });

        const routes = [optimizedRoute, ...altRoutes];

        // Sort by duration if fastest mode selected
        if (optimizationMode === 'fastest') {
          routes.sort((a, b) => a.duration_minutes - b.duration_minutes);
        }

        // Store road conditions data for the UI to consume
        const result = {
          origin: origin,
          destination: destination,
          optimization_mode: optimizationMode,
          generated_at: new Date().toISOString(),
          routes: routes,
          road_conditions: conditionsData || null,
          data_source: 'backend',
        };

        _routeBackendOk = true;
        console.info('✅ Route data fetched from backend API');
        return result;
      } catch (backendError) {
        _routeBackendOk = false;
        console.warn(
          '⚠️ Backend route API unavailable, falling back to BFS mock:',
          backendError.message
        );
      }
    } else {
      console.info('⚡ Backend route API known-down — using BFS mock directly (no network wait)');
    }

    // ── Fallback: Client-Side Mock Calculation ──
    const liveRoads = await trafficAPI.getLiveTraffic();
    const roadMap = {};
    liveRoads.forEach((r) => {
      roadMap[r.road_id] = r;
    });

    // ── Build adjacency graph from road network junctions ──
    // Each road segment declares which hubs it connects via its `junctions`
    // array. We build a bidirectional graph: hubId → [{roadId, neighborHub}]
    const hubGraph = {};
    Object.values(ROAD_NETWORK_GEOMETRY.segments).forEach((seg) => {
      const junctions = seg.junctions || [];
      for (let i = 0; i < junctions.length; i++) {
        for (let j = 0; j < junctions.length; j++) {
          if (i === j) continue;
          const from = junctions[i];
          const to = junctions[j];
          if (!hubGraph[from]) hubGraph[from] = [];
          // Avoid duplicate edges for the same road
          const exists = hubGraph[from].some((e) => e.roadId === seg.road_id && e.hub === to);
          if (!exists) hubGraph[from].push({ hub: to, roadId: seg.road_id });
        }
      }
    });

    /**
     * BFS that finds up to `maxPaths` simple (non-repeating hub) paths
     * between originId and destinationId through the hub graph.
     * Returns an array of road-ID arrays, e.g. [["R001"], ["R002","R005"]].
     */
    function findHubPaths(fromHub, toHub, maxPaths = 3) {
      const results = [];
      // Queue entries: { hub, roadPath: string[], visitedHubs: Set }
      const queue = [{ hub: fromHub, roadPath: [], visitedHubs: new Set([fromHub]) }];

      while (queue.length > 0 && results.length < maxPaths) {
        const { hub, roadPath, visitedHubs } = queue.shift();
        const neighbors = hubGraph[hub] || [];

        for (const { hub: nextHub, roadId } of neighbors) {
          if (nextHub === toHub) {
            results.push([...roadPath, roadId]);
            if (results.length >= maxPaths) break;
          } else if (!visitedHubs.has(nextHub)) {
            queue.push({
              hub: nextHub,
              roadPath: [...roadPath, roadId],
              visitedHubs: new Set([...visitedHubs, nextHub]),
            });
          }
        }
      }

      // De-duplicate paths that traverse the same road set
      const seen = new Set();
      return results.filter((p) => {
        const key = [...p].sort().join(',');
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    }

    // Find up to 3 distinct paths for the chosen hub pair
    const foundPaths = findHubPaths(originId, destinationId, 3);

    // Guarantee at least one fallback path even if BFS finds nothing
    // (e.g., disconnected hubs) — fall back to the single direct segment
    // that best overlaps the origin hub, or R001 as last resort.
    if (foundPaths.length === 0) {
      const directSeg =
        Object.values(ROAD_NETWORK_GEOMETRY.segments).find((s) => s.junctions.includes(originId)) ||
        ROAD_NETWORK_GEOMETRY.segments['R001'];
      foundPaths.push([directSeg.road_id]);
    }

    // Apply eco / fastest modifier: sort each alternative path by its
    // combined congestion score so the "best" one bubbles to position 0.
    const scorePath = (segIds) => {
      let totalTime = 0;
      let totalDist = 0;
      let totalCongestion = 0;
      segIds.forEach((id) => {
        const geom = ROAD_NETWORK_GEOMETRY.segments[id];
        const live = roadMap[id] || { avg_speed_kmph: 50, density: 5 };
        if (!geom) return;
        const speed = Math.max(5, live.avg_speed_kmph || 40);
        totalTime += (geom.length_km / speed) * 60;
        totalDist += geom.length_km;
        totalCongestion += live.density || 0;
      });
      return { totalTime, totalDist, totalCongestion };
    };

    // Sort discovered paths by the active optimisation strategy
    const scoredPaths = foundPaths.map((p) => ({ path: p, ...scorePath(p) }));
    if (optimizationMode === 'eco') {
      scoredPaths.sort((a, b) => a.totalCongestion - b.totalCongestion);
    } else {
      // ai_optimal & fastest both prefer lowest travel time
      scoredPaths.sort((a, b) => a.totalTime - b.totalTime);
    }

    const routeLabels = [
      { id: 'ROUTE_ALPHA', name: 'Express Arterial Route', type: 'AI Optimal', recommended: true },
      { id: 'ROUTE_BETA', name: 'Western Ring Bypass', type: 'Alternative A', recommended: false },
      {
        id: 'ROUTE_GAMMA',
        name: 'Harbor East Perimeter',
        type: 'Alternative B',
        recommended: false,
      },
    ];

    const buildRouteSummary = (id, name, type, segmentsList, isAiRecommended) => {
      let totalDistanceKm = 0;
      let totalTravelTimeMin = 0;
      let totalFreeFlowTimeMin = 0;
      let worstCongestion = 'Low';
      const detailedSegments = [];
      const allCoords = [];

      segmentsList.forEach((segId) => {
        const geom = ROAD_NETWORK_GEOMETRY.segments[segId];
        const live = roadMap[segId] || { density: 5, avg_speed_kmph: 50, congestion_level: 'Low' };

        if (geom) {
          totalDistanceKm += geom.length_km;
          const speed = Math.max(5, live.avg_speed_kmph || 40);
          const segTime = (geom.length_km / speed) * 60;
          const freeFlowTime = (geom.length_km / geom.speed_limit) * 60;
          totalTravelTimeMin += segTime;
          totalFreeFlowTimeMin += freeFlowTime;

          if (
            live.congestion_level === 'Severe' ||
            (worstCongestion !== 'Severe' && live.congestion_level === 'High')
          ) {
            worstCongestion = live.congestion_level;
          } else if (worstCongestion === 'Low' && live.congestion_level === 'Medium') {
            worstCongestion = 'Medium';
          }

          detailedSegments.push({
            road_id: segId,
            road_name: geom.road_name,
            length_km: geom.length_km,
            speed_limit: geom.speed_limit,
            current_speed: speed,
            density: live.density,
            congestion_level: live.congestion_level,
            segment_time_min: Math.round(segTime * 10) / 10,
            coordinates: geom.coordinates,
          });

          geom.coordinates.forEach((pt) => allCoords.push(pt));
        }
      });

      const delayMin = Math.max(
        0,
        Math.round((totalTravelTimeMin - totalFreeFlowTimeMin) * 10) / 10
      );
      const totalMin = Math.round(totalTravelTimeMin);

      return {
        route_id: id,
        route_name: name,
        route_type: type,
        is_recommended: isAiRecommended,
        distance_km: Math.round(totalDistanceKm * 10) / 10,
        duration_minutes: totalMin,
        delay_minutes: delayMin,
        worst_congestion: worstCongestion,
        ai_confidence: isAiRecommended ? 0.94 : 0.82,
        co2_estimate_kg: Math.round(totalDistanceKm * 0.12 * 10) / 10,
        segments: detailedSegments,
        coordinates: allCoords,
      };
    };

    const routes = scoredPaths.map((sp, idx) => {
      const lbl = routeLabels[idx] || {
        id: `ROUTE_${String.fromCharCode(65 + idx)}`,
        name: `Route ${String.fromCharCode(65 + idx)}`,
        type: `Alternative ${String.fromCharCode(65 + idx)}`,
        recommended: false,
      };
      return buildRouteSummary(lbl.id, lbl.name, lbl.type, sp.path, lbl.recommended);
    });

    return {
      origin: origin,
      destination: destination,
      optimization_mode: optimizationMode,
      generated_at: new Date().toISOString(),
      routes: routes,
      road_conditions: null,
      data_source: 'mock_fallback',
    };
  },
};

// ==========================================
// Milestone 3: AI Recommendations API (Intern 3)
// ==========================================
const aiAPI = {
  _appliedDirectives: new Set(),

  /**
   * Fetch AI recommendation for a specific corridor dynamically.
   * Hits Intern 3's microservice: GET /api/v1/ai/recommendations?road_id={road_id} (port 8010)
   * Response schema contains: { road_id, recommendation_text, based_on }
   */
  async getRecommendationForRoad(roadId = 'R001') {
    const normalizedRoad = (roadId || 'R001').toUpperCase().trim();
    const urlsToTry = [
      `${API_CONFIG.AI_ENGINE_BASE}/api/v1/ai/recommendations?road_id=${encodeURIComponent(normalizedRoad)}`,
      `${API_CONFIG.AI_ENGINE_BASE}/ai/recommendations?road_id=${encodeURIComponent(normalizedRoad)}`,
    ];

    let liveData = null;
    for (const url of urlsToTry) {
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(3500) });
        if (res.ok) {
          liveData = await res.json();
          break;
        }
      } catch (err) {
        // Try next endpoint
      }
    }

    let recObj = null;
    if (Array.isArray(liveData) && liveData.length > 0) {
      recObj = liveData[0];
    } else if (liveData && (liveData.recommendation_text || liveData.recommendation)) {
      recObj = liveData;
    }

    if (recObj && (recObj.recommendation_text || recObj.recommendation)) {
      const text = recObj.recommendation_text || recObj.recommendation;
      const basedOn =
        recObj.based_on ||
        recObj.reason ||
        `Calculated from real-time speed, volume, and density telemetry for corridor ${normalizedRoad}.`;
      return {
        road_id: normalizedRoad,
        recommendation_text: text,
        based_on: basedOn,
        isLive: true,
        priority:
          normalizedRoad === 'R007' || normalizedRoad === 'R006'
            ? 'CRITICAL'
            : normalizedRoad === 'R005'
              ? 'HIGH'
              : 'MEDIUM',
        confidence_score: 0.94,
        confidence_pct: '94.2%',
        model_origin: 'Intern 3 AI Engine (Port 8010)',
        created_at: new Date().toISOString(),
      };
    }

    // M3 Day 5 Data-Informed Fallback per road
    const fallbackDatabase = {
      R001: {
        name: 'Main Expressway',
        text: 'Activate dynamic variable speed harmonics (VSL at 45 km/h) and stagger junction ramp metering at Milepost 14.2 to homogenize vehicle headway.',
        based_on:
          'Main Expressway peak vehicle volume approaching 28 veh/min with 14% speed deceleration and elevated High congestion count during diurnal surge.',
        priority: 'MEDIUM',
        confidence_pct: '91.5%',
        impact: { flow_recovery_pct: '+15%', delay_reduction_min: '4.0 min/veh', co2_saved_kg: 85 },
      },
      R002: {
        name: 'Central Avenue',
        text: 'Harmonize arterial green intervals (+12s outbound) and coordinate signal cycles across intersections C-04 to C-09 to ease queue buildup.',
        based_on:
          'Elevated stop-and-go queue formation detected with vehicle density at 18.2 veh/km and pedestrian crossing delay spikes.',
        priority: 'MEDIUM',
        confidence_pct: '88.7%',
        impact: { flow_recovery_pct: '+18%', delay_reduction_min: '5.2 min/veh', co2_saved_kg: 95 },
      },
      R003: {
        name: 'West Ring Road',
        text: 'Maintain nominal high-capacity bypass routing; advise heavy fleet transit through West Ring bypass to alleviate inner ring congestion.',
        based_on:
          'West Ring capacity surplus of 62% with steady 48 km/h average velocity; minimal conflict nodes.',
        priority: 'LOW',
        confidence_pct: '96.1%',
        impact: { flow_recovery_pct: '+8%', delay_reduction_min: '2.1 min/veh', co2_saved_kg: 40 },
      },
      R004: {
        name: 'North Boulevard',
        text: 'Standard telemetry monitoring active. Nominal green split cycles sufficient; no tactical diversion required.',
        based_on:
          'Free-flow conditions maintained with density below 5.0 veh/km and 60 km/h average cruise speed.',
        priority: 'LOW',
        confidence_pct: '97.4%',
        impact: { flow_recovery_pct: '+2%', delay_reduction_min: '0.5 min/veh', co2_saved_kg: 15 },
      },
      R005: {
        name: 'Industrial Highway',
        text: 'Enforce freight transit lane restrictions and adjust turning pocket phase timing at logistics node junctions.',
        based_on:
          'Heavy freight density accumulation reaching 21.5 veh/km with afternoon volume plateau and slower truck acceleration profiles.',
        priority: 'HIGH',
        confidence_pct: '89.8%',
        impact: {
          flow_recovery_pct: '+24%',
          delay_reduction_min: '7.8 min/veh',
          co2_saved_kg: 160,
        },
      },
      R006: {
        name: 'Airport Road',
        text: 'Extend green wave progression (+18s) along Airport Expressway north-south corridor to prevent queue spillback into terminal approach.',
        based_on:
          'Severe congestion probability of 78% detected from 55 veh/km density spike and drop in average speed to 12 km/h near terminal junction.',
        priority: 'CRITICAL',
        confidence_pct: '94.8%',
        impact: {
          flow_recovery_pct: '+28%',
          delay_reduction_min: '8.5 min/veh',
          co2_saved_kg: 140,
        },
      },
      R007: {
        name: 'Harbor Tunnel',
        text: 'Deploy dynamic VMS advisory to divert commercial traffic to R003 West Ring Road and restrict tunnel lane inflow.',
        based_on:
          'Severe bottleneck conditions at Harbor Tunnel approach with speed down to 6.5 km/h, density at 29.8 veh/km, and Severe readings dominating 84% of time-buckets.',
        priority: 'CRITICAL',
        confidence_pct: '96.4%',
        impact: {
          flow_recovery_pct: '+35%',
          delay_reduction_min: '14.2 min/veh',
          co2_saved_kg: 220,
        },
      },
    };

    const fallback = fallbackDatabase[normalizedRoad] || fallbackDatabase['R001'];
    return {
      road_id: normalizedRoad,
      recommendation_text: fallback.text,
      based_on: fallback.based_on,
      isLive: false,
      priority: fallback.priority,
      confidence_score: 0.92,
      confidence_pct: fallback.confidence_pct,
      model_origin: 'M3 Heuristics (Ready for Port 8010)',
      impact: fallback.impact,
      created_at: new Date().toISOString(),
    };
  },

  async getTacticalRecommendations(selectedRoadId = null) {
    if (selectedRoadId && selectedRoadId !== 'ALL') {
      const rec = await this.getRecommendationForRoad(selectedRoadId);
      const roadNames = {
        R001: 'Main Expressway',
        R002: 'Central Avenue',
        R003: 'West Ring Road',
        R004: 'North Boulevard',
        R005: 'Industrial Highway',
        R006: 'Airport Road',
        R007: 'Harbor Tunnel',
      };
      return [
        {
          id: `REC-AI-${rec.road_id}`,
          code: `DIR-${rec.road_id}`,
          type: 'autonomous-directive',
          title: `Dynamic Corridor Optimization (${rec.road_id})`,
          target_corridor: `${roadNames[rec.road_id] || rec.road_id} (${rec.road_id})`,
          sub_target: 'Telemetry Grid Segment',
          priority: rec.priority,
          confidence_score: rec.confidence_score || 0.93,
          confidence_pct: rec.confidence_pct,
          model_origin: rec.model_origin,
          recommendation_text: rec.recommendation_text,
          based_on: rec.based_on,
          rationale: `${rec.recommendation_text} Based on: ${rec.based_on}`,
          predicted_impact: rec.impact || {
            flow_recovery_pct: '+25%',
            delay_reduction_min: '8.0 min/veh',
            co2_saved_kg: 130,
          },
          action_label: `Deploy ${rec.road_id} Directive`,
          applied: this._appliedDirectives.has(`REC-AI-${rec.road_id}`),
          isLive: rec.isLive,
          created_at: rec.created_at,
        },
      ];
    }

    // Return batch recommendations for top critical corridors
    const defaultCorridors = ['R006', 'R007', 'R001'];
    const results = await Promise.all(
      defaultCorridors.map((id) => this.getRecommendationForRoad(id))
    );
    const roadNames = {
      R001: 'Main Expressway',
      R006: 'Airport Road',
      R007: 'Harbor Tunnel',
    };
    const actions = {
      R006: 'Extend Northbound Green Split (+18s)',
      R007: 'Deploy VMS Advisory & Fleet Divert',
      R001: 'Regulate VSL to 45 km/h',
    };
    return results.map((r) => ({
      id: `REC-AI-${r.road_id}`,
      code: `DIR-${r.road_id}`,
      type: 'autonomous-directive',
      title:
        r.road_id === 'R006'
          ? 'Dynamic Green-Wave Signal Offset'
          : r.road_id === 'R007'
            ? 'Commercial Fleet Heavy Traffic Diversion'
            : 'Dynamic Variable Speed Harmonics (VSL)',
      target_corridor: `${roadNames[r.road_id] || r.road_id} (${r.road_id})`,
      sub_target:
        r.road_id === 'R006'
          ? 'Intersections J-12 through J-15'
          : r.road_id === 'R007'
            ? 'Reroute via West Ring Road'
            : 'Milepost 14.2 - 18.0',
      priority: r.priority,
      confidence_score: r.confidence_score || 0.94,
      confidence_pct: r.confidence_pct,
      model_origin: r.model_origin,
      recommendation_text: r.recommendation_text,
      based_on: r.based_on,
      rationale: r.recommendation_text,
      predicted_impact: r.impact || {
        flow_recovery_pct: '+28%',
        delay_reduction_min: '8.5 min/veh',
        co2_saved_kg: 140,
      },
      action_label: actions[r.road_id] || `Deploy ${r.road_id} Directive`,
      applied: this._appliedDirectives.has(`REC-AI-${r.road_id}`),
      isLive: r.isLive,
      created_at: r.created_at,
    }));
  },

  async applyDirective(directiveId) {
    this._appliedDirectives.add(directiveId);
    NotificationManager.addNotification({
      id: `ACT-${Date.now()}`,
      category: 'ai',
      severity: 'info',
      title: `AI Directive ${directiveId} Deployed`,
      message: `Mitigation command applied successfully across grid controllers. Telemetry feedback loop initiated.`,
      time: 'Just now',
      unread: true,
    });
    return {
      success: true,
      directiveId,
      status: 'DEPLOYED_ACTIVE',
      timestamp: new Date().toISOString(),
    };
  },
};

// ==========================================
// Milestone 3: Analytics, Heatmap & Reports API (Intern 2)
// ==========================================
const analyticsAPI = {
  getKeyKPIs() {
    return {
      avg_network_speed: {
        value: 38.4,
        unit: 'km/h',
        change: '+4.2%',
        trend: 'up',
        label: 'vs 24h Prior',
      },
      congestion_index: {
        value: 42.1,
        max: 100,
        status: 'Moderate',
        change: '-12%',
        trend: 'down',
        label: 'Peak Easing',
      },
      peak_delay_surge: {
        value: 18.4,
        unit: 'min',
        worst_road: 'Harbor Tunnel (R007)',
        label: 'Max Bottleneck Delay',
      },
      ml_model_accuracy: {
        value: 94.2,
        unit: '%',
        model: 'XGBoost-M2',
        label: 'Chronological Test R²',
      },
      active_mitigations: { value: 3, label: 'Active AI Directives' },
    };
  },

  getHourlyTrends() {
    const hours = [
      '00:00',
      '01:00',
      '02:00',
      '03:00',
      '04:00',
      '05:00',
      '06:00',
      '07:00',
      '08:00',
      '09:00',
      '10:00',
      '11:00',
      '12:00',
      '13:00',
      '14:00',
      '15:00',
      '16:00',
      '17:00',
      '18:00',
      '19:00',
      '20:00',
      '21:00',
      '22:00',
      '23:00',
    ];

    const observedVolume = [
      45, 30, 22, 18, 25, 60, 140, 260, 310, 280, 210, 195, 220, 205, 190, 230, 290, 340, 325, 270,
      190, 130, 85, 55,
    ];

    const predictedVolume = [
      42, 28, 20, 19, 28, 65, 145, 255, 318, 275, 205, 200, 215, 210, 195, 235, 295, 335, 330, 265,
      185, 125, 80, 50,
    ];

    const avgSpeed = [
      58, 59, 60, 60, 58, 54, 46, 31, 24, 28, 42, 45, 41, 44, 46, 40, 32, 22, 25, 34, 45, 52, 55,
      57,
    ];

    const congestionThreshold = new Array(24).fill(250);

    return {
      hours,
      observedVolume,
      predictedVolume,
      avgSpeed,
      congestionThreshold,
    };
  },

  /**
   * Congestion Heatmap Visualization Service (Intern 2 endpoint)
   * GET /analytics/heatmap?start_date=2026-07-27&end_date=2026-08-23&time_bucket=hour
   * Returns: { source, time_bucket, roads, time_buckets, grid: [ { road_id, time_bucket, avg_vehicle_count, avg_speed_kmph, avg_density, max_density, congestion_score, congestion_level, total_readings, low_count, medium_count, high_count, severe_count } ] }
   */
  async getCongestionHeatmap(options = {}) {
    const { start_date = '2026-07-27', end_date = '2026-08-23', time_bucket = 'hour' } = options;

    const params = new URLSearchParams();
    if (start_date) params.append('start_date', start_date);
    if (end_date) params.append('end_date', end_date);
    if (time_bucket) params.append('time_bucket', time_bucket);

    const urlsToTry = [`${API_CONFIG.ANALYTICS_BASE}/analytics/heatmap?${params.toString()}`];

    for (const url of urlsToTry) {
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(4000) });
        if (res.ok) {
          const data = await res.json();
          if (data && data.grid && Array.isArray(data.grid)) {
            return {
              ...data,
              isLive: true,
            };
          }
        }
      } catch (err) {
        // Try fallback
      }
    }

    // High-Fidelity M3 Day 5 Data Fallback strictly conforming to Intern 2's schema
    return this.generateSyntheticHeatmap(time_bucket);
  },

  generateSyntheticHeatmap(_timeBucket = 'hour') {
    const roadProfiles = [
      {
        id: 'R001',
        name: 'Main Expressway',
        baseVol: 30,
        baseSpeed: 55,
        baseDensity: 7.5,
        peakBoost: 1.8,
      },
      {
        id: 'R002',
        name: 'Central Avenue',
        baseVol: 28,
        baseSpeed: 42,
        baseDensity: 9.0,
        peakBoost: 1.6,
      },
      {
        id: 'R003',
        name: 'West Ring Road',
        baseVol: 25,
        baseSpeed: 48,
        baseDensity: 6.8,
        peakBoost: 1.3,
      },
      {
        id: 'R004',
        name: 'North Boulevard',
        baseVol: 10,
        baseSpeed: 60,
        baseDensity: 2.5,
        peakBoost: 1.1,
      },
      {
        id: 'R005',
        name: 'Industrial Highway',
        baseVol: 35,
        baseSpeed: 30,
        baseDensity: 14.5,
        peakBoost: 1.7,
      },
      {
        id: 'R006',
        name: 'Airport Road',
        baseVol: 52,
        baseSpeed: 14,
        baseDensity: 22.8,
        peakBoost: 2.2,
      },
      {
        id: 'R007',
        name: 'Harbor Tunnel',
        baseVol: 65,
        baseSpeed: 7.2,
        baseDensity: 29.5,
        peakBoost: 2.4,
      },
    ];

    const roads = roadProfiles.map((r) => r.id);
    const time_buckets = Array.from({ length: 24 }, (_, i) => i);
    const grid = [];

    roadProfiles.forEach((rp) => {
      time_buckets.forEach((h) => {
        let hourFactor = 0.5;
        if ((h >= 7 && h <= 9) || (h >= 17 && h <= 19)) {
          hourFactor = rp.peakBoost;
        } else if (h >= 11 && h <= 15) {
          hourFactor = 1.1;
        } else if (h >= 22 || h <= 5) {
          hourFactor = 0.35;
        }

        const avg_vehicle_count = Math.max(2, Math.round(rp.baseVol * hourFactor * 10) / 10);
        const avg_density = Math.max(0.5, Math.round(rp.baseDensity * hourFactor * 10) / 10);
        const max_density = Math.round(avg_density * (1.15 + (h % 3) * 0.08) * 10) / 10;
        const avg_speed_kmph = Math.max(
          5.5,
          Math.round(Math.max(6, rp.baseSpeed - avg_density * 1.35) * 10) / 10
        );

        let total_readings = 28;
        let low_count = 0,
          medium_count = 0,
          high_count = 0,
          severe_count = 0;

        if (avg_density >= 26) {
          severe_count = 22;
          high_count = 5;
          medium_count = 1;
          low_count = 0;
        } else if (avg_density >= 18) {
          severe_count = 3;
          high_count = 19;
          medium_count = 5;
          low_count = 1;
        } else if (avg_density >= 9) {
          severe_count = 0;
          high_count = 3;
          medium_count = 20;
          low_count = 5;
        } else {
          severe_count = 0;
          high_count = 0;
          medium_count = 2;
          low_count = 26;
        }

        const counts = {
          Low: low_count,
          Medium: medium_count,
          High: high_count,
          Severe: severe_count,
        };
        const congestion_level = Object.keys(counts).reduce((a, b) =>
          counts[a] > counts[b] ? a : b
        );
        const score =
          Math.round(
            ((low_count * 1 + medium_count * 2 + high_count * 3 + severe_count * 4) /
              total_readings) *
              100
          ) / 100;

        grid.push({
          road_id: rp.id,
          road_name: rp.name,
          time_bucket: h,
          avg_vehicle_count,
          avg_speed_kmph,
          avg_density,
          max_density,
          congestion_score: score,
          congestion_level,
          total_readings,
          low_count,
          medium_count,
          high_count,
          severe_count,
        });
      });
    });

    return {
      source: 'M2 traffic_history (Client Fallback)',
      time_bucket: 'hour',
      roads,
      time_buckets,
      grid,
      isLive: false,
    };
  },

  getSpatialTemporalHeatmap() {
    return this.generateSyntheticHeatmap('hour');
  },

  /**
   * Download Historical Report (Intern 2 endpoint)
   * GET /analytics/reports?road_id={road_id}&start_date={start_date}&end_date={end_date}&limit={limit}
   * Returns CSV text attachment.
   */
  async downloadHistoricalReport(options = {}) {
    const {
      road_id = null,
      start_date = '2026-07-27',
      end_date = '2026-08-23',
      limit = 10000,
    } = options;

    const params = new URLSearchParams();
    if (road_id && road_id !== 'ALL') params.append('road_id', road_id);
    if (start_date) params.append('start_date', start_date);
    if (end_date) params.append('end_date', end_date);
    if (limit) params.append('limit', limit);

    const urlsToTry = [`${API_CONFIG.ANALYTICS_BASE}/analytics/reports?${params.toString()}`];

    let csvData = null;
    let rowCount = 0;
    let isLive = false;

    for (const url of urlsToTry) {
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(6000) });
        if (res.ok) {
          csvData = await res.text();
          const countHeader = res.headers.get('X-Report-Row-Count');
          rowCount = countHeader ? parseInt(countHeader, 10) : csvData.split('\n').length - 1;
          isLive = true;
          break;
        }
      } catch (err) {
        // Try fallback
      }
    }

    const safeRoad = road_id && road_id !== 'ALL' ? road_id : 'all_corridors';
    const filename = `traffic_historical_report_${safeRoad}_${start_date}_to_${end_date}.csv`;

    if (!csvData) {
      // Generate full CSV strictly adhering to Intern 2 M3 Day 5 schema:
      // road_id,sensor_id,reading_timestamp,vehicle_count,avg_speed_kmph,road_capacity,traffic_density_vehicles_per_km,congestion_level,latitude,longitude,source
      const roadsToInclude =
        road_id && road_id !== 'ALL'
          ? [road_id]
          : ['R001', 'R002', 'R003', 'R004', 'R005', 'R006', 'R007'];
      const coords = {
        R001: [12.9716, 77.5946, 320],
        R002: [12.982, 77.608, 220],
        R003: [12.9352, 77.534, 280],
        R004: [13.0358, 77.597, 180],
        R005: [12.899, 77.671, 260],
        R006: [13.1986, 77.7066, 240],
        R007: [12.942, 77.622, 210],
      };

      let rows = [
        'road_id,sensor_id,reading_timestamp,vehicle_count,avg_speed_kmph,road_capacity,traffic_density_vehicles_per_km,congestion_level,latitude,longitude,source',
      ];

      const startDt = new Date(start_date || '2026-07-27');
      const endDt = new Date(end_date || '2026-08-23');
      const oneHour = 60 * 60 * 1000;
      let current = new Date(startDt.getTime());
      let generatedCount = 0;
      const maxRows = Math.min(Number(limit) || 10000, 2500);

      while (current <= endDt && generatedCount < maxRows) {
        const tsStr = current.toISOString();
        const hour = current.getHours();

        for (const rId of roadsToInclude) {
          if (generatedCount >= maxRows) break;
          const [lat, lon, cap] = coords[rId] || [12.97, 77.59, 200];
          const isPeak = (hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 20);
          const factor = isPeak ? 1.8 : hour >= 23 || hour <= 5 ? 0.4 : 1.0;
          const vehCount = Math.round(cap * 0.12 * factor + (generatedCount % 7));
          const density = Math.round((vehCount / 4.5) * 10) / 10;
          const speed = Math.max(6.0, Math.round((65 - density * 1.5) * 10) / 10);
          let level = 'Low';
          if (density >= 26) level = 'Severe';
          else if (density >= 18) level = 'High';
          else if (density >= 9) level = 'Medium';

          rows.push(
            `${rId},SENS-${rId}-01,${tsStr},${vehCount},${speed},${cap},${density},${level},${lat},${lon},M2_history_dataset`
          );
          generatedCount++;
        }

        current = new Date(current.getTime() + 4 * oneHour);
      }

      csvData = rows.join('\n');
      rowCount = rows.length - 1;
      isLive = false;
    }

    // Trigger file download
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return {
      success: true,
      filename,
      rowCount,
      isLive,
    };
  },

  exportCSV() {
    return this.downloadHistoricalReport();
  },
};

// ==========================================
// Alerts API – Real Backend Integration
// ==========================================
const alertsAPI = {
  /**
   * GET /api/v1/alerts/my
   * Returns the current user's alert list from the backend.
   * Requires a valid Bearer token in sessionStorage.
   */
  async getMyAlerts() {
    return await apiFetch('/alerts/my');
  },

  /**
   * PATCH /api/v1/alerts/{alert_id}/read
   * Marks a single alert as read on the backend.
   */
  async markAsRead(alertId) {
    return await apiFetch(`/alerts/${alertId}/read`, { method: 'PATCH' });
  },
};

// ==========================================
// Milestone 3: Centralized Notification Manager
// ==========================================
const NotificationManager = {
  STORAGE_KEY: 'tv_notifications_state_v1',
  _listeners: [],
  _notifications: [],

  /**
   * Initialise the store:
   *  1. Immediately show whatever is cached in sessionStorage so the UI
   *     isn't blank while the network call is in flight.
   *  2. Fetch fresh data from GET /api/v1/alerts/my and replace the store.
   *  3. Fall back to seeded mock data when the backend is unreachable.
   */
  init() {
    // Hydrate from cache first for instant UI
    try {
      const saved = sessionStorage.getItem(this.STORAGE_KEY);
      if (saved) {
        this._notifications = JSON.parse(saved);
        this._notifyListeners();
      }
    } catch (_) {
      /* ignore */
    }

    // Fetch live data from the real API
    this._fetchFromAPI();
  },

  async _fetchFromAPI() {
    try {
      const raw = await alertsAPI.getMyAlerts();
      // Normalise the backend payload into the internal notification shape.
      // Backend sends: alert_id, type, severity, road_id, message, read, created_at
      const normalised = (Array.isArray(raw) ? raw : raw.alerts || raw.data || []).map((a) => ({
        id: String(a.id || a.alert_id || `NOTIF-${Date.now()}-${Math.random()}`),
        // Backend sends `type` (e.g. "accident") – map it to `category`
        category: a.category || a.type || a.alert_type || 'general',
        severity: a.severity || a.level || 'info',
        title: a.title || a.message || 'Alert',
        // Backend sends `road_id` (e.g. "R003") – map it to `location`
        location: a.location || a.road_name || a.corridor || a.road_id || 'Grid',
        message: a.message || a.description || a.details || '',
        time: a.created_at ? _relativeTime(a.created_at) : a.time || 'Just now',
        unread: a.is_read === false || a.read === false || a.unread === true,
        action: a.action || { label: 'View Alerts', url: 'Alerts.html' },
      }));

      if (normalised.length > 0) {
        this._notifications = normalised;
      } else if (this._notifications.length === 0) {
        // API returned empty list and cache was also empty – show mock
        this.seedDefaultNotifications();
        return;
      }
      this.persist();
    } catch (err) {
      console.warn(
        '[AlertsAPI] Could not reach GET /alerts/my – using fallback data.',
        err.message
      );
      // Only seed mock data if we have nothing in cache
      if (this._notifications.length === 0) {
        this.seedDefaultNotifications();
      } else {
        // Listeners haven't been notified yet after the cache load
        this._notifyListeners();
      }
    }
  },

  seedDefaultNotifications() {
    this._notifications = [
      {
        id: 'NOTIF-101',
        category: 'critical',
        severity: 'severe',
        title: 'Severe Bottleneck Gridlock',
        location: 'Harbor Tunnel Approach (R007)',
        message:
          'Flow reduced by 75%. Density peaked at 29.8 veh/km with speeds below 6.5 km/h. Automated diversion routes suggested.',
        time: 'Just now',
        unread: true,
        action: { label: 'View Alerts', url: 'Alerts.html' },
      },
      {
        id: 'NOTIF-102',
        category: 'ai',
        severity: 'info',
        title: 'AI Tactical Directive Generated',
        location: 'Airport Road (R006)',
        message:
          'XGBoost Model-v1 recommends +18s green-split offset on J-12..J-15 to absorb upcoming rush queue (Confidence: 94.8%).',
        time: '3m ago',
        unread: true,
        action: { label: 'Review Advisory', url: 'Alerts.html' },
      },
      {
        id: 'NOTIF-103',
        category: 'critical',
        severity: 'critical',
        title: 'Accident & Corridor Stoppage',
        location: 'Central Avenue (R002)',
        message:
          'Slow vehicle stoppage reported near Tech Park off-ramp. Highway patrol unit TV-02 dispatched.',
        time: '9m ago',
        unread: true,
        action: { label: 'Track Unit', url: 'Alerts.html' },
      },
      {
        id: 'NOTIF-104',
        category: 'roadworks',
        severity: 'warning',
        title: 'Lane Restriction & Maintenance',
        location: 'Industrial Highway (R005)',
        message:
          'Right lane closed at Milepost 8.2 for sensor maintenance. Capacity throttled by 25%.',
        time: '24m ago',
        unread: true,
        action: { label: 'Inspect Corridor', url: 'route-analysis.html' },
      },
      {
        id: 'NOTIF-105',
        category: 'general',
        severity: 'info',
        title: 'M2 Model Checkpoint Synced',
        location: 'Grid AI Engine',
        message:
          'Chronological validation accuracy verified at 94.2% across all 7 monitored metropolitan corridors.',
        time: '45m ago',
        unread: false,
        action: { label: 'Open Analytics', url: 'analytics.html' },
      },
    ];
    this.persist();
  },

  persist() {
    try {
      sessionStorage.setItem(this.STORAGE_KEY, JSON.stringify(this._notifications));
    } catch (e) {
      // Memory fallback
    }
    this._notifyListeners();
  },

  getNotifications(category = 'all') {
    if (category === 'all') return this._notifications;
    if (category === 'unread') return this._notifications.filter((n) => n.unread);
    if (category === 'critical')
      return this._notifications.filter(
        (n) => n.severity === 'severe' || n.severity === 'critical' || n.category === 'critical'
      );
    if (category === 'ai')
      return this._notifications.filter((n) => n.category === 'ai' || n.type === 'ai-advisory');
    return this._notifications.filter((n) => n.category === category || n.severity === category);
  },

  getUnreadCount() {
    return this._notifications.filter((n) => n.unread).length;
  },

  canAcknowledge() {
    return ['OPERATOR', 'ADMIN'].includes(AuthManager.getRole());
  },

  markAsRead(id) {
    if (!this.canAcknowledge()) return;
    const item = this._notifications.find((n) => n.id === id);
    if (item) {
      item.unread = false;
      this.persist();
    }
    // Fire-and-forget PATCH to the real backend
    alertsAPI
      .markAsRead(id)
      .catch((err) => console.warn(`[AlertsAPI] PATCH /alerts/${id}/read failed:`, err.message));
  },

  markAllAsRead() {
    if (!this.canAcknowledge()) return;
    this._notifications
      .filter((n) => n.unread)
      .forEach((n) => {
        alertsAPI
          .markAsRead(n.id)
          .catch((err) =>
            console.warn(`[AlertsAPI] PATCH /alerts/${n.id}/read failed:`, err.message)
          );
        n.unread = false;
      });
    this.persist();
  },

  dismiss(id) {
    this._notifications = this._notifications.filter((n) => n.id !== id);
    this.persist();
  },

  clearAll() {
    this._notifications = [];
    this.persist();
  },

  addNotification(notif) {
    this._notifications.unshift({
      id: notif.id || `NOTIF-${Date.now()}`,
      category: notif.category || 'general',
      severity: notif.severity || 'info',
      title: notif.title || 'Grid Update',
      location: notif.location || 'Autonomous Grid',
      message: notif.message || '',
      time: notif.time || 'Just now',
      unread: true,
      action: notif.action || { label: 'View Alerts', url: 'Alerts.html' },
    });
    this.persist();
  },

  subscribe(callback) {
    if (typeof callback === 'function') {
      this._listeners.push(callback);
      callback(this._notifications, this.getUnreadCount());
    }
  },

  _notifyListeners() {
    const unread = this.getUnreadCount();
    this._listeners.forEach((cb) => {
      try {
        cb(this._notifications, unread);
      } catch (e) {
        console.error(e);
      }
    });
  },
};

// Initialize Notification Store
NotificationManager.init();

// ==========================================
// Milestone 3: Global Notification Bell UI Mount
// ==========================================
const NotificationBellUI = {
  isOpen: false,
  activeFilter: 'all',

  mount() {
    // Ensure toast container exists
    if (!document.getElementById('toast-container')) {
      const tc = document.createElement('div');
      tc.id = 'toast-container';
      tc.className =
        'fixed bottom-20 md:bottom-8 right-6 z-50 flex flex-col gap-2 pointer-events-none';
      document.body.appendChild(tc);
    }

    // Look for existing bell button or inject into header
    let bellBtn = document.getElementById('nav-notification-bell-btn');
    if (!bellBtn) {
      const header = document.querySelector('header');
      if (header) {
        // Find utility container on the right
        const rightControls =
          header.querySelector('div.flex.items-center:last-child') ||
          header.querySelector('button[title*="Theme"]')?.parentElement;
        if (rightControls) {
          const bellWrapper = document.createElement('div');
          bellWrapper.className = 'relative flex items-center';
          bellWrapper.innerHTML = `
                        <button id="nav-notification-bell-btn" class="relative w-9 h-9 rounded-xl bg-surface-container-high/80 hover:bg-surface-container-highest border border-white/10 flex items-center justify-center text-on-surface-variant hover:text-on-surface transition-all focus:outline-none" title="Notifications & Incident Alerts">
                            <span class="material-symbols-outlined text-[20px]">notifications</span>
                            <span id="nav-bell-badge" class="hidden absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-[#e11d48] text-white text-[10px] font-bold flex items-center justify-center border-2 border-[#0b1326] shadow-[0_0_8px_rgba(225,29,72,0.6)] animate-pulse">0</span>
                        </button>
                    `;
          // Insert before theme toggle if present, otherwise as first child
          const themeBtn = rightControls.querySelector(
            'button[title*="Theme"], button[onclick*="toggle"]'
          );
          if (themeBtn) {
            rightControls.insertBefore(bellWrapper, themeBtn);
          } else {
            rightControls.insertBefore(bellWrapper, rightControls.firstChild);
          }
          bellBtn = document.getElementById('nav-notification-bell-btn');
        }
      }
    }

    // Build Drawer / Dropdown DOM
    if (!document.getElementById('notification-drawer')) {
      const drawer = document.createElement('div');
      drawer.id = 'notification-drawer';
      drawer.className =
        'hidden fixed top-16 right-4 sm:right-6 md:right-8 w-[92vw] sm:w-[420px] max-w-[440px] z-50 rounded-2xl glass-panel border border-white/15 shadow-[0_16px_48px_rgba(0,0,0,0.7)] backdrop-blur-2xl flex flex-col overflow-hidden transition-all duration-200';
      drawer.innerHTML = `
                <!-- Header -->
                <div class="p-4 border-b border-white/10 flex items-center justify-between bg-surface-container/70">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-lg bg-secondary/15 border border-secondary/30 flex items-center justify-center text-secondary">
                            <span class="material-symbols-outlined text-[18px]">notifications_active</span>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="font-headline-lg text-sm font-bold text-on-surface">GRID ALERTS</span>
                                <span id="drawer-unread-pill" class="text-[10px] font-label-sm font-bold px-2 py-0.5 rounded-full bg-[#e11d48]/20 text-rose-300 border border-[#e11d48]/30">0 New</span>
                            </div>
                            <div class="text-[10px] font-label-sm text-on-surface-variant">Live Dispatch & Telemetry Stream</div>
                        </div>
                    </div>
                    <div class="flex items-center gap-1">
                        ${NotificationManager.canAcknowledge() ? '<button onclick="NotificationManager.markAllAsRead()" class="text-[11px] font-label-sm text-on-surface-variant hover:text-secondary px-2 py-1 rounded hover:bg-white/5 transition-all" title="Mark all notifications as read">Mark All Read</button>' : ''}
                        <button onclick="NotificationBellUI.toggle(false)" class="w-7 h-7 rounded-lg hover:bg-white/10 text-on-surface-variant hover:text-on-surface flex items-center justify-center transition-all">
                            <span class="material-symbols-outlined text-[18px]">close</span>
                        </button>
                    </div>
                </div>

                <!-- Filter Tabs with Badges -->
                <div class="flex items-center gap-1 p-2 border-b border-white/5 bg-surface-container-low/50 font-label-sm">
                    <button class="notif-filter-tab active text-[11px] px-3 py-1.5 rounded-lg bg-primary-container text-on-primary-container font-semibold transition-all flex items-center gap-1.5" data-tab="all" onclick="NotificationBellUI.setTab('all', this)">
                        <span>All</span>
                        <span id="tab-count-all" class="text-[10px] opacity-75"></span>
                    </button>
                    <button class="notif-filter-tab text-[11px] px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-all flex items-center gap-1.5" data-tab="critical" onclick="NotificationBellUI.setTab('critical', this)">
                        <span>Critical</span>
                        <span id="tab-count-critical" class="text-[10px] opacity-75"></span>
                    </button>
                    <button class="notif-filter-tab text-[11px] px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-all flex items-center gap-1.5" data-tab="ai" onclick="NotificationBellUI.setTab('ai', this)">
                        <span>AI Directives</span>
                        <span id="tab-count-ai" class="text-[10px] opacity-75"></span>
                    </button>
                </div>

                <!-- Notification Feed List -->
                <div id="drawer-notif-list" class="max-h-[390px] overflow-y-auto p-3 flex flex-col gap-2.5 divide-y divide-white/5">
                    <div class="text-center py-8 text-on-surface-variant text-xs font-label-sm">No new notifications</div>
                </div>

                <!-- Footer Link to Alerts -->
                <div class="p-3 border-t border-white/10 bg-surface-container/90 flex items-center justify-between">
                    <a href="Alerts.html" class="text-xs font-label-sm font-semibold text-secondary hover:text-white flex items-center gap-1 transition-all">
                        <span>Open Incident Command Center</span>
                        <span class="material-symbols-outlined text-[15px]">arrow_forward</span>
                    </a>
                    <button onclick="NotificationManager.clearAll()" class="text-[11px] font-label-sm text-on-surface-variant hover:text-error transition-all">Clear All</button>
                </div>
            `;
      document.body.appendChild(drawer);
    }

    // Attach click listener to bell button
    if (bellBtn) {
      bellBtn.onclick = (e) => {
        e.stopPropagation();
        NotificationBellUI.toggle();
      };
    }

    // Close on outside click
    document.addEventListener('click', (e) => {
      const drawer = document.getElementById('notification-drawer');
      const bell = document.getElementById('nav-notification-bell-btn');
      if (
        NotificationBellUI.isOpen &&
        drawer &&
        !drawer.contains(e.target) &&
        bell &&
        !bell.contains(e.target)
      ) {
        NotificationBellUI.toggle(false);
      }
    });

    // Subscribe to NotificationManager state
    NotificationManager.subscribe((notifs, unreadCount) => {
      NotificationBellUI.updateBadge(unreadCount);
      NotificationBellUI.updateTabCounts(notifs);
      NotificationBellUI.renderList(notifs);
    });

    // Poll the real API every 60 seconds to surface new alerts automatically
    this._pollInterval = setInterval(() => {
      NotificationManager._fetchFromAPI();
    }, 60000);
  },

  toggle(forceState) {
    const drawer = document.getElementById('notification-drawer');
    if (!drawer) return;
    this.isOpen = forceState !== undefined ? forceState : !this.isOpen;
    if (this.isOpen) {
      drawer.classList.remove('hidden');
    } else {
      drawer.classList.add('hidden');
    }
  },

  setTab(tab, btnEl) {
    this.activeFilter = tab;
    document.querySelectorAll('.notif-filter-tab').forEach((b) => {
      b.classList.remove(
        'active',
        'bg-primary-container',
        'text-on-primary-container',
        'font-semibold'
      );
      b.classList.add('text-on-surface-variant');
    });
    if (btnEl) {
      btnEl.classList.add(
        'active',
        'bg-primary-container',
        'text-on-primary-container',
        'font-semibold'
      );
      btnEl.classList.remove('text-on-surface-variant');
    }
    this.renderList(NotificationManager.getNotifications(tab));
  },

  updateBadge(unreadCount) {
    const badge = document.getElementById('nav-bell-badge');
    const pill = document.getElementById('drawer-unread-pill');
    if (badge) {
      if (unreadCount > 0) {
        badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    }
    if (pill) {
      pill.textContent = `${unreadCount} Unread`;
    }
  },

  updateTabCounts(notifs) {
    const countAll = notifs.length;
    const countCrit = notifs.filter(
      (n) => n.severity === 'severe' || n.severity === 'critical' || n.category === 'critical'
    ).length;
    const countAi = notifs.filter((n) => n.category === 'ai' || n.type === 'ai-advisory').length;

    const elAll = document.getElementById('tab-count-all');
    const elCrit = document.getElementById('tab-count-critical');
    const elAi = document.getElementById('tab-count-ai');

    if (elAll) elAll.textContent = `(${countAll})`;
    if (elCrit) elCrit.textContent = `(${countCrit})`;
    if (elAi) elAi.textContent = `(${countAi})`;
  },

  renderList(notifs) {
    const container = document.getElementById('drawer-notif-list');
    if (!container) return;
    const canAcknowledge = NotificationManager.canAcknowledge();

    let filtered = notifs;
    if (this.activeFilter === 'critical') {
      filtered = notifs.filter(
        (n) => n.severity === 'severe' || n.severity === 'critical' || n.category === 'critical'
      );
    } else if (this.activeFilter === 'ai') {
      filtered = notifs.filter((n) => n.category === 'ai' || n.type === 'ai-advisory');
    }

    if (!filtered.length) {
      container.innerHTML = `
                <div class="text-center py-10 text-on-surface-variant text-xs font-label-sm flex flex-col items-center gap-2">
                    <span class="material-symbols-outlined text-3xl text-on-surface-variant/30">notifications_off</span>
                    <span>No incidents or advisories in this category</span>
                </div>
            `;
      return;
    }

    container.innerHTML = filtered
      .map((n) => {
        const isCritical = n.severity === 'severe' || n.severity === 'critical';
        const isWarning = n.severity === 'warning';
        const isAi = n.category === 'ai';

        let icon = 'info';
        let iconColor = 'text-secondary';
        let borderAccent = 'border-l-4 border-l-secondary';
        let bgSeverity = 'bg-surface-container-high/40';

        if (isCritical) {
          icon = 'emergency';
          iconColor = 'text-[#e11d48]';
          borderAccent = 'border-l-4 border-l-[#e11d48] shadow-[0_0_12px_rgba(225,29,72,0.2)]';
          bgSeverity = 'bg-rose-950/20';
        } else if (isAi) {
          icon = 'smart_toy';
          iconColor = 'text-tertiary';
          borderAccent = 'border-l-4 border-l-tertiary shadow-[0_0_12px_rgba(205,189,255,0.15)]';
          bgSeverity = 'bg-tertiary-container/20';
        } else if (isWarning) {
          icon = 'construction';
          iconColor = 'text-yellow-400';
          borderAccent = 'border-l-4 border-l-yellow-400';
          bgSeverity = 'bg-yellow-950/15';
        }

        return `
                <div class="p-3 rounded-xl ${borderAccent} ${bgSeverity} hover:bg-white/5 transition-all ${n.unread ? 'border border-white/10' : 'opacity-65'}">
                    <div class="flex items-start justify-between gap-2">
                        <div class="flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-[17px] ${iconColor}">${icon}</span>
                            <span class="text-xs font-bold font-body-md text-on-surface">${n.title}</span>
                        </div>
                        <div class="flex items-center gap-1">
                            <span class="text-[10px] font-label-sm text-on-surface-variant whitespace-nowrap">${n.time}</span>
                            <button onclick="NotificationManager.dismiss('${n.id}')" class="text-on-surface-variant hover:text-error p-0.5" title="Dismiss">
                                <span class="material-symbols-outlined text-[13px]">close</span>
                            </button>
                        </div>
                    </div>
                    <div class="text-[11px] font-label-sm text-secondary/90 mt-0.5 flex items-center gap-1">
                        <span class="material-symbols-outlined text-[12px]">location_on</span>
                        <span>${n.location}</span>
                    </div>
                    <p class="text-xs text-on-surface-variant mt-1.5 leading-relaxed font-body-md">${n.message}</p>
                    <div class="flex items-center justify-between mt-2.5 pt-2 border-t border-white/5">
                        <a href="${n.action?.url || 'Alerts.html'}" ${canAcknowledge ? `onclick="NotificationManager.markAsRead('${n.id}')"` : ''} class="text-[11px] font-label-sm font-semibold text-secondary hover:text-white flex items-center gap-1 transition-all">
                            <span>${n.action?.label || 'Inspect'}</span>
                            <span class="material-symbols-outlined text-[13px]">open_in_new</span>
                        </a>
                        <div class="flex items-center gap-2">
                            ${
                              canAcknowledge && n.unread
                                ? `
                                <button onclick="NotificationManager.markAsRead('${n.id}')" class="text-[10px] font-label-sm text-on-surface-variant hover:text-emerald-300 transition-colors flex items-center gap-0.5">
                                    <span class="material-symbols-outlined text-[12px]">check</span>
                                    <span>Acknowledge</span>
                                </button>
                            `
                                : canAcknowledge
                                  ? `
                                <span class="text-[10px] font-label-sm text-emerald-400/90 flex items-center gap-0.5">
                                    <span class="material-symbols-outlined text-[12px]">done_all</span>
                                    <span>Read</span>
                                </span>
                            `
                                  : ''
                            }
                        </div>
                    </div>
                </div>
            `;
      })
      .join('');
  },
};

// ==========================================
// Auto-sync navigation links and user profile badges on load
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  const role = AuthManager.getRole() || 'OPERATOR';
  const userName =
    AuthManager.getUserName() || role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
  const dashUrl = AuthManager.getDashboardUrl();

  document.querySelectorAll('.nav-home-link').forEach((el) => {
    el.href = dashUrl;
  });

  const nameEl = document.getElementById('nav-user-name');
  if (nameEl) nameEl.textContent = userName;

  const roleEl = document.getElementById('nav-user-role');
  if (roleEl) roleEl.textContent = role;

  // Redundant admin link handling
  document.querySelectorAll('.nav-admin-only').forEach((el) => {
    el.classList.add('hidden');
  });

  // Mount Notification Bell UI across all pages
  NotificationBellUI.mount();

  // Mount Theme Manager
  ThemeManager.init();
});

// ==========================================
// Centralized Theme Manager (Dark / Light)
// ==========================================
const ThemeManager = {
  STORAGE_KEY: 'trafficvision_theme',

  getTheme() {
    try {
      return localStorage.getItem(this.STORAGE_KEY) || 'dark';
    } catch (_) {
      return 'dark';
    }
  },

  setTheme(theme) {
    try {
      localStorage.setItem(this.STORAGE_KEY, theme);
    } catch (_) {
      // storage unavailable (e.g. private mode): keep defaults
    }
    this.apply(theme);
  },

  toggle() {
    const next = this.getTheme() === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
    return next;
  },

  ensureStyles() {
    if (typeof document === 'undefined' || !document.head) return;
    if (document.getElementById('tv-theme-global-styles')) return;
    const style = document.createElement('style');
    style.id = 'tv-theme-global-styles';
    style.textContent = `
            /* Smooth theme transition */
            body, header, nav, .glass-panel, .glass-card, input, select, textarea, button {
                transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
            }

            /* Light theme overrides for entire TrafficVision suite */
            html.light body {
                background-color: #f1f5f9 !important;
                color: #0f172a !important;
            }

            /* Header */
            html.light header {
                background-color: rgba(255, 255, 255, 0.92) !important;
                border-color: #e2e8f0 !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
            }
            html.light header nav {
                background-color: #f8fafc !important;
                border-color: #e2e8f0 !important;
            }
            html.light header nav a:not(.bg-secondary\\/15) {
                color: #475569 !important;
            }
            html.light header nav a:not(.bg-secondary\\/15):hover {
                color: #0f172a !important;
                background-color: #e2e8f0 !important;
            }
            html.light header nav a.bg-secondary\\/15,
            html.light header nav a.text-secondary {
                background-color: #e0f2fe !important;
                color: #0284c7 !important;
                border-color: #bae6fd !important;
            }
            html.light header button,
            html.light .theme-toggle-btn {
                background-color: #f1f5f9 !important;
                border-color: #cbd5e1 !important;
                color: #475569 !important;
            }
            html.light header button:hover,
            html.light .theme-toggle-btn:hover {
                background-color: #e2e8f0 !important;
                color: #0f172a !important;
            }
            html.light #nav-user-name {
                color: #0f172a !important;
            }

            /* Panels, Cards & Containers */
            html.light .glass-panel,
            html.light .glass-card {
                background: #ffffff !important;
                border-color: #e2e8f0 !important;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06) !important;
                color: #0f172a !important;
            }
            html.light .bg-surface-container,
            html.light .bg-surface-container-high,
            html.light .bg-surface-container-highest,
            html.light .bg-surface-container-low,
            html.light .bg-surface-variant {
                background-color: #f8fafc !important;
                border-color: #e2e8f0 !important;
            }

            html.light .text-on-surface {
                color: #0f172a !important;
            }
            html.light .text-on-surface-variant {
                color: #475569 !important;
            }

            /* Inputs & Controls */
            html.light input:not([type="checkbox"]):not([type="radio"]),
            html.light select,
            html.light textarea {
                background-color: #ffffff !important;
                border-color: #cbd5e1 !important;
                color: #0f172a !important;
            }
            html.light input::placeholder {
                color: #94a3b8 !important;
            }

            /* Mobile Bottom Bar */
            html.light nav.fixed.bottom-0,
            html.light nav.md\\:hidden {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-color: #e2e8f0 !important;
                box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.06) !important;
            }
            html.light nav.fixed.bottom-0 a,
            html.light nav.md\\:hidden a {
                color: #64748b !important;
            }
            html.light nav.fixed.bottom-0 a.text-secondary,
            html.light nav.md\\:hidden a.text-secondary {
                color: #0284c7 !important;
                background-color: #e0f2fe !important;
            }

            /* Notification Drawer */
            html.light #notification-drawer {
                background: #ffffff !important;
                border-color: #e2e8f0 !important;
                box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12) !important;
                color: #0f172a !important;
            }
            html.light .notification-item:hover {
                background-color: #f8fafc !important;
            }

            /* Common border utilities */
            html.light .border-white\\/10,
            html.light .border-white\\/5,
            html.light .border-white\\/15,
            html.light .border-white\\/20 {
                border-color: #e2e8f0 !important;
            }
            html.light .border-outline-variant {
                border-color: #cbd5e1 !important;
            }
        `;
    document.head.appendChild(style);
  },

  apply(theme) {
    const isDark = theme === 'dark';
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.remove('dark');
      root.classList.add('light');
    }

    this.ensureStyles();

    // Update all theme toggle buttons across the UI
    document
      .querySelectorAll('button[title*="Theme"], .theme-toggle-btn, #theme-toggle-btn')
      .forEach((btn) => {
        btn.setAttribute('title', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
        btn.setAttribute('aria-label', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon) {
          icon.textContent = isDark ? 'light_mode' : 'dark_mode';
        }
      });
  },

  init() {
    const theme = this.getTheme();
    this.apply(theme);

    // Bind any theme toggle buttons on page
    document
      .querySelectorAll(
        'button[title*="Theme"], button[onclick*="classList.toggle"], .theme-toggle-btn, #theme-toggle-btn'
      )
      .forEach((btn) => {
        btn.onclick = (e) => {
          e.preventDefault();
          ThemeManager.toggle();
        };
      });
  },
};

// Immediate invocation to ensure early theme synchronization
try {
  ThemeManager.apply(ThemeManager.getTheme());
} catch (_) {
  // storage unavailable (e.g. private mode): keep defaults
}

window.ThemeManager = ThemeManager;
window.toggleTheme = () => ThemeManager.toggle();

// ==========================================
// Helper – human-readable relative time
// ==========================================
function _relativeTime(isoString) {
  try {
    const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  } catch (_) {
    return 'Recently';
  }
}
