/**
 * TrafficVision AI - Centralized API Client & Frontend Utilities
 * Supports live backend communication with automatic fallback aligned with Day 6 Traffic Monitoring specs.
 */

const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',
    TIMEOUT: 10000
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
            const hasAccess = allowedRoles.some(r => {
                const normalized = r.toUpperCase();
                const targetRole = (normalized === 'USER') ? 'PUBLIC' : normalized;
                const userRole = (currentRole === 'USER') ? 'PUBLIC' : currentRole;
                return userRole === targetRole || (targetRole === 'OPERATOR' && userRole === 'TRAFFIC_OPERATOR');
            });
            if (!hasAccess) {
                const targetUrl = this.getDashboardUrl(currentRole);
                const currentPage = window.location.pathname.split('/').pop();
                // Prevent infinite redirect loop if already on target dashboard
                if (currentPage && decodeURIComponent(currentPage).toLowerCase() === targetUrl.toLowerCase()) {
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
// Core Fetch Client - Direct Backend Call
// ==========================================
async function apiFetch(endpoint, options = {}, alternateEndpoint = null) {
    const token = AuthManager.getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
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
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        // Handle 401 Silent Refresh
        if (response.status === 401 && AuthManager.getRefreshToken()) {
            const refreshed = await tryTokenRefresh();
            if (refreshed) {
                const refreshedToken = AuthManager.getToken();
                const retryHeaders = {
                    ...headers,
                    'Authorization': `Bearer ${refreshedToken}`
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
            errorDetail = errorDetail.map(e => e.msg || (typeof e === 'string' ? e : JSON.stringify(e))).join(', ');
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
            body: JSON.stringify({ refresh_token: refreshToken })
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
        try {
            return await apiFetch('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
        } catch (err) {
            throw err;
        }
    },
    async register(name, email, password, role = 'user') {
        let backendRole = (role || 'user').toLowerCase();
        if (backendRole === 'public') {
            backendRole = 'user';
        } else if (backendRole === 'traffic_operator') {
            backendRole = 'operator';
        }

        try {
            return await apiFetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ name, email, password, role: backendRole })
            });
        } catch (err) {
            throw err;
        }
    },
    async getProfile() {
        try {
            return await apiFetch('/auth/me');
        } catch (err) {
            return {
                user_id: "local-user",
                name: AuthManager.getUserName(),
                role: AuthManager.getRole()
            };
        }
    }
};

const operatorAPI = {
    _storageKey: 'traffic_operators_roster',
    _getDefaults() {
        return [
            { id: "OP-101", name: "J. Smith", email: "j.smith@trafficvision.ai", sector: "Airport Corridor (R006)", status: "Active", shift: "Morning", created_at: "2026-09-10" },
            { id: "OP-102", name: "Sarah Connor", email: "s.connor@trafficvision.ai", sector: "Downtown Grid (R002)", status: "Active", shift: "Day", created_at: "2026-09-11" },
            { id: "OP-103", name: "Alex Chen", email: "a.chen@trafficvision.ai", sector: "Main Expressway (R001)", status: "Standby", shift: "Evening", created_at: "2026-09-12" },
            { id: "OP-104", name: "Elena Rostova", email: "e.rostova@trafficvision.ai", sector: "West Ring Road (R003)", status: "Active", shift: "Night", created_at: "2026-09-12" }
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
            sector: sector || "Downtown Grid (R002)",
            status: "Active",
            shift: shift || "Morning",
            created_at: new Date().toISOString().split('T')[0]
        };
        operators.unshift(newOp);
        this._save(operators);
        return newOp;
    },
    async removeOperator(id) {
        const operators = this.getOperators();
        const filtered = operators.filter(op => op.id !== id);
        this._save(filtered);
        return true;
    }
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

const ROAD_NETWORK_GEOMETRY = {
    center: [12.9716, 77.5946], // Metropolitan Metro Center Coordinates
    zoom: 13,
    hubs: [
        { id: "HUB_DOWNTOWN", name: "Downtown Central Terminal", coords: [12.9750, 77.5850], icon: "hub", color: "#8dcdff" },
        { id: "HUB_TECH_PARK", name: "Tech Park Sector 4", coords: [12.9350, 77.6250], icon: "apartment", color: "#bdc2ff" },
        { id: "HUB_AIRPORT", name: "International Airport Junction", coords: [13.0150, 77.6350], icon: "flight_takeoff", color: "#cdbdff" },
        { id: "HUB_INDUSTRIAL", name: "Industrial Zone Gate 2", coords: [12.9450, 77.5450], icon: "factory", color: "#facc15" },
        { id: "HUB_HARBOR", name: "Harbor Logistics Basin", coords: [12.9850, 77.6550], icon: "anchor", color: "#e11d48" },
        { id: "HUB_WEST_RIDGE", name: "West Ridge Interchange", coords: [12.9600, 77.5300], icon: "alt_route", color: "#4ade80" }
    ],
    segments: {
        "R001": {
            road_id: "R001",
            road_name: "Main Expressway",
            length_km: 8.4,
            speed_limit: 60,
            coordinates: [
                [12.9750, 77.5850],
                [12.9720, 77.5980],
                [12.9650, 77.6100],
                [12.9520, 77.6180],
                [12.9350, 77.6250]
            ],
            junctions: ["HUB_DOWNTOWN", "HUB_TECH_PARK"]
        },
        "R002": {
            road_id: "R002",
            road_name: "Central Avenue",
            length_km: 5.2,
            speed_limit: 45,
            coordinates: [
                [12.9750, 77.5850],
                [12.9680, 77.5800],
                [12.9550, 77.5720],
                [12.9450, 77.5450]
            ],
            junctions: ["HUB_DOWNTOWN", "HUB_INDUSTRIAL"]
        },
        "R003": {
            road_id: "R003",
            road_name: "West Ring Road",
            length_km: 7.8,
            speed_limit: 50,
            coordinates: [
                [12.9450, 77.5450],
                [12.9520, 77.5380],
                [12.9600, 77.5300],
                [12.9800, 77.5420],
                [12.9950, 77.5600],
                [12.9750, 77.5850]
            ],
            junctions: ["HUB_INDUSTRIAL", "HUB_WEST_RIDGE", "HUB_DOWNTOWN"]
        },
        "R004": {
            road_id: "R004",
            road_name: "North Boulevard",
            length_km: 9.1,
            speed_limit: 65,
            coordinates: [
                [12.9750, 77.5850],
                [12.9880, 77.5950],
                [13.0020, 77.6120],
                [13.0150, 77.6350]
            ],
            junctions: ["HUB_DOWNTOWN", "HUB_AIRPORT"]
        },
        "R005": {
            road_id: "R005",
            road_name: "Industrial Highway",
            length_km: 6.5,
            speed_limit: 40,
            coordinates: [
                [12.9450, 77.5450],
                [12.9380, 77.5650],
                [12.9320, 77.5900],
                [12.9350, 77.6250]
            ],
            junctions: ["HUB_INDUSTRIAL", "HUB_TECH_PARK"]
        },
        "R006": {
            road_id: "R006",
            road_name: "Airport Road",
            length_km: 11.2,
            speed_limit: 50,
            coordinates: [
                [13.0150, 77.6350],
                [13.0050, 77.6480],
                [12.9850, 77.6550],
                [12.9650, 77.6400],
                [12.9350, 77.6250]
            ],
            junctions: ["HUB_AIRPORT", "HUB_HARBOR", "HUB_TECH_PARK"]
        },
        "R007": {
            road_id: "R007",
            road_name: "Harbor Tunnel Approach",
            length_km: 4.6,
            speed_limit: 35,
            coordinates: [
                [12.9750, 77.5850],
                [12.9790, 77.6150],
                [12.9850, 77.6550]
            ],
            junctions: ["HUB_DOWNTOWN", "HUB_HARBOR"]
        }
    }
};

const predictAPI = {
    async getCongestion(roadId) {
        // Build the POST body the backend expects (CongestionRequest schema)
        const road = MOCK_TRAFFIC_DATA.find(r => r.road_id.toUpperCase() === roadId.toUpperCase()) || MOCK_TRAFFIC_DATA[0];
        const geom = ROAD_NETWORK_GEOMETRY.segments[road.road_id] || { length_km: 8.0, speed_limit: 60 };
        const now = new Date();
        const requestBody = {
            road_id: road.road_id,
            vehicle_count: road.vehicle_count || 30,
            density: road.density || 10,
            avg_speed_kmph: road.avg_speed_kmph || 40,
            road_capacity: geom.speed_limit ? geom.speed_limit * 2 : 100,   // estimate capacity from speed limit
            road_length_km: geom.length_km || 5.0,
            hour: now.getHours(),
            day_of_week: now.getDay(),          // 0 = Sunday … 6 = Saturday
            is_weekend: (now.getDay() === 0 || now.getDay() === 6) ? 1 : 0
        };

        try {
            return await apiFetch('/predict/congestion', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });
        } catch (err) {
            console.warn(`Using fallback prediction for ${roadId} (backend unavailable):`, err.message);
            const density = road.density || 10;

            let predicted_level = "Low";
            let confidence = 0.88;
            if (density >= 28) { predicted_level = "Severe"; confidence = 0.94; }
            else if (density >= 20) { predicted_level = "High"; confidence = 0.91; }
            else if (density >= 10) { predicted_level = "Medium"; confidence = 0.85; }

            return {
                road_id: road.road_id,
                road_name: road.road_name,
                predicted_level,
                confidence,
                generated_by: "model-v1"
            };
        }
    },

    async getPeakHourPrediction(roadId = "R006") {
        try {
            const data = await apiFetch(`/predict/peak-hours?road_id=${encodeURIComponent(roadId)}`);
            if (data && data.peak_hours) return data;
        } catch (err) {
            console.warn(`Using model-v1 peak-hour prediction generator for ${roadId}:`, err.message);
        }

        // Intern 3's model-v1 peak-hours calculation: hours [8, 9, 10, 17, 18, 19, 20]
        const road = MOCK_TRAFFIC_DATA.find(r => r.road_id.toUpperCase() === roadId.toUpperCase()) || MOCK_TRAFFIC_DATA[5];
        const baseDensity = road.density;
        const peakHours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
        
        const hourProfiles = {
            7:  { multiplier: 0.65, label: "07:00 AM" },
            8:  { multiplier: 1.35, label: "08:00 AM (Morning Peak)" },
            9:  { multiplier: 1.45, label: "09:00 AM (Morning Rush)" },
            10: { multiplier: 1.15, label: "10:00 AM" },
            11: { multiplier: 0.85, label: "11:00 AM" },
            12: { multiplier: 0.90, label: "12:00 PM" },
            13: { multiplier: 0.88, label: "01:00 PM" },
            14: { multiplier: 0.92, label: "02:00 PM" },
            15: { multiplier: 1.05, label: "03:00 PM" },
            16: { multiplier: 1.25, label: "04:00 PM" },
            17: { multiplier: 1.50, label: "05:00 PM (Evening Peak)" },
            18: { multiplier: 1.60, label: "06:00 PM (Evening Rush)" },
            19: { multiplier: 1.35, label: "07:00 PM" },
            20: { multiplier: 1.05, label: "08:00 PM" },
            21: { multiplier: 0.70, label: "09:00 PM" }
        };

        const predictions = peakHours.map(hour => {
            const profile = hourProfiles[hour] || { multiplier: 1.0, label: `${hour}:00` };
            const simDensity = Math.round(baseDensity * profile.multiplier * 10) / 10;
            const simVehicles = Math.round((road.vehicle_count || 30) * profile.multiplier);
            
            let level = "Low";
            let confidence = 0.89;
            if (simDensity >= 28) { level = "Severe"; confidence = 0.95; }
            else if (simDensity >= 20) { level = "High"; confidence = 0.92; }
            else if (simDensity >= 10) { level = "Medium"; confidence = 0.86; }
            
            return {
                hour: hour,
                time_label: profile.label,
                density: simDensity,
                vehicle_count: simVehicles,
                predicted_level: level,
                confidence: confidence,
                is_peak_period: [8, 9, 10, 17, 18, 19, 20].includes(hour)
            };
        });

        return {
            road_id: road.road_id,
            road_name: road.road_name,
            peak_hours: predictions,
            generated_by: "model-v1",
            timestamp: new Date().toISOString()
        };
    },

    async getAllDelayEstimates() {
        const liveRoads = await trafficAPI.getLiveTraffic();
        return liveRoads.map(road => {
            const geom = ROAD_NETWORK_GEOMETRY.segments[road.road_id] || { length_km: 7.0, speed_limit: 50 };
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
            const predictedDelay = Math.max(0, Math.round((predictedMinutes - freeFlowMinutes) * 10) / 10);

            let status = "Normal Flow";
            let statusColor = "text-emerald-400";
            if (delayMinutes >= 15 || road.congestion_level === "Severe") {
                status = "Critical Delay";
                statusColor = "text-rose-400";
            } else if (delayMinutes >= 8 || road.congestion_level === "High") {
                status = "High Delay";
                statusColor = "text-error";
            } else if (delayMinutes >= 3 || road.congestion_level === "Medium") {
                status = "Moderate Delay";
                statusColor = "text-yellow-400";
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
                status_color: statusColor
            };
        });
    },

    getTemporalForecast(roadId, horizonMinutes = 0) {
        const road = MOCK_TRAFFIC_DATA.find(r => r.road_id.toUpperCase() === roadId.toUpperCase()) || MOCK_TRAFFIC_DATA[0];
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
        
        let predictedLevel = "Low";
        if (predictedDensity >= 28) predictedLevel = "Severe";
        else if (predictedDensity >= 20) predictedLevel = "High";
        else if (predictedDensity >= 10) predictedLevel = "Medium";

        return {
            road_id: road.road_id,
            road_name: road.road_name,
            horizon_minutes: horizonMinutes,
            current_density: baseDensity,
            predicted_density: predictedDensity,
            current_speed: baseSpeed,
            predicted_speed: predictedSpeed,
            predicted_level: predictedLevel,
            confidence: Math.max(0.72, Math.round((0.95 - (horizonMinutes * 0.0015)) * 100) / 100),
            trend: densityDelta > 0 ? "Increasing Congestion" : (densityDelta < 0 ? "Clearing Flow" : "Stable")
        };
    },

    getAllRoadForecasts(horizonMinutes = 30) {
        return MOCK_TRAFFIC_DATA.map(road => this.getTemporalForecast(road.road_id, horizonMinutes));
    },

    getHistoricalVsPredicted(roadId) {
        const road = MOCK_TRAFFIC_DATA.find(r => r.road_id.toUpperCase() === roadId.toUpperCase()) || MOCK_TRAFFIC_DATA[0];
        const base = road.density;
        return [
            { time: "18:00", actual: Math.max(1, base * 0.5), predicted: Math.max(1, base * 0.52) },
            { time: "19:00", actual: Math.max(2, base * 0.75), predicted: Math.max(2, base * 0.72) },
            { time: "20:00 (Now)", actual: base, predicted: base },
            { time: "20:30 (+30m)", actual: null, predicted: Math.round((base * 1.25) * 10) / 10 },
            { time: "21:00 (+1h)", actual: null, predicted: Math.round((base * 1.4) * 10) / 10 },
            { time: "22:00 (+2h)", actual: null, predicted: Math.round((base * 0.9) * 10) / 10 }
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
            this.getPeakHourPrediction("R006"),
            this.getPeakHourPrediction("R007")
        ]);

        const timestamp = new Date().toISOString();
        const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        const filename = `TrafficVision_AI_Prediction_Report_${new Date().toISOString().slice(0,10)}_${Date.now().toString().slice(-4)}.${format}`;

        if (format === 'json') {
            const reportPayload = {
                report_title: "TrafficVision AI - Comprehensive Prediction & Delay Report",
                generated_at: timestamp,
                model_version: "model-v1 (Intern 3 AI Prediction Service)",
                executive_summary: {
                    total_roads_monitored: densitySummary.total_roads || liveRoads.length,
                    total_vehicles_active: densitySummary.total_vehicle_count,
                    average_network_density: densitySummary.average_density,
                    severe_bottlenecks: densitySummary.severe_congestion_roads || 0,
                    high_congestion_roads: densitySummary.high_congestion_roads || 0
                },
                corridor_delay_estimates: delays,
                per_road_temporal_forecasts_30m: this.getAllRoadForecasts(30),
                peak_hour_schedules: {
                    "Airport Road (R006)": peakR006.peak_hours,
                    "Harbor Tunnel Approach (R007)": peakR007.peak_hours
                },
                recommended_interventions: [
                    "Activate dynamic signal prioritization at Tech Park & Airport Junctions",
                    "Reroute commercial freight from Harbor Tunnel (R007) to West Bypass (R003)",
                    "Deploy automated variable message signs (VMS) on Main Expressway"
                ]
            };

            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportPayload, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", filename);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
            return { filename, status: "success", count: liveRoads.length };
        }

        // CSV Export Format
        let csvContent = `TrafficVision AI - Network Traffic Prediction & Delay Analysis Report\n`;
        csvContent += `Generated At,"${dateStr}"\n`;
        csvContent += `AI Prediction Engine,Intern 3 (model-v1)\n`;
        csvContent += `Network Avg Density,${densitySummary.average_density} veh/km\n`;
        csvContent += `Active Vehicles Monitored,${densitySummary.total_vehicle_count}\n\n`;

        csvContent += `--- 1. LIVE CORRIDOR DELAY ESTIMATES & SPEED PROJECTIONS ---\n`;
        csvContent += `Road ID,Road Name,Length (km),Speed Limit (km/h),Current Speed (km/h),Predicted Speed (km/h),Free Flow Time (min),Current Time (min),Current Delay (min),Predicted Delay +30m (min),Congestion Level,Predicted Level (+30m),Status\n`;

        delays.forEach(d => {
            csvContent += `"${d.road_id}","${d.road_name}",${d.length_km},${d.speed_limit},${d.current_speed},${d.predicted_speed},${d.free_flow_time_min},${d.current_time_min},${d.delay_minutes},${d.predicted_delay_30m},"${d.congestion_level}","${d.predicted_level}","${d.status}"\n`;
        });

        csvContent += `\n--- 2. PER-ROAD MULTI-HORIZON CONGESTION FORECASTS ---\n`;
        csvContent += `Road ID,Road Name,Current Density (veh/km),Forecast +15m Density,Forecast +30m Density,Forecast +60m Density,Forecast +120m Density,Trend,Confidence Score\n`;

        liveRoads.forEach(r => {
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
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        return { filename, status: "success", count: liveRoads.length };
    }
};

// ==========================================
// Route Analysis API Helpers
// ==========================================

/**
 * Maps a numeric congestion_score (0.0–1.0) from the backend
 * to the UI congestion level string used by getCongestionBadgeInfo().
 */
function congestionScoreToLevel(score) {
    if (score == null || isNaN(score)) return "Low";
    if (score >= 0.75) return "Severe";
    if (score >= 0.50) return "High";
    if (score >= 0.25) return "Medium";
    return "Low";
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
    const routeId = backendRoute.route_id || `ROUTE_${(opts.rank || 0)}`;
    const geometry = backendRoute.geometry || backendRoute.path || [];
    // The backend returns GeoJSON geometry as [[lng, lat], ...] or [{lat, lng}, ...]
    // Leaflet polylines expect [lat, lng], so swap GeoJSON array coordinates to [lat, lng].
    const coordinates = geometry.map(pt => {
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
        current_speed: distanceKm > 0 && durationMin > 0
            ? Math.round((distanceKm / (durationMin / 60)) * 10) / 10
            : 40,
        density: Math.round(congestionScore * 30 * 100) / 100, // approximate density from score
        congestion_level: congestionLevel,
        segment_time_min: durationMin,
        coordinates: coordinates
    };

    return {
        route_id: routeId,
        route_name: opts.routeName || `Route ${opts.rank || 1}`,
        route_type: opts.routeType || "Alternative",
        is_recommended: !!opts.isRecommended,
        distance_km: Math.round(distanceKm * 10) / 10,
        duration_minutes: durationMin,
        delay_minutes: delayMin,
        worst_congestion: congestionLevel,
        congestion_score: congestionScore,
        ai_confidence: opts.isRecommended ? 0.94 : (0.85 - (opts.rank || 0) * 0.03),
        co2_estimate_kg: Math.round((distanceKm * 0.12) * 10) / 10,
        segments: [segment],
        coordinates: coordinates
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
    const toRad = d => d * Math.PI / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) ** 2
            + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
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

    async calculateRoutes(originId, destinationId, optimizationMode = "ai_optimal") {
        const hubs = ROAD_NETWORK_GEOMETRY.hubs;
        const origin = hubs.find(h => h.id === originId) || hubs[0];
        const destination = hubs.find(h => h.id === destinationId) || hubs[1];

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
                    this.fetchRoadConditions(originCoords, destCoords).catch(() => null)
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
                const ptToArr = pt => Array.isArray(pt) ? [pt[1], pt[0]]
                                    : (pt?.lat != null ? [pt.lat, pt.lng] : null);
                const routeStart = ptToArr(rawGeometry[0]);
                const routeEnd   = ptToArr(rawGeometry[rawGeometry.length - 1]);
                if (routeStart && routeEnd) {
                    const startOffset = haversineKm(originCoords, routeStart);
                    const endOffset   = haversineKm(destCoords,   routeEnd);
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
                    routeType: "AI Optimal",
                    routeName: optimizedData.route_name || "AI Optimized Route",
                    rank: 0,
                    travelTimeMin: estimatedMinutes
                });

                // Build alternate routes
                const altRoutes = [];
                const altArray = Array.isArray(alternatesData) ? alternatesData : (alternatesData?.routes || []);
                altArray.forEach((alt, idx) => {
                    const altRoute = normalizeBackendRoute(alt, {
                        isRecommended: false,
                        routeType: `Alternative ${String.fromCharCode(65 + idx)}`, // A, B, C...
                        routeName: alt.route_name || `Alternate Route ${String.fromCharCode(65 + idx)}`,
                        rank: alt.rank || (idx + 1),
                        travelTimeMin: null // travel-time endpoint is only for the primary route
                    });
                    altRoutes.push(altRoute);
                });

                const routes = [optimizedRoute, ...altRoutes];

                // Sort by duration if fastest mode selected
                if (optimizationMode === "fastest") {
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
                    data_source: "backend"
                };

                _routeBackendOk = true;
                console.info('✅ Route data fetched from backend API');
                return result;

            } catch (backendError) {
                _routeBackendOk = false;
                console.warn('⚠️ Backend route API unavailable, falling back to BFS mock:', backendError.message);
            }
        } else {
            console.info('⚡ Backend route API known-down — using BFS mock directly (no network wait)');
        }

        // ── Fallback: Client-Side Mock Calculation ──
        const liveRoads = await trafficAPI.getLiveTraffic();
        const roadMap = {};
        liveRoads.forEach(r => { roadMap[r.road_id] = r; });

        // ── Build adjacency graph from road network junctions ──
        // Each road segment declares which hubs it connects via its `junctions`
        // array. We build a bidirectional graph: hubId → [{roadId, neighborHub}]
        const hubGraph = {};
        Object.values(ROAD_NETWORK_GEOMETRY.segments).forEach(seg => {
            const junctions = seg.junctions || [];
            for (let i = 0; i < junctions.length; i++) {
                for (let j = 0; j < junctions.length; j++) {
                    if (i === j) continue;
                    const from = junctions[i];
                    const to   = junctions[j];
                    if (!hubGraph[from]) hubGraph[from] = [];
                    // Avoid duplicate edges for the same road
                    const exists = hubGraph[from].some(e => e.roadId === seg.road_id && e.hub === to);
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
                            visitedHubs: new Set([...visitedHubs, nextHub])
                        });
                    }
                }
            }

            // De-duplicate paths that traverse the same road set
            const seen = new Set();
            return results.filter(p => {
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
            const directSeg = Object.values(ROAD_NETWORK_GEOMETRY.segments)
                .find(s => s.junctions.includes(originId)) || ROAD_NETWORK_GEOMETRY.segments["R001"];
            foundPaths.push([directSeg.road_id]);
        }

        // Apply eco / fastest modifier: sort each alternative path by its
        // combined congestion score so the "best" one bubbles to position 0.
        const scorePath = (segIds) => {
            let totalTime = 0;
            let totalDist = 0;
            let totalCongestion = 0;
            segIds.forEach(id => {
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
        const scoredPaths = foundPaths.map(p => ({ path: p, ...scorePath(p) }));
        if (optimizationMode === "eco") {
            scoredPaths.sort((a, b) => a.totalCongestion - b.totalCongestion);
        } else {
            // ai_optimal & fastest both prefer lowest travel time
            scoredPaths.sort((a, b) => a.totalTime - b.totalTime);
        }

        const routeLabels = [
            { id: "ROUTE_ALPHA", name: "Express Arterial Route",   type: "AI Optimal",   recommended: true  },
            { id: "ROUTE_BETA",  name: "Western Ring Bypass",       type: "Alternative A", recommended: false },
            { id: "ROUTE_GAMMA", name: "Harbor East Perimeter",     type: "Alternative B", recommended: false }
        ];

        const buildRouteSummary = (id, name, type, segmentsList, isAiRecommended) => {
            let totalDistanceKm = 0;
            let totalTravelTimeMin = 0;
            let totalFreeFlowTimeMin = 0;
            let worstCongestion = "Low";
            const detailedSegments = [];
            const allCoords = [];

            segmentsList.forEach(segId => {
                const geom = ROAD_NETWORK_GEOMETRY.segments[segId];
                const live = roadMap[segId] || { density: 5, avg_speed_kmph: 50, congestion_level: "Low" };

                if (geom) {
                    totalDistanceKm += geom.length_km;
                    const speed = Math.max(5, live.avg_speed_kmph || 40);
                    const segTime = (geom.length_km / speed) * 60;
                    const freeFlowTime = (geom.length_km / geom.speed_limit) * 60;
                    totalTravelTimeMin += segTime;
                    totalFreeFlowTimeMin += freeFlowTime;

                    if (live.congestion_level === "Severe" || (worstCongestion !== "Severe" && live.congestion_level === "High")) {
                        worstCongestion = live.congestion_level;
                    } else if (worstCongestion === "Low" && live.congestion_level === "Medium") {
                        worstCongestion = "Medium";
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
                        coordinates: geom.coordinates
                    });

                    geom.coordinates.forEach(pt => allCoords.push(pt));
                }
            });

            const delayMin = Math.max(0, Math.round((totalTravelTimeMin - totalFreeFlowTimeMin) * 10) / 10);
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
                co2_estimate_kg: Math.round((totalDistanceKm * 0.12) * 10) / 10,
                segments: detailedSegments,
                coordinates: allCoords
            };
        };

        const routes = scoredPaths.map((sp, idx) => {
            const lbl = routeLabels[idx] || {
                id: `ROUTE_${String.fromCharCode(65 + idx)}`,
                name: `Route ${String.fromCharCode(65 + idx)}`,
                type: `Alternative ${String.fromCharCode(65 + idx)}`,
                recommended: false
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
            data_source: "mock_fallback"
        };
    }
};

// Auto-sync navigation links and user profile badges on load
document.addEventListener('DOMContentLoaded', () => {
    const role = AuthManager.getRole() || 'OPERATOR';
    const userName = AuthManager.getUserName() || (role.charAt(0).toUpperCase() + role.slice(1).toLowerCase());
    const dashUrl = AuthManager.getDashboardUrl();

    document.querySelectorAll('.nav-home-link').forEach(el => {
        el.href = dashUrl;
    });

    const nameEl = document.getElementById('nav-user-name');
    if (nameEl) nameEl.textContent = userName;

    const roleEl = document.getElementById('nav-user-role');
    if (roleEl) roleEl.textContent = role;

    // When admin is loaded, the dashboard page and admin page are the same,
    // so redundant 'Admin' links in the nav bar are removed / kept hidden.
    document.querySelectorAll('.nav-admin-only').forEach(el => {
        el.classList.add('hidden');
    });
});


