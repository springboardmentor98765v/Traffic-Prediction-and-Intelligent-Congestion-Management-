/**
 * TrafficVision AI - Centralized API Client & Frontend Utilities
 * Supports live backend communication with automatic fallback aligned with Day 6 Traffic Monitoring specs.
 */

const API_CONFIG = {
    BASE_URL: 'http://localhost:8001/api/v1',
    TIMEOUT: 5000
};

// ==========================================
// Mock Fallback Data (Day 6 Schema Aligned)
// ==========================================
const MOCK_TRAFFIC_DATA = [
    {
        road_id: "R001",
        road_name: "Main Expressway",
        vehicle_count: 28,
        density: 5.6,
        avg_speed_kmph: 55.0,
        speed: "55 km/h",
        congestion_level: "Low",
        updated_at: new Date().toISOString()
    },
    {
        road_id: "R002",
        road_name: "Central Avenue",
        vehicle_count: 27,
        density: 6.75,
        avg_speed_kmph: 42.0,
        speed: "42 km/h",
        congestion_level: "Low",
        updated_at: new Date().toISOString()
    },
    {
        road_id: "R003",
        road_name: "West Ring Road",
        vehicle_count: 26,
        density: 7.43,
        avg_speed_kmph: 48.0,
        speed: "48 km/h",
        congestion_level: "Low",
        updated_at: new Date().toISOString()
    },
    {
        road_id: "R004",
        road_name: "North Boulevard",
        vehicle_count: 1,
        density: 0.22,
        avg_speed_kmph: 60.0,
        speed: "60 km/h",
        congestion_level: "Low",
        updated_at: new Date().toISOString()
    },
    {
        road_id: "R005",
        road_name: "Industrial Highway",
        vehicle_count: 34,
        density: 11.33,
        avg_speed_kmph: 28.5,
        speed: "28 km/h",
        congestion_level: "Medium",
        updated_at: new Date().toISOString()
    },
    {
        road_id: "R006",
        road_name: "Airport Road",
        vehicle_count: 55,
        density: 22.4,
        avg_speed_kmph: 12.0,
        speed: "12 km/h",
        congestion_level: "High",
        updated_at: new Date().toISOString()
    },
    {
        road_id: "R007",
        road_name: "Harbor Tunnel Approach",
        vehicle_count: 68,
        density: 29.8,
        avg_speed_kmph: 6.5,
        speed: "6 km/h",
        congestion_level: "Severe",
        updated_at: new Date().toISOString()
    }
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
    avg_delay: "+5.4m",
    timestamp: new Date().toISOString()
};

// ==========================================
// Data Normalization & Badge Helpers
// ==========================================
function normalizeDensitySummary(data) {
    if (!data) return MOCK_DENSITY_SUMMARY;

    const totalRoads = data.total_roads ?? data.total_roads_monitored ?? 6;
    const avgDensity = Number(data.average_density ?? data.average_network_density ?? 8.95);
    const maxDensity = Number(data.maximum_density ?? (avgDensity * 1.8));
    const minDensity = Number(data.minimum_density ?? 0.22);
    const highCount = Number(data.high_congestion_roads ?? (data.congested_segments ?? 1));
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
        timestamp: data.timestamp || new Date().toISOString()
    };
}

function normalizeRoadData(road) {
    if (!road) return null;
    const roadNames = {
        "R001": "Main Expressway",
        "R002": "Central Avenue",
        "R003": "West Ring Road",
        "R004": "North Boulevard",
        "R005": "Industrial Highway",
        "R006": "Airport Road",
        "R007": "Harbor Tunnel Approach"
    };

    const level = (road.congestion_level || "Low").trim();
    const density = Number(road.density ?? road.traffic_density_vehicles_per_km ?? 0);
    const vehicleCount = Number(road.vehicle_count ?? 0);
    const avgSpeed = road.avg_speed_kmph !== undefined && road.avg_speed_kmph !== null
        ? Number(road.avg_speed_kmph)
        : (level === "Severe" ? 7 : (level === "High" ? 14 : (level === "Medium" ? 28 : 50)));

    return {
        road_id: road.road_id,
        road_name: road.road_name || road.name || roadNames[road.road_id] || `Road ${road.road_id}`,
        vehicle_count: vehicleCount,
        density: Math.round(density * 100) / 100,
        avg_speed_kmph: Math.round(avgSpeed * 10) / 10,
        speed: road.speed || `${Math.round(avgSpeed)} km/h`,
        congestion_level: level,
        updated_at: road.updated_at || road.reading_timestamp || new Date().toISOString()
    };
}

function getCongestionBadgeInfo(level = "Low", density = 0) {
    const normLevel = (level || "").toLowerCase();

    if (normLevel.includes("severe") || density >= 28) {
        return {
            level: "Severe",
            label: "Severe Gridlock",
            badgeBg: "bg-[#e11d48]/20 text-[#fda4af] border-[#e11d48]/40 shadow-[0_0_12px_rgba(225,29,72,0.4)]",
            borderClass: "border-l-4 border-l-[#e11d48]",
            badgeClass: "text-[#fda4af]",
            indicatorBg: "bg-[#e11d48]",
            icon: "emergency",
            colorHex: "#e11d48"
        };
    } else if (normLevel.includes("high") || density >= 20) {
        return {
            level: "High",
            label: "Heavy Congestion",
            badgeBg: "bg-[#ef4444]/20 text-[#fca5a5] border-[#ef4444]/30",
            borderClass: "border-l-4 border-l-[#ef4444]",
            badgeClass: "text-error",
            indicatorBg: "bg-error",
            icon: "car_crash",
            colorHex: "#ef4444"
        };
    } else if (normLevel.includes("med") || density >= 10) {
        return {
            level: "Medium",
            label: "Moderate Delay",
            badgeBg: "bg-[#facc15]/20 text-[#fef08a] border-[#facc15]/30",
            borderClass: "border-l-4 border-l-[#facc15]",
            badgeClass: "text-yellow-400",
            indicatorBg: "bg-yellow-400",
            icon: "info",
            colorHex: "#facc15"
        };
    } else {
        return {
            level: "Low",
            label: "Optimal Flow",
            badgeBg: "bg-[#4ade80]/20 text-[#bbf7d0] border-[#4ade80]/30",
            borderClass: "border-l-4 border-l-[#4ade80]",
            badgeClass: "text-emerald-300",
            indicatorBg: "bg-emerald-400",
            icon: "check_circle",
            colorHex: "#4ade80"
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
        const role = (sessionStorage.getItem('role') || '').toUpperCase();
        if (role === 'TRAFFIC_OPERATOR') return 'OPERATOR';
        return role;
    },
    getUserName() {
        return sessionStorage.getItem('user_name') || 'Traffic Operator';
    },
    setSession(data) {
        if (data.access_token) sessionStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) sessionStorage.setItem('refresh_token', data.refresh_token);
        if (data.role) sessionStorage.setItem('role', data.role.toUpperCase());
        if (data.name) sessionStorage.setItem('user_name', data.name);
    },
    clearSession() {
        sessionStorage.clear();
    },
    isAuthenticated() {
        return !!this.getToken();
    },
    getDashboardUrl(role) {
        const r = (role || this.getRole()).toUpperCase();
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
            const hasAccess = allowedRoles.some(r => {
                const normalized = r.toUpperCase();
                return currentRole === normalized || (normalized === 'OPERATOR' && currentRole === 'TRAFFIC_OPERATOR');
            });
            if (!hasAccess) {
                window.location.replace(this.getDashboardUrl(currentRole));
                return false;
            }
        }
        return true;
    },
    logout() {
        this.clearSession();
        window.location.href = 'Login.html';
    }
};

// Global shorthand for inline HTML onclick handlers
function logout() {
    AuthManager.logout();
}

function getDashboardUrl() {
    return AuthManager.getDashboardUrl();
}

// ==========================================
// Core Fetch Client with Auto Retry / Fallback
// ==========================================
async function apiFetch(endpoint, options = {}, alternateEndpoint = null) {
    const token = AuthManager.getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    // Candidate base hosts/ports
    const baseHosts = [
        API_CONFIG.BASE_URL,
        'http://localhost:8000/api/v1',
        'http://localhost:8001/api/v1'
    ];

    // Candidate endpoint paths to handle both clean and double-prefixed router setups
    const endpointVariations = [endpoint];
    if (alternateEndpoint) {
        endpointVariations.push(alternateEndpoint);
    }
    // Also auto-add duplicate prefix variations if endpoint starts with /auth, /traffic, /predict
    if (endpoint.startsWith('/auth/')) {
        endpointVariations.push(endpoint.replace('/auth/', '/auth/api/v1/auth/'));
        endpointVariations.push(endpoint.replace('/auth/', '/auth/auth/'));
    } else if (endpoint.startsWith('/traffic/')) {
        endpointVariations.push(endpoint.replace('/traffic/', '/traffic/traffic/'));
    } else if (endpoint.startsWith('/predict/')) {
        endpointVariations.push(endpoint.replace('/predict/', '/predict/predict/'));
    }

    const urlsToTry = [];
    baseHosts.forEach(base => {
        endpointVariations.forEach(ep => {
            const fullUrl = `${base}${ep}`;
            if (!urlsToTry.includes(fullUrl)) {
                urlsToTry.push(fullUrl);
            }
        });
    });

    for (let i = 0; i < urlsToTry.length; i++) {
        const url = urlsToTry[i];
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

            let response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            // Handle 401 Silent Refresh
            if (response.status === 401 && AuthManager.getRefreshToken()) {
                const refreshed = await tryTokenRefresh();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${AuthManager.getToken()}`;
                    response = await fetch(url, { ...options, headers });
                }
            }

            if (response.ok) {
                return await response.json();
            }

            // If 404/405, try other path/port combinations
            if ((response.status === 404 || response.status === 405) && i < urlsToTry.length - 1) {
                continue;
            }

            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP Error ${response.status}`);
        } catch (err) {
            if (i === urlsToTry.length - 1) {
                throw err;
            }
        }
    }
}

async function tryTokenRefresh() {
    const refreshToken = AuthManager.getRefreshToken();
    if (!refreshToken) return false;
    try {
        const res = await fetch(`${API_CONFIG.BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        if (res.ok) {
            const data = await res.json();
            if (data.access_token) {
                sessionStorage.setItem('access_token', data.access_token);
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
        try {
            return await apiFetch('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            }, '/auth/auth/login');
        } catch (err) {
            throw err;
        }
    },
    async register(name, email, password, role = 'PUBLIC') {
        try {
            return await apiFetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ name, email, password, role })
            }, '/auth/auth/register');
        } catch (err) {
            throw err;
        }
    },
    async getProfile() {
        try {
            return await apiFetch('/auth/me', {}, '/auth/auth/me');
        } catch (err) {
            return {
                user_id: "local-user",
                name: AuthManager.getUserName(),
                role: AuthManager.getRole()
            };
        }
    }
};

const trafficAPI = {
    async getLiveTraffic() {
        try {
            const data = await apiFetch('/traffic/live', {}, '/traffic/traffic/live');
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
            const data = await apiFetch('/traffic/density', {}, '/traffic/traffic/density');
            return normalizeDensitySummary(data);
        } catch (err) {
            console.warn('Using Day 6 mock density summary:', err.message);
            return normalizeDensitySummary(MOCK_DENSITY_SUMMARY);
        }
    },
    async getRoadTraffic(roadId) {
        try {
            const data = await apiFetch(`/traffic/road/${roadId}`, {}, `/traffic/traffic/road/${roadId}`);
            if (data) {
                const norm = normalizeRoadData(data);
                const rawHistory = Array.isArray(data.history) ? data.history : [];
                norm.history = rawHistory.map(h => ({
                    vehicle_count: h.vehicle_count,
                    density: Number(h.density ?? h.traffic_density_vehicles_per_km ?? 0),
                    congestion_level: h.congestion_level || norm.congestion_level,
                    avg_speed_kmph: h.avg_speed_kmph ? Number(h.avg_speed_kmph) : norm.avg_speed_kmph,
                    updated_at: h.updated_at || h.reading_timestamp || h.time || new Date().toISOString()
                }));
                return norm;
            }
            throw new Error("No data returned");
        } catch (err) {
            console.warn(`Using mock road data for ${roadId}:`, err.message);
            const road = MOCK_TRAFFIC_DATA.find(r => r.road_id.toUpperCase() === roadId.toUpperCase()) || MOCK_TRAFFIC_DATA[0];
            const norm = normalizeRoadData(road);
            norm.history = [
                { updated_at: "21:00:00", density: norm.density * 0.8, vehicle_count: Math.round(norm.vehicle_count * 0.8), avg_speed_kmph: norm.avg_speed_kmph * 1.1, congestion_level: "Low" },
                { updated_at: "21:30:00", density: norm.density * 0.95, vehicle_count: Math.round(norm.vehicle_count * 0.95), avg_speed_kmph: norm.avg_speed_kmph * 1.05, congestion_level: norm.congestion_level },
                { updated_at: "22:00:00", density: norm.density, vehicle_count: norm.vehicle_count, avg_speed_kmph: norm.avg_speed_kmph, congestion_level: norm.congestion_level }
            ];
            return norm;
        }
    }
};

const predictAPI = {
    async getCongestion(roadId) {
        try {
            return await apiFetch(`/predict/congestion?road_id=${encodeURIComponent(roadId)}`, {}, `/predict/predict/congestion?road_id=${encodeURIComponent(roadId)}`);
        } catch (err) {
            console.warn(`Using fallback heuristic prediction for ${roadId}:`, err.message);
            const road = MOCK_TRAFFIC_DATA.find(r => r.road_id.toUpperCase() === roadId.toUpperCase()) || MOCK_TRAFFIC_DATA[0];
            let predicted_level = "Low";
            if (road.density >= 28) predicted_level = "Severe";
            else if (road.density >= 20) predicted_level = "High";
            else if (road.density >= 10) predicted_level = "Medium";
            return {
                road_id: roadId,
                predicted_level: predicted_level,
                confidence: 0.88,
                generated_by: "heuristic-fallback-v2"
            };
        }
    }
};

// Auto-sync navigation links on load
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-home-link').forEach(el => {
        el.href = AuthManager.getDashboardUrl();
    });
});

