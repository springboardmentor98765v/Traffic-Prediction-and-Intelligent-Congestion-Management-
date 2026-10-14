"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from "react";
import { api, TrafficRoad, DensityMetrics, TrafficAlert, AIRecommendation, INITIAL_ROADS } from "./api";

interface TrafficContextType {
  roads: TrafficRoad[];
  metrics: DensityMetrics;
  alerts: TrafficAlert[];
  recommendations: AIRecommendation[];
  isLiveBackend: boolean;
  isLoading: boolean;
  lastUpdated: Date;
  selectedRoad: TrafficRoad | null;
  setSelectedRoad: (road: TrafficRoad | null) => void;
  autoRefresh: boolean;
  setAutoRefresh: (enabled: boolean) => void;
  refreshData: () => Promise<void>;
  acknowledgeAlert: (alertId: string) => Promise<void>;
  resolveAlert: (alertId: string) => Promise<void>;
  broadcastIncident: (roadId: string, title: string, message: string, severity: "critical" | "warning" | "advisory") => Promise<void>;
  applyRecommendation: (id: string) => Promise<void>;
  dismissRecommendation: (id: string) => Promise<void>;
  refreshRecommendations: () => Promise<void>;
}

const TrafficContext = createContext<TrafficContextType | undefined>(undefined);

export function TrafficProvider({ children }: { children: ReactNode }) {
  const [roads, setRoads] = useState<TrafficRoad[]>(INITIAL_ROADS);
  const [metrics, setMetrics] = useState<DensityMetrics>({
    average_density: 51.2,
    total_roads: 5,
    congested_roads: 2,
    network_speed_avg: 36.4,
    timestamp: new Date().toISOString(),
  });
  const [alerts, setAlerts] = useState<TrafficAlert[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isLiveBackend, setIsLiveBackend] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [selectedRoad, setSelectedRoad] = useState<TrafficRoad | null>(null);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);

  const refreshData = useCallback(async () => {
    try {
      const [trafficRes, metricsRes, alertsRes, recsRes] = await Promise.all([
        api.getLiveTraffic(),
        api.getDensityMetrics(),
        api.getAlerts(),
        api.getRecommendations(),
      ]);

      setRoads(trafficRes.roads);
      setIsLiveBackend(trafficRes.isLive);
      setMetrics(metricsRes.metrics);
      setAlerts(alertsRes);
      setRecommendations(recsRes);
      setLastUpdated(new Date());

      // Keep selected road reference updated
      if (selectedRoad) {
        const updated = trafficRes.roads.find((r) => r.road_id === selectedRoad.road_id);
        if (updated) setSelectedRoad(updated);
      }
    } catch (err) {
      console.error("Traffic poll failed", err);
    }
  }, [selectedRoad]);

  // Initial load
  useEffect(() => {
    setIsLoading(true);
    refreshData().finally(() => setIsLoading(false));
  }, []);

  // Periodic 5s polling interval
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      refreshData();
    }, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshData]);

  const acknowledgeAlert = async (alertId: string) => {
    const updated = await api.acknowledgeAlert(alertId);
    setAlerts([...updated]);
  };

  const resolveAlert = async (alertId: string) => {
    const updated = await api.resolveAlert(alertId);
    setAlerts([...updated]);
  };

  const broadcastIncident = async (roadId: string, title: string, message: string, severity: "critical" | "warning" | "advisory") => {
    const newAlert = await api.broadcastIncident(roadId, title, message, severity);
    setAlerts((prev) => [newAlert, ...prev]);
  };

  const applyRecommendation = async (id: string) => {
    const updated = await api.applyRecommendation(id);
    setRecommendations([...updated]);
    // Refresh live roads after applying optimization to reflect lower congestion
    const trafficRes = await api.getLiveTraffic();
    setRoads(trafficRes.roads);
  };

  const dismissRecommendation = async (id: string) => {
    const updated = await api.dismissRecommendation(id);
    setRecommendations([...updated]);
  };

  const refreshRecommendations = async () => {
    const recs = await api.getRecommendations();
    setRecommendations(recs);
  };

  return (
    <TrafficContext.Provider
      value={{
        roads,
        metrics,
        alerts,
        recommendations,
        isLiveBackend,
        isLoading,
        lastUpdated,
        selectedRoad,
        setSelectedRoad,
        autoRefresh,
        setAutoRefresh,
        refreshData,
        acknowledgeAlert,
        resolveAlert,
        broadcastIncident,
        applyRecommendation,
        dismissRecommendation,
        refreshRecommendations,
      }}
    >
      {children}
    </TrafficContext.Provider>
  );
}

export function useTraffic(): TrafficContextType {
  const context = useContext(TrafficContext);
  if (!context) {
    throw new Error("useTraffic must be used within a TrafficProvider");
  }
  return context;
}
