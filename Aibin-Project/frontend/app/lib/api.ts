// TrafficVision AI - Comprehensive API Client & Simulation Service

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface TrafficRoad {
  road_id: string;
  name: string;
  vehicle_count: number;
  density: number;
  speed: number;
  congestion_level: "Low" | "Medium" | "High" | string;
  updated_at: string;
  trend?: "up" | "down" | "stable";
  coordinates?: [number, number];
}

export interface RoadHistoryPoint {
  hour: number;
  density: number;
  congestion_level: string;
  avg_speed: number;
  timestamp: string;
}

export interface RoadDetail {
  road_id: string;
  name: string;
  congestion_level: string;
  vehicle_count: number;
  density: number;
  speed: number;
  history: RoadHistoryPoint[];
}

export interface DensityMetrics {
  average_density: number;
  total_roads: number;
  congested_roads: number;
  timestamp: string;
  network_speed_avg: number;
}

export interface PredictionResult {
  road_id: string;
  road_name?: string;
  predicted_level: "Low" | "Medium" | "High" | string;
  confidence: number;
  current_density: number;
  time_of_day: number;
  generated_by: string;
  recommendation?: string;
}

export interface TrafficAlert {
  id: string;
  road_id: string;
  road_name: string;
  severity: "critical" | "warning" | "advisory";
  title: string;
  message: string;
  timestamp: string;
  status: "active" | "acknowledged" | "resolved";
  action_recommended?: string;
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
  user: UserProfile;
}

// Milestone 2 Route Optimization & Analysis Types
export interface RouteLocation {
  id: string;
  name: string;
  category: "transit" | "commercial" | "airport" | "arterial" | "tech_hub";
  coordinates: [number, number];
  address: string;
}

export interface RouteSegment {
  segment_id: string;
  road_id: string;
  road_name: string;
  length_km: number;
  current_density: number;
  current_speed: number;
  congestion_level: "Low" | "Medium" | "High" | string;
  surface_condition: "Dry / Optimal" | "Normal" | "Wet / Slick" | "Construction Alert";
  incident_active: boolean;
  estimated_delay_sec: number;
}

export interface RoutePlan {
  route_id: string;
  name: string;
  is_recommended: boolean;
  type: "primary_fastest" | "alternate_bypass" | "alternate_eco";
  distance_km: number;
  travel_time_minutes: number;
  baseline_time_minutes: number;
  congestion_delay_minutes: number;
  average_speed_kmh: number;
  congestion_level: "Low" | "Medium" | "High" | string;
  corridors: string[];
  coordinates: [number, number][];
  savings_minutes: number;
  eco_score: number;
  segments: RouteSegment[];
  summary: string;
}

export interface RouteTravelDetail {
  route_id: string;
  total_distance_km: number;
  total_travel_time_min: number;
  total_delay_min: number;
  overall_condition: string;
  segments: RouteSegment[];
}

export interface CorridorForecast {
  road_id: string;
  road_name: string;
  current_density: number;
  predicted_density: number;
  congestion_probability: number;
  level: "Low" | "Medium" | "High";
  recommendation: string;
  peak_surge: boolean;
}

export interface PredictionHorizon {
  horizon_minutes: number;
  label: string;
  avg_predicted_density: number;
  confidence_score: number;
  bottlenecks_predicted: string[];
  corridors: CorridorForecast[];
}

export interface AIRecommendation {
  id: string;
  title: string;
  category: "signal_retiming" | "detour_routing" | "ramp_metering" | "green_wave" | "vms_advisory";
  priority: "critical" | "high" | "moderate" | "advisory";
  target_corridor_id: string;
  target_corridor_name: string;
  target_junction?: string;
  description: string;
  action_plan: string;
  impact_delay_reduction_pct: number;
  impact_speed_gain_kmh: number;
  impact_co2_offset_pct: number;
  confidence: number;
  status: "pending" | "applied" | "dismissed";
  applied_at?: string;
  simulation: {
    baseline_delay_min: number;
    optimized_delay_min: number;
    baseline_density_pct: number;
    optimized_density_pct: number;
    queue_length_meters_before: number;
    queue_length_meters_after: number;
  };
}

export interface HeatmapCell {
  day_index: number;
  day_name: string;
  hour: number;
  density: number;
  speed: number;
  congestion_level: "Low" | "Medium" | "High";
  incident_risk: "low" | "medium" | "critical";
  volume_count: number;
}

export interface HistoricalTimeSeriesPoint {
  timestamp: string;
  label: string;
  network_avg_density: number;
  network_avg_speed: number;
  corridor_densities: Record<string, number>;
}

export interface HistoricalReportFilter {
  dateRange: "24h" | "7d" | "30d" | "custom";
  corridorId: string;
  includeTelemetry: boolean;
  includeAlerts: boolean;
  includeRecommendations: boolean;
  includeCarbonMetrics: boolean;
}


// Token & Auth Persistence
export const tokenStorage = {
  getToken: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("tv_access_token");
  },
  setTokens: (accessToken: string, refreshToken?: string) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("tv_access_token", accessToken);
    if (refreshToken) localStorage.setItem("tv_refresh_token", refreshToken);
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
  },
  isSimulationMode: (): boolean => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem("tv_simulation_mode") === "true";
  },
  setSimulationMode: (enabled: boolean) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("tv_simulation_mode", enabled ? "true" : "false");
  },
};

// Realistic Default Monitored Corridors
export const INITIAL_ROADS: TrafficRoad[] = [
  {
    road_id: "R001",
    name: "MG Road",
    vehicle_count: 142,
    density: 78.4,
    speed: 18.5,
    congestion_level: "High",
    updated_at: new Date().toISOString(),
    trend: "up",
    coordinates: [12.9716, 77.5946],
  },
  {
    road_id: "R002",
    name: "Ring Road",
    vehicle_count: 88,
    density: 45.2,
    speed: 39.0,
    congestion_level: "Medium",
    updated_at: new Date().toISOString(),
    trend: "down",
    coordinates: [12.9352, 77.6245],
  },
  {
    road_id: "R003",
    name: "Station Road",
    vehicle_count: 165,
    density: 82.1,
    speed: 14.2,
    congestion_level: "High",
    updated_at: new Date().toISOString(),
    trend: "up",
    coordinates: [12.9784, 77.5684],
  },
  {
    road_id: "R004",
    name: "Airport Road",
    vehicle_count: 32,
    density: 18.0,
    speed: 62.4,
    congestion_level: "Low",
    updated_at: new Date().toISOString(),
    trend: "stable",
    coordinates: [13.0125, 77.6582],
  },
  {
    road_id: "R005",
    name: "Civil Lines",
    vehicle_count: 60,
    density: 32.5,
    speed: 48.0,
    congestion_level: "Low",
    updated_at: new Date().toISOString(),
    trend: "down",
    coordinates: [12.9856, 77.6012],
  },
];

export const INITIAL_ALERTS: TrafficAlert[] = [
  {
    id: "ALT-101",
    road_id: "R003",
    road_name: "Station Road",
    severity: "critical",
    title: "Severe Congestion & Queue Spillback",
    message: "Density sustained above 82% for over 15 minutes. Heavy bottleneck approaching rail terminal junction.",
    timestamp: new Date(Date.now() - 3 * 60000).toISOString(),
    status: "active",
    action_recommended: "Deploy traffic dispatch officer & lengthen Northbound green signal by 25s",
  },
  {
    id: "ALT-102",
    road_id: "R001",
    road_name: "MG Road",
    severity: "warning",
    title: "Rush Hour Volume Surge",
    message: "Vehicle volume up 28% in past 10 minutes. Density entering high threshold (78%).",
    timestamp: new Date(Date.now() - 11 * 60000).toISOString(),
    status: "acknowledged",
    action_recommended: "Broadcast variable message signage (VMS) advisory to divert toward Ring Road",
  },
  {
    id: "ALT-103",
    road_id: "R004",
    road_name: "Airport Road",
    severity: "advisory",
    title: "Optimal Flow Corridor Identified",
    message: "Airport arterial corridor maintaining 62 km/h free flow velocity. Recommended bypass route.",
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
    status: "resolved",
    action_recommended: "Promote route on commuter display network",
  },
];

export const INITIAL_RECOMMENDATIONS: AIRecommendation[] = [
  {
    id: "REC-101",
    title: "Station Road Ingress Green Phase Extension",
    category: "signal_retiming",
    priority: "critical",
    target_corridor_id: "R003",
    target_corridor_name: "Station Road",
    target_junction: "Terminal North Ingress (J-104)",
    description: "Station Road density reached 82.1% with vehicle queue growing by 18 vehicles/min. Current 45s green phase causes severe spillback onto feeder arterials.",
    action_plan: "Extend northbound cycle from 45s to 70s (+25s green) for 30 minutes, dynamically reducing cross-street phase.",
    impact_delay_reduction_pct: 34,
    impact_speed_gain_kmh: 8.5,
    impact_co2_offset_pct: 16.2,
    confidence: 0.94,
    status: "pending",
    simulation: {
      baseline_delay_min: 24.5,
      optimized_delay_min: 16.2,
      baseline_density_pct: 82.1,
      optimized_density_pct: 58.4,
      queue_length_meters_before: 850,
      queue_length_meters_after: 320,
    },
  },
  {
    id: "REC-102",
    title: "Dynamic Bypass Detour: MG Road to Outer Ring Road",
    category: "detour_routing",
    priority: "high",
    target_corridor_id: "R001",
    target_corridor_name: "MG Road",
    target_junction: "Victoria Flyover Divergence (J-082)",
    description: "MG Road operating at 78.4% capacity. Diverting 20% of commercial traffic toward Outer Ring elevated bypass prevents gridlock crest.",
    action_plan: "Update Variable Message Signs (VMS #4, #7) with advisory: 'MG Road Heavy Congestion (+18m delay) - Divert via Ring Road'.",
    impact_delay_reduction_pct: 22,
    impact_speed_gain_kmh: 6.2,
    impact_co2_offset_pct: 11.5,
    confidence: 0.89,
    status: "pending",
    simulation: {
      baseline_delay_min: 19.8,
      optimized_delay_min: 15.4,
      baseline_density_pct: 78.4,
      optimized_density_pct: 61.0,
      queue_length_meters_before: 620,
      queue_length_meters_after: 280,
    },
  },
  {
    id: "REC-103",
    title: "Outer Ring Road Green Wave Arterial Coordination",
    category: "green_wave",
    priority: "moderate",
    target_corridor_id: "R002",
    target_corridor_name: "Ring Road",
    target_junction: "Corridor Nodes J-201 through J-205",
    description: "Off-peak platooning observed. Synchronizing progression offset by 14.5s allows free-flow platoon clearance at 55 km/h.",
    action_plan: "Synchronize offsets across 4 signalized junctions along Ring Road to enable continuous progressive arterial flow.",
    impact_delay_reduction_pct: 18,
    impact_speed_gain_kmh: 9.0,
    impact_co2_offset_pct: 14.0,
    confidence: 0.91,
    status: "pending",
    simulation: {
      baseline_delay_min: 12.0,
      optimized_delay_min: 9.8,
      baseline_density_pct: 45.2,
      optimized_density_pct: 38.0,
      queue_length_meters_before: 310,
      queue_length_meters_after: 140,
    },
  },
  {
    id: "REC-104",
    title: "Airport Corridor Variable Speed Advisory Buffer",
    category: "vms_advisory",
    priority: "advisory",
    target_corridor_id: "R004",
    target_corridor_name: "Airport Road",
    target_junction: "Northern Curve Sector B",
    description: "Approaching airport access speed variance creates phantom shockwaves. Advisory speed smoothing prevents braking waves.",
    action_plan: "Display 50 km/h recommended advisory speed on overhead digital gantries to harmonize vehicle headway.",
    impact_delay_reduction_pct: 9,
    impact_speed_gain_kmh: 4.0,
    impact_co2_offset_pct: 6.8,
    confidence: 0.85,
    status: "applied",
    applied_at: new Date(Date.now() - 45 * 60000).toISOString(),
    simulation: {
      baseline_delay_min: 8.5,
      optimized_delay_min: 7.7,
      baseline_density_pct: 18.0,
      optimized_density_pct: 17.1,
      queue_length_meters_before: 120,
      queue_length_meters_after: 45,
    },
  },
  {
    id: "REC-105",
    title: "Civil Lines Ingress Ramp Metering Adjustment",
    category: "ramp_metering",
    priority: "high",
    target_corridor_id: "R005",
    target_corridor_name: "Civil Lines",
    target_junction: "East Arterial Ingress Ramp #2",
    description: "Evening transit surge predicted within 25 minutes. Restricting ramp influx to 12 vehicles/min protects main corridor velocity.",
    action_plan: "Activate dynamic ramp meter at 5.0-second red interval during peak commute window.",
    impact_delay_reduction_pct: 26,
    impact_speed_gain_kmh: 7.8,
    impact_co2_offset_pct: 12.8,
    confidence: 0.92,
    status: "pending",
    simulation: {
      baseline_delay_min: 16.4,
      optimized_delay_min: 12.1,
      baseline_density_pct: 54.0,
      optimized_density_pct: 40.2,
      queue_length_meters_before: 480,
      queue_length_meters_after: 190,
    },
  },
];

// Live telemetry drift simulation state
let simulatedRoads: TrafficRoad[] = JSON.parse(JSON.stringify(INITIAL_ROADS));
let simulatedAlerts: TrafficAlert[] = JSON.parse(JSON.stringify(INITIAL_ALERTS));
let simulatedRecommendations: AIRecommendation[] = JSON.parse(JSON.stringify(INITIAL_RECOMMENDATIONS));

function driftSimulation() {
  simulatedRoads = simulatedRoads.map((road) => {
    // Subtle realistic drift (-3 to +3 density)
    const drift = (Math.random() - 0.48) * 3;
    const newDensity = Math.max(8, Math.min(96, Math.round((road.density + drift) * 10) / 10));
    let congestion = "Low";
    if (newDensity > 50) congestion = "High";
    else if (newDensity >= 20) congestion = "Medium";

    // Speed inversely proportional to density
    const speed = Math.max(10, Math.round((70 - (newDensity * 0.65)) * 10) / 10);
    const vehicleCount = Math.round(newDensity * 1.8 + Math.floor(Math.random() * 10));

    return {
      ...road,
      density: newDensity,
      congestion_level: congestion,
      speed,
      vehicle_count: vehicleCount,
      updated_at: new Date().toISOString(),
      trend: drift > 0.5 ? "up" : drift < -0.5 ? "down" : "stable",
    };
  });
}

// Low-level fetch wrapper with seamless fallback
async function fetchWithFallback<T>(endpoint: string, fallbackFn: () => T, options: RequestInit = {}): Promise<{ data: T; isLive: boolean }> {
  // If user forced simulation mode, use fallback immediately
  if (tokenStorage.isSimulationMode()) {
    return { data: fallbackFn(), isLive: false };
  }

  const token = tokenStorage.getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000); // 2s timeout for instantaneous responsiveness

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      // Backend error -> fallback to mock
      return { data: fallbackFn(), isLive: false };
    }

    const json = await res.json();
    return { data: json as T, isLive: true };
  } catch {
    // Network down or connection refused -> gracefully use realistic simulation
    return { data: fallbackFn(), isLive: false };
  }
}

// Exported high-level API service
export const api = {
  // --- Auth Endpoints ---
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        const data = await res.json();
        const userProfile: UserProfile = {
          user_id: "usr_" + Math.random().toString(36).substring(7),
          name: email.split("@")[0].toUpperCase(),
          email,
          role: data.role || "operator",
        };
        return {
          access_token: data.access_token,
          refresh_token: data.refresh_token,
          token_type: data.token_type || "bearer",
          role: data.role || "operator",
          user: userProfile,
        };
      }
    } catch {
      // Offline fallback
    }

    // Determine mock role from email or default
    let mockRole: "admin" | "operator" | "public" = "operator";
    if (email.toLowerCase().includes("admin")) mockRole = "admin";
    else if (email.toLowerCase().includes("commuter") || email.toLowerCase().includes("public")) mockRole = "public";

    const mockProfile: UserProfile = {
      user_id: "usr_mock_" + Math.random().toString(36).substring(7),
      name: email.split("@")[0].toUpperCase(),
      email,
      role: mockRole,
    };

    return {
      access_token: "mock_jwt_token_" + Date.now(),
      refresh_token: "mock_refresh_token_" + Date.now(),
      token_type: "bearer",
      role: mockRole,
      user: mockProfile,
    };
  },

  async register(name: string, email: string, password: string, role: string = "operator"): Promise<UserProfile> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role }),
      });
      if (res.ok) {
        return res.json();
      }
    } catch {
      // Offline fallback
    }

    return {
      user_id: "usr_reg_" + Math.random().toString(36).substring(7),
      name,
      email,
      role,
    };
  },

  async getMe(): Promise<UserProfile> {
    const user = tokenStorage.getUser();
    if (user) return user;
    return {
      user_id: "usr_default",
      name: "Operator Control",
      email: "operator@trafficvision.ai",
      role: "operator",
    };
  },

  // --- Traffic Endpoints ---
  async getLiveTraffic(): Promise<{ roads: TrafficRoad[]; isLive: boolean }> {
    driftSimulation();
    const result = await fetchWithFallback<TrafficRoad[]>("/traffic/live", () => simulatedRoads);
    
    // Normalize format if backend returns road format
    const roads = result.data.map((r) => {
      const existing = simulatedRoads.find((s) => s.road_id.toUpperCase() === r.road_id.toUpperCase());
      return {
        ...r,
        speed: r.speed || (existing ? existing.speed : Math.max(12, Math.round(70 - (r.density * 0.6)))),
        coordinates: r.coordinates || (existing ? existing.coordinates : [12.97, 77.59]),
        trend: r.trend || (existing ? existing.trend : "stable"),
      };
    });

    return { roads, isLive: result.isLive };
  },

  async getDensityMetrics(): Promise<{ metrics: DensityMetrics; isLive: boolean }> {
    const fallback = (): DensityMetrics => {
      const total = simulatedRoads.length;
      const congested = simulatedRoads.filter((r) => r.congestion_level === "High").length;
      const sumDensity = simulatedRoads.reduce((acc, r) => acc + r.density, 0);
      const sumSpeed = simulatedRoads.reduce((acc, r) => acc + (r.speed || 35), 0);
      return {
        average_density: Math.round((sumDensity / total) * 10) / 10,
        total_roads: total,
        congested_roads: congested,
        timestamp: new Date().toISOString(),
        network_speed_avg: Math.round((sumSpeed / total) * 10) / 10,
      };
    };

    const result = await fetchWithFallback<DensityMetrics>("/traffic/density", fallback);
    const data = result.data;
    if (!data.network_speed_avg) {
      data.network_speed_avg = Math.round((simulatedRoads.reduce((acc, r) => acc + r.speed, 0) / simulatedRoads.length) * 10) / 10;
    }
    return { metrics: data, isLive: result.isLive };
  },

  async getRoadDetail(roadId: string): Promise<{ detail: RoadDetail; isLive: boolean }> {
    const fallback = (): RoadDetail => {
      const road = simulatedRoads.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) || simulatedRoads[0];
      const history: RoadHistoryPoint[] = [];
      const currentHour = new Date().getHours();

      for (let i = 23; i >= 0; i--) {
        const hour = (currentHour - i + 24) % 24;
        let baseDensity = 25;
        if ((hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 20)) {
          baseDensity = 70 + (Math.random() * 20);
        } else if (hour >= 0 && hour <= 5) {
          baseDensity = 10 + (Math.random() * 10);
        } else {
          baseDensity = 35 + (Math.random() * 20);
        }
        const density = Math.round(baseDensity * 10) / 10;
        let congestion = "Low";
        if (density > 50) congestion = "High";
        else if (density >= 20) congestion = "Medium";

        history.push({
          hour,
          density,
          congestion_level: congestion,
          avg_speed: Math.round((72 - density * 0.6) * 10) / 10,
          timestamp: new Date(Date.now() - i * 3600000).toISOString(),
        });
      }

      return {
        road_id: road.road_id,
        name: road.name,
        congestion_level: road.congestion_level,
        vehicle_count: road.vehicle_count,
        density: road.density,
        speed: road.speed,
        history,
      };
    };

    const result = await fetchWithFallback<RoadDetail>(`/traffic/road/${roadId}`, fallback);
    return { detail: result.data, isLive: result.isLive };
  },

  // --- AI Prediction Endpoints ---
  async getPrediction(roadId: string): Promise<{ prediction: PredictionResult; isLive: boolean }> {
    const fallback = (): PredictionResult => {
      const road = simulatedRoads.find((r) => r.road_id.toUpperCase() === roadId.toUpperCase()) || simulatedRoads[0];
      const hour = new Date().getHours();
      let predictedLevel = road.congestion_level;
      if ((hour >= 7 && hour <= 10) || (hour >= 17 && hour <= 20)) {
        if (predictedLevel === "Low") predictedLevel = "Medium";
        else if (predictedLevel === "Medium") predictedLevel = "High";
      }

      let recommendation = "Maintain current signal phase times.";
      if (predictedLevel === "High") {
        recommendation = "Extend green signal phase by 20s at downstream intersections and activate dynamic detour signage.";
      } else if (predictedLevel === "Medium") {
        recommendation = "Monitor corridor ingress ramp velocity and prepare signal adaptation.";
      }

      return {
        road_id: road.road_id,
        road_name: road.name,
        predicted_level: predictedLevel,
        confidence: 0.86,
        current_density: road.density,
        time_of_day: hour,
        generated_by: "AI Congestion Engine (v1.2)",
        recommendation,
      };
    };

    const result = await fetchWithFallback<PredictionResult>(`/predict/congestion?road_id=${roadId}`, fallback);
    return { prediction: result.data, isLive: result.isLive };
  },

  // --- Alerts Endpoints (Intern 1: GET /alerts/my & mark read) ---
  async getAlerts(): Promise<TrafficAlert[]> {
    const res = await fetchWithFallback<TrafficAlert[]>("/alerts/my", () => simulatedAlerts);
    return res.data;
  },

  async acknowledgeAlert(alertId: string): Promise<TrafficAlert[]> {
    simulatedAlerts = simulatedAlerts.map((a) =>
      a.id === alertId ? { ...a, status: "acknowledged" as const } : a
    );
    await fetchWithFallback(`/alerts/${alertId}/read`, () => ({ success: true, alert_id: alertId }), { method: "POST" });
    return simulatedAlerts;
  },

  async resolveAlert(alertId: string): Promise<TrafficAlert[]> {
    simulatedAlerts = simulatedAlerts.map((a) =>
      a.id === alertId ? { ...a, status: "resolved" as const } : a
    );
    await fetchWithFallback(`/alerts/${alertId}/resolve`, () => ({ success: true, alert_id: alertId }), { method: "POST" });
    return simulatedAlerts;
  },

  async broadcastIncident(roadId: string, title: string, message: string, severity: "critical" | "warning" | "advisory"): Promise<TrafficAlert> {
    const road = simulatedRoads.find((r) => r.road_id === roadId) || simulatedRoads[0];
    const newAlert: TrafficAlert = {
      id: "ALT-" + Math.floor(100 + Math.random() * 900),
      road_id: road.road_id,
      road_name: road.name,
      severity,
      title,
      message,
      timestamp: new Date().toISOString(),
      status: "active",
      action_recommended: "Manual incident trigger broadcast to all operators",
    };
    simulatedAlerts = [newAlert, ...simulatedAlerts];
    return newAlert;
  },

  // ==========================================
  // --- Milestone 2: Route Optimization ---
  // ==========================================
  getRouteLocations(): RouteLocation[] {
    return [
      {
        id: "LOC-01",
        name: "Station Road Rail & Transit Hub",
        category: "transit",
        coordinates: [12.9784, 77.5684],
        address: "Station Road Central Concourse, Zone 1",
      },
      {
        id: "LOC-02",
        name: "MG Road Central Business District",
        category: "commercial",
        coordinates: [12.9716, 77.5946],
        address: "MG Road Commercial Corridor, Sector 4",
      },
      {
        id: "LOC-03",
        name: "Outer Ring Road Junction",
        category: "arterial",
        coordinates: [12.9272, 77.6238],
        address: "Ring Road Expressway Flyover, South Gate",
      },
      {
        id: "LOC-04",
        name: "Airport Expressway Terminal",
        category: "airport",
        coordinates: [13.0125, 77.6582],
        address: "Airport Northern Access Highway, Sector 9",
      },
      {
        id: "LOC-05",
        name: "Civil Lines Administrative Complex",
        category: "arterial",
        coordinates: [12.9856, 77.5907],
        address: "Civil Lines Gov Boulevard, West Wing",
      },
      {
        id: "LOC-06",
        name: "Electronic City Tech Zone",
        category: "tech_hub",
        coordinates: [12.8452, 77.6602],
        address: "Hosur Elevated Tollway, South Tech Park",
      },
      {
        id: "LOC-07",
        name: "Indiranagar Metro Corridor",
        category: "commercial",
        coordinates: [12.9783, 77.6408],
        address: "100ft Road Metro Junction, East District",
      },
    ];
  },

  async optimizeRoute(
    originId: string,
    destinationId: string,
    preference: "fastest" | "least_congested" | "eco" = "fastest"
  ): Promise<{ recommended: RoutePlan; alternates: RoutePlan[]; isLive: boolean }> {
    const locations = this.getRouteLocations();
    const orig = locations.find((l) => l.id === originId) || locations[0];
    const dest = locations.find((l) => l.id === destinationId) || locations[3];

    // Midpoints calculation for realistic polyline curvatures
    const midLat = (orig.coordinates[0] + dest.coordinates[0]) / 2;
    const midLng = (orig.coordinates[1] + dest.coordinates[1]) / 2;

    const fallback = () => {
      // Primary Optimized Route (Bypassing heavy gridlock)
      const primaryCoordinates: [number, number][] = [
        orig.coordinates,
        [midLat + 0.015, midLng - 0.01],
        [midLat + 0.02, midLng + 0.015],
        dest.coordinates,
      ];

      // Alternate 1: Core City Artery (Straight through, but higher congestion)
      const alt1Coordinates: [number, number][] = [
        orig.coordinates,
        [midLat - 0.008, midLng - 0.005],
        [midLat + 0.005, midLng + 0.008],
        dest.coordinates,
      ];

      // Alternate 2: Outer Perimeter Ring
      const alt2Coordinates: [number, number][] = [
        orig.coordinates,
        [midLat - 0.02, midLng + 0.025],
        [midLat + 0.01, midLng + 0.035],
        dest.coordinates,
      ];

      const primarySegments: RouteSegment[] = [
        {
          segment_id: "SEG-01",
          road_id: "R003",
          road_name: orig.name,
          length_km: 2.4,
          current_density: 35.0,
          current_speed: 42.0,
          congestion_level: "Low",
          surface_condition: "Dry / Optimal",
          incident_active: false,
          estimated_delay_sec: 45,
        },
        {
          segment_id: "SEG-02",
          road_id: "R002",
          road_name: "Outer Ring Elevated Express",
          length_km: 8.6,
          current_density: 22.5,
          current_speed: 64.0,
          congestion_level: "Low",
          surface_condition: "Dry / Optimal",
          incident_active: false,
          estimated_delay_sec: 30,
        },
        {
          segment_id: "SEG-03",
          road_id: "R004",
          road_name: dest.name,
          length_km: 3.2,
          current_density: 28.0,
          current_speed: 55.0,
          congestion_level: "Low",
          surface_condition: "Dry / Optimal",
          incident_active: false,
          estimated_delay_sec: 40,
        },
      ];

      const alt1Segments: RouteSegment[] = [
        {
          segment_id: "SEG-ALT1-01",
          road_id: "R001",
          road_name: "MG Road Central Corridor",
          length_km: 5.8,
          current_density: 78.4,
          current_speed: 18.2,
          congestion_level: "High",
          surface_condition: "Normal",
          incident_active: true,
          estimated_delay_sec: 620,
        },
        {
          segment_id: "SEG-ALT1-02",
          road_id: "R004",
          road_name: "Airport Connector",
          length_km: 6.4,
          current_density: 46.0,
          current_speed: 38.0,
          congestion_level: "Medium",
          surface_condition: "Dry / Optimal",
          incident_active: false,
          estimated_delay_sec: 180,
        },
      ];

      const alt2Segments: RouteSegment[] = [
        {
          segment_id: "SEG-ALT2-01",
          road_id: "R005",
          road_name: "Civil Lines Perimeter Parkway",
          length_km: 16.4,
          current_density: 18.0,
          current_speed: 58.0,
          congestion_level: "Low",
          surface_condition: "Dry / Optimal",
          incident_active: false,
          estimated_delay_sec: 60,
        },
      ];

      const recommended: RoutePlan = {
        route_id: "RT-REC-01",
        name: "AI Intelligent Bypass (Outer Ring Corridor)",
        is_recommended: true,
        type: "primary_fastest",
        distance_km: 14.2,
        travel_time_minutes: 24,
        baseline_time_minutes: 18,
        congestion_delay_minutes: 4,
        average_speed_kmh: 48.6,
        congestion_level: "Low",
        corridors: ["Station Link", "Outer Ring Express", "Airport North"],
        coordinates: primaryCoordinates,
        savings_minutes: 14,
        eco_score: 92,
        segments: primarySegments,
        summary: "Avoids high congestion on MG Road. Continuous multi-lane elevated velocity.",
      };

      const alternates: RoutePlan[] = [
        {
          route_id: "RT-ALT-01",
          name: "Direct Arterial (Via Central MG Road)",
          is_recommended: false,
          type: "alternate_bypass",
          distance_km: 12.2,
          travel_time_minutes: 38,
          baseline_time_minutes: 20,
          congestion_delay_minutes: 18,
          average_speed_kmh: 19.3,
          congestion_level: "High",
          corridors: ["MG Road", "Airport Connector"],
          coordinates: alt1Coordinates,
          savings_minutes: -14,
          eco_score: 64,
          segments: alt1Segments,
          summary: "Shorter physical distance but penalized by 18 min bottleneck delay near Junction 4.",
        },
        {
          route_id: "RT-ALT-02",
          name: "Perimeter Parkway (Eco-Friendly Smooth Flow)",
          is_recommended: false,
          type: "alternate_eco",
          distance_km: 16.4,
          travel_time_minutes: 31,
          baseline_time_minutes: 26,
          congestion_delay_minutes: 5,
          average_speed_kmh: 52.0,
          congestion_level: "Low",
          corridors: ["Civil Lines Bypass", "Eastern Orbital"],
          coordinates: alt2Coordinates,
          savings_minutes: -7,
          eco_score: 96,
          segments: alt2Segments,
          summary: "Longer distance with zero stop-and-go queueing. Lowest brake wear and fuel emissions.",
        },
      ];

      return { recommended, alternates };
    };

    const res = await fetchWithFallback<{ recommended: RoutePlan; alternates: RoutePlan[] }>(
      `/route/optimize?origin=${originId}&destination=${destinationId}&preference=${preference}`,
      fallback
    );

    return {
      recommended: res.data.recommended,
      alternates: res.data.alternates,
      isLive: res.isLive,
    };
  },

  async getRouteTravel(routeId: string): Promise<{ travel: RouteTravelDetail; isLive: boolean }> {
    const fallback = (): RouteTravelDetail => {
      return {
        route_id: routeId,
        total_distance_km: 14.2,
        total_travel_time_min: 24,
        total_delay_min: 4,
        overall_condition: "Optimal / Clear Flow",
        segments: [
          {
            segment_id: "SEG-01",
            road_id: "R003",
            road_name: "Station Road Interchange",
            length_km: 2.4,
            current_density: 35.0,
            current_speed: 42.0,
            congestion_level: "Low",
            surface_condition: "Dry / Optimal",
            incident_active: false,
            estimated_delay_sec: 45,
          },
          {
            segment_id: "SEG-02",
            road_id: "R002",
            road_name: "Outer Ring Elevated Express",
            length_km: 8.6,
            current_density: 22.5,
            current_speed: 64.0,
            congestion_level: "Low",
            surface_condition: "Dry / Optimal",
            incident_active: false,
            estimated_delay_sec: 30,
          },
          {
            segment_id: "SEG-03",
            road_id: "R004",
            road_name: "Airport Northern Access Ramp",
            length_km: 3.2,
            current_density: 28.0,
            current_speed: 55.0,
            congestion_level: "Low",
            surface_condition: "Dry / Optimal",
            incident_active: false,
            estimated_delay_sec: 40,
          },
        ],
      };
    };

    const res = await fetchWithFallback<RouteTravelDetail>(`/route/travel?route_id=${routeId}`, fallback);
    return { travel: res.data, isLive: res.isLive };
  },

  // ==========================================
  // --- Milestone 2: Prediction Forecasting ---
  // ==========================================
  async getPredictionForecast(
    horizonMinutes: number = 30,
    scenario?: string
  ): Promise<{ forecast: PredictionHorizon; isLive: boolean }> {
    const fallback = (): PredictionHorizon => {
      let multiplier = 1.0;
      if (horizonMinutes === 15) multiplier = 1.05;
      else if (horizonMinutes === 30) multiplier = 1.15;
      else if (horizonMinutes === 60) multiplier = 1.30;
      else if (horizonMinutes === 120) multiplier = 1.45;

      if (scenario === "rain") multiplier *= 1.25;
      else if (scenario === "closure") multiplier *= 1.35;
      else if (scenario === "event") multiplier *= 1.4;

      const corridors: CorridorForecast[] = simulatedRoads.map((road) => {
        let basePred = road.density * multiplier;
        if (scenario === "closure" && road.road_id === "R001") {
          basePred = 95.0; // Lane closure gridlock
        }
        const predDensity = Math.min(98.0, Math.round(basePred * 10) / 10);
        const prob = Math.min(0.98, Math.round((predDensity / 100) * 100) / 100);

        let lvl: "Low" | "Medium" | "High" = "Low";
        if (predDensity > 50) lvl = "High";
        else if (predDensity >= 25) lvl = "Medium";

        let rec = "Flow predicted within normal buffer.";
        if (lvl === "High") {
          rec = "Critical surge predicted. Prepare traffic light phase extension (+25s).";
        } else if (lvl === "Medium") {
          rec = "Moderate ingress increase. Recommend dynamic advisory sign updates.";
        }

        return {
          road_id: road.road_id,
          road_name: road.name,
          current_density: road.density,
          predicted_density: predDensity,
          congestion_probability: prob,
          level: lvl,
          recommendation: rec,
          peak_surge: predDensity > 65,
        };
      });

      const bottlenecks = corridors.filter((c) => c.level === "High").map((c) => c.road_name);

      return {
        horizon_minutes: horizonMinutes,
        label: horizonMinutes === 0 ? "Real-time Telemetry" : `+${horizonMinutes} Minute Forecast`,
        avg_predicted_density: Math.round((corridors.reduce((a, b) => a + b.predicted_density, 0) / corridors.length) * 10) / 10,
        confidence_score: horizonMinutes <= 30 ? 0.91 : horizonMinutes <= 60 ? 0.86 : 0.79,
        bottlenecks_predicted: bottlenecks,
        corridors,
      };
    };

    const res = await fetchWithFallback<PredictionHorizon>(
      `/predict/forecast?horizon=${horizonMinutes}${scenario ? `&scenario=${scenario}` : ""}`,
      fallback
    );

    return { forecast: res.data, isLive: res.isLive };
  },

  // ==========================================
  // --- AI Recommendations Management (Intern 3: /ai/recommendations) ---
  // ==========================================
  async getRecommendations(): Promise<AIRecommendation[]> {
    const res = await fetchWithFallback<AIRecommendation[]>("/ai/recommendations", () => simulatedRecommendations);
    return res.data;
  },

  async applyRecommendation(id: string): Promise<AIRecommendation[]> {
    simulatedRecommendations = simulatedRecommendations.map((rec) => {
      if (rec.id === id) {
        return {
          ...rec,
          status: "applied" as const,
          applied_at: new Date().toISOString(),
        };
      }
      return rec;
    });

    // Simulated impact: reduce target road density slightly to show live effect
    const target = simulatedRecommendations.find((r) => r.id === id);
    if (target) {
      simulatedRoads = simulatedRoads.map((road) => {
        if (road.road_id === target.target_corridor_id) {
          const newDensity = Math.max(20, Math.round((road.density * 0.85) * 10) / 10);
          return {
            ...road,
            density: newDensity,
            congestion_level: newDensity > 50 ? "High" : newDensity >= 25 ? "Medium" : "Low",
            speed: Math.min(65, Math.round((road.speed + target.impact_speed_gain_kmh) * 10) / 10),
            trend: "down" as const,
          };
        }
        return road;
      });
    }

    await fetchWithFallback(`/ai/recommendations/${id}/apply`, () => ({ success: true, rec_id: id }), { method: "POST" });
    return simulatedRecommendations;
  },

  async dismissRecommendation(id: string): Promise<AIRecommendation[]> {
    simulatedRecommendations = simulatedRecommendations.map((rec) =>
      rec.id === id ? { ...rec, status: "dismissed" as const } : rec
    );
    await fetchWithFallback(`/ai/recommendations/${id}/dismiss`, () => ({ success: true, rec_id: id }), { method: "POST" });
    return simulatedRecommendations;
  },

  // ==========================================
  // --- Historical Analytics & Trends (Intern 2: /analytics/trends) ---
  // ==========================================
  async getHistoricalAnalytics(
    timeframe: "24h" | "7d" | "30d" = "24h",
    corridorId?: string
  ): Promise<{
    points: HistoricalTimeSeriesPoint[];
    summary: {
      avgDensity: number;
      avgSpeed: number;
      peakDensity: number;
      peakHour: string;
      totalVolume: number;
    };
  }> {
    const fallback = (): {
      points: HistoricalTimeSeriesPoint[];
      summary: {
        avgDensity: number;
        avgSpeed: number;
        peakDensity: number;
        peakHour: string;
        totalVolume: number;
      };
    } => {
      const points: HistoricalTimeSeriesPoint[] = [];

      if (timeframe === "24h") {
        // 24 hourly data points (00:00 to 23:00)
        for (let h = 0; h < 24; h++) {
          const isMorningPeak = h >= 8 && h <= 10;
          const isEveningPeak = h >= 17 && h <= 20;
          const isNight = h < 6;

          let baseDensity = 45;
          if (isMorningPeak) baseDensity = 78 + (h === 9 ? 8 : 0);
          else if (isEveningPeak) baseDensity = 84 + (h === 18 ? 6 : 0);
          else if (isNight) baseDensity = 12 + h * 2;
          else if (h >= 11 && h <= 16) baseDensity = 52 + ((h % 2) * 6);

          const corridorDensities: Record<string, number> = {};
          simulatedRoads.forEach((r) => {
            let multiplier = 1.0;
            if (r.road_id === "R003") multiplier = 1.15;
            if (r.road_id === "R001") multiplier = 1.08;
            if (r.road_id === "R004") multiplier = 0.65;
            const val = Math.min(96, Math.max(8, Math.round(baseDensity * multiplier * 10) / 10));
            corridorDensities[r.road_id] = val;
          });

          const effectiveDensity = corridorId && corridorDensities[corridorId]
            ? corridorDensities[corridorId]
            : baseDensity;

          const effectiveSpeed = Math.max(14, Math.round((70 - effectiveDensity * 0.6) * 10) / 10);

          points.push({
            timestamp: `2026-09-22T${h < 10 ? "0" + h : h}:00:00Z`,
            label: `${h < 10 ? "0" + h : h}:00`,
            network_avg_density: effectiveDensity,
            network_avg_speed: effectiveSpeed,
            corridor_densities: corridorDensities,
          });
        }
      } else if (timeframe === "7d") {
        const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        days.forEach((day, idx) => {
          const isWeekend = idx >= 5;
          const baseDensity = isWeekend ? 38 + (idx === 5 ? 8 : 2) : 68 + ((idx % 3) * 4);
          const corridorDensities: Record<string, number> = {};
          simulatedRoads.forEach((r) => {
            const val = Math.min(95, Math.max(15, Math.round(baseDensity * (r.road_id === "R003" ? 1.18 : r.road_id === "R004" ? 0.6 : 1.0))));
            corridorDensities[r.road_id] = val;
          });

          const effectiveDensity = corridorId && corridorDensities[corridorId] ? corridorDensities[corridorId] : baseDensity;

          points.push({
            timestamp: `Day -${6 - idx}`,
            label: day,
            network_avg_density: effectiveDensity,
            network_avg_speed: Math.max(16, Math.round((72 - effectiveDensity * 0.62) * 10) / 10),
            corridor_densities: corridorDensities,
          });
        });
      } else {
        // 30 days
        for (let d = 1; d <= 30; d++) {
          const isWeekend = d % 7 === 6 || d % 7 === 0;
          const baseDensity = isWeekend ? 42 + (d % 5) : 66 + ((d * 3) % 18);
          const corridorDensities: Record<string, number> = {};
          simulatedRoads.forEach((r) => {
            corridorDensities[r.road_id] = Math.min(94, Math.max(12, Math.round(baseDensity * (r.road_id === "R003" ? 1.14 : 0.95))));
          });

          points.push({
            timestamp: `Sep ${d}`,
            label: `${d}`,
            network_avg_density: baseDensity,
            network_avg_speed: Math.max(18, Math.round((70 - baseDensity * 0.58) * 10) / 10),
            corridor_densities: corridorDensities,
          });
        }
      }

      const densities = points.map((p) => p.network_avg_density);
      const speeds = points.map((p) => p.network_avg_speed);
      const maxDensity = Math.max(...densities);
      const peakPoint = points.find((p) => p.network_avg_density === maxDensity);

      return {
        points,
        summary: {
          avgDensity: Math.round((densities.reduce((a, b) => a + b, 0) / densities.length) * 10) / 10,
          avgSpeed: Math.round((speeds.reduce((a, b) => a + b, 0) / speeds.length) * 10) / 10,
          peakDensity: maxDensity,
          peakHour: peakPoint ? peakPoint.label : "18:00",
          totalVolume: 42850,
        },
      };
    };

    const res = await fetchWithFallback<{
      points: HistoricalTimeSeriesPoint[];
      summary: {
        avgDensity: number;
        avgSpeed: number;
        peakDensity: number;
        peakHour: string;
        totalVolume: number;
      };
    }>(
      `/analytics/trends?timeframe=${timeframe}${corridorId ? `&corridor_id=${corridorId}` : ""}`,
      fallback
    );
    return res.data;
  },

  // ==========================================
  // --- 7x24 Congestion Heatmap Matrix (Intern 2: /analytics/heatmap) ---
  // ==========================================
  async getCongestionHeatmap(corridorId?: string): Promise<HeatmapCell[]> {
    const fallback = (): HeatmapCell[] => {
      const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
      const cells: HeatmapCell[] = [];

      const targetRoad = simulatedRoads.find((r) => r.road_id === corridorId);
      const corridorMultiplier = targetRoad
        ? targetRoad.road_id === "R003"
          ? 1.2
          : targetRoad.road_id === "R004"
          ? 0.65
          : 1.0
        : 1.0;

      for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
        const dayName = days[dayIndex];
        const isWeekend = dayIndex >= 5;

        for (let hour = 0; hour < 24; hour++) {
          let base = 20;

          if (!isWeekend) {
            // Weekday traffic profile
            if (hour >= 0 && hour <= 5) base = 8 + hour * 1.5;
            else if (hour === 6) base = 28;
            else if (hour === 7) base = 56;
            else if (hour >= 8 && hour <= 10) base = 82 + (hour === 9 ? 9 : 0);
            else if (hour >= 11 && hour <= 15) base = 48 + ((hour % 3) * 5);
            else if (hour >= 16 && hour <= 19) base = 86 + (hour === 18 ? 8 : 0);
            else if (hour === 20) base = 68;
            else if (hour === 21) base = 44;
            else base = 24 - (hour - 22) * 6;
          } else {
            // Weekend traffic profile: later start, smoother hump
            if (hour <= 7) base = 6 + hour * 1.2;
            else if (hour >= 8 && hour <= 11) base = 28 + (hour - 8) * 6;
            else if (hour >= 12 && hour <= 17) base = 52 + ((hour % 4) * 3);
            else if (hour >= 18 && hour <= 21) base = 64 + (hour === 19 ? 5 : 0);
            else base = 32 - (hour - 22) * 8;
          }

          const density = Math.min(98, Math.max(5, Math.round(base * corridorMultiplier)));
          const speed = Math.max(12, Math.round(72 - density * 0.62));
          const congestion_level = density > 65 ? "High" : density >= 35 ? "Medium" : "Low";
          const incident_risk = density > 78 ? "critical" : density >= 52 ? "medium" : "low";
          const volume_count = Math.round(density * 2.8 + Math.random() * 12);

          cells.push({
            day_index: dayIndex,
            day_name: dayName,
            hour,
            density,
            speed,
            congestion_level,
            incident_risk,
            volume_count,
          });
        }
      }

      return cells;
    };

    const res = await fetchWithFallback<HeatmapCell[]>(
      `/analytics/heatmap${corridorId ? `?corridor_id=${corridorId}` : ""}`,
      fallback
    );
    return res.data;
  },

  // ==========================================
  // --- Historical Report Download Handlers ---
  // ==========================================
  downloadCsvReport(filter: HistoricalReportFilter) {
    const rows: string[] = [];
    rows.push("Timestamp,Corridor_ID,Corridor_Name,Density_Percent,Speed_KMH,Congestion_Level,Vehicle_Count,Incident_Active");

    const targetRoads = filter.corridorId === "all"
      ? simulatedRoads
      : simulatedRoads.filter((r) => r.road_id === filter.corridorId);

    const now = Date.now();
    const count = filter.dateRange === "24h" ? 24 : filter.dateRange === "7d" ? 7 : 30;
    const intervalMs = filter.dateRange === "24h" ? 3600000 : 86400000;

    for (let i = count - 1; i >= 0; i--) {
      const timeStr = new Date(now - i * intervalMs).toISOString();
      targetRoads.forEach((road) => {
        const variance = ((i * 7 + road.name.length) % 15) - 7;
        const density = Math.min(98, Math.max(10, Math.round(road.density + variance)));
        const speed = Math.max(14, Math.round(72 - density * 0.6));
        const level = density > 50 ? "High" : density >= 25 ? "Medium" : "Low";
        const vehicleCount = Math.round(density * 1.8 + 20);
        const incident = density > 75 ? "YES" : "NO";

        rows.push(`"${timeStr}","${road.road_id}","${road.name}",${density},${speed},"${level}",${vehicleCount},"${incident}"`);
      });
    }

    const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(rows.join("\n"));
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", `TrafficVision_Historical_Report_${filter.dateRange}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  downloadJsonReport(filter: HistoricalReportFilter) {
    const targetRoads = filter.corridorId === "all"
      ? simulatedRoads
      : simulatedRoads.filter((r) => r.road_id === filter.corridorId);

    const exportPayload = {
      system: "TrafficVision AI - Intelligent Congestion Management",
      report_type: "Historical Telemetry & Congestion Audit",
      generated_at: new Date().toISOString(),
      filter: filter,
      summary_kpis: {
        total_corridors_analyzed: targetRoads.length,
        network_average_density: Math.round((targetRoads.reduce((a, b) => a + b.density, 0) / targetRoads.length) * 10) / 10,
        network_average_speed_kmh: Math.round((targetRoads.reduce((a, b) => a + b.speed, 0) / targetRoads.length) * 10) / 10,
        active_incidents_logged: simulatedAlerts.filter((a) => a.status === "active").length,
        total_recommendations_count: simulatedRecommendations.length,
      },
      corridors: targetRoads,
      alerts: filter.includeAlerts ? simulatedAlerts : undefined,
      recommendations: filter.includeRecommendations ? simulatedRecommendations : undefined,
    };

    const jsonString = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportPayload, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", jsonString);
    link.setAttribute("download", `TrafficVision_Data_Export_${filter.dateRange}_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  downloadHtmlExecutiveReport(filter: HistoricalReportFilter) {
    const targetRoads = filter.corridorId === "all"
      ? simulatedRoads
      : simulatedRoads.filter((r) => r.road_id === filter.corridorId);

    const avgDensity = Math.round((targetRoads.reduce((a, b) => a + b.density, 0) / targetRoads.length) * 10) / 10;
    const avgSpeed = Math.round((targetRoads.reduce((a, b) => a + b.speed, 0) / targetRoads.length) * 10) / 10;

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TrafficVision AI - Executive Mobility Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #090d16; color: #f1f5f9; padding: 40px; margin: 0; }
    .header { border-bottom: 2px solid #1e293b; padding-bottom: 24px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-start; }
    h1 { margin: 0 0 8px; color: #38bdf8; font-size: 26px; }
    .meta { font-size: 12px; color: #94a3b8; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
    .kpi-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 18px; }
    .kpi-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-val { font-size: 28px; font-weight: 800; color: #f8fafc; margin-top: 6px; }
    table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }
    th { text-align: left; padding: 12px; background: #1e293b; color: #cbd5e1; font-weight: 600; text-transform: uppercase; font-size: 11px; }
    td { padding: 12px; border-bottom: 1px solid #1e293b; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; }
    .badge-high { background: rgba(244,63,94,0.15); color: #fb7185; border: 1px solid rgba(244,63,94,0.3); }
    .badge-med { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
    .badge-low { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
    .section-title { font-size: 16px; font-weight: 700; color: #e2e8f0; margin-top: 32px; margin-bottom: 12px; }
    .rec-item { background: #0f172a; border-left: 4px solid #38bdf8; border-radius: 6px; padding: 14px; margin-bottom: 12px; }
    .rec-title { font-weight: 700; color: #38bdf8; font-size: 14px; }
    .rec-desc { font-size: 12px; color: #cbd5e1; margin-top: 4px; }
    @media print { body { background: #fff; color: #000; padding: 20px; } .kpi-card { background: #f8fafc; border: 1px solid #cbd5e1; } .kpi-val { color: #000; } }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>🚦 TrafficVision AI • Executive Traffic & Congestion Report</h1>
      <div class="meta">Automated Intelligence Summary | Scope: ${filter.dateRange.toUpperCase()} | Generated: ${new Date().toLocaleString()}</div>
    </div>
    <button onclick="window.print()" style="background:#0284c7;color:#fff;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-weight:600;">Print / Save PDF</button>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-title">Average Network Density</div>
      <div class="kpi-val" style="color: ${avgDensity > 50 ? '#fb7185' : '#34d399'}">${avgDensity}%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Network Flow Velocity</div>
      <div class="kpi-val">${avgSpeed} <span style="font-size: 14px; font-weight: normal; color: #94a3b8;">km/h</span></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Active Critical Bottlenecks</div>
      <div class="kpi-val" style="color: #f59e0b;">${targetRoads.filter((r) => r.density > 50).length} / ${targetRoads.length}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">AI Optimizations Proposed</div>
      <div class="kpi-val" style="color: #38bdf8;">${simulatedRecommendations.length}</div>
    </div>
  </div>

  <div class="section-title">Corridor Performance & Congestion Audit</div>
  <table>
    <thead>
      <tr>
        <th>Corridor ID</th>
        <th>Corridor Name</th>
        <th>Current Density</th>
        <th>Flow Speed</th>
        <th>Congestion Index</th>
        <th>Vehicle Flow</th>
      </tr>
    </thead>
    <tbody>
      ${targetRoads.map((r) => `
        <tr>
          <td><code>${r.road_id}</code></td>
          <td><strong>${r.name}</strong></td>
          <td>${r.density}%</td>
          <td>${r.speed} km/h</td>
          <td><span class="badge ${r.density > 50 ? 'badge-high' : r.density >= 25 ? 'badge-med' : 'badge-low'}">${r.congestion_level}</span></td>
          <td>${r.vehicle_count} veh/min</td>
        </tr>
      `).join("")}
    </tbody>
  </table>

  <div class="section-title">Active AI Mitigation Recommendations</div>
  <div>
    ${simulatedRecommendations.slice(0, 3).map((rec) => `
      <div class="rec-item">
        <div class="rec-title">${rec.title} • [${rec.priority.toUpperCase()}]</div>
        <div class="rec-desc"><strong>Target:</strong> ${rec.target_corridor_name} | <strong>Expected Delay Reduction:</strong> -${rec.impact_delay_reduction_pct}% | <strong>Confidence:</strong> ${(rec.confidence * 100).toFixed(0)}%</div>
        <div class="rec-desc" style="color: #94a3b8; margin-top: 6px;">${rec.action_plan}</div>
      </div>
    `).join("")}
  </div>
</body>
</html>`;

    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const win = window.open(url, "_blank");
    if (!win) {
      const link = document.createElement("a");
      link.href = url;
      link.download = `TrafficVision_Executive_Report_${new Date().toISOString().slice(0, 10)}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  },
};

