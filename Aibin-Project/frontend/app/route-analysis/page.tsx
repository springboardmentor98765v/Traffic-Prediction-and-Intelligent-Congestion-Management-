"use client";

import React, { useState, useEffect } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import LeafletMapWrapper from "../components/LeafletMapWrapper";
import type { MapMarker, MapRoute } from "../components/LeafletMap";
import { api, RouteLocation, RoutePlan, RouteSegment } from "../lib/api";
import { useAuth } from "../lib/auth-context";

export default function RouteAnalysisPage() {
  const { role } = useAuth();
  const [locations, setLocations] = useState<RouteLocation[]>([]);
  const [originId, setOriginId] = useState<string>("LOC-01"); // Station Hub
  const [destinationId, setDestinationId] = useState<string>("LOC-04"); // Airport Terminal
  const [preference, setPreference] = useState<"fastest" | "least_congested" | "eco">("fastest");
  const [loading, setLoading] = useState<boolean>(false);

  const [recommendedRoute, setRecommendedRoute] = useState<RoutePlan | null>(null);
  const [alternateRoutes, setAlternateRoutes] = useState<RoutePlan[]>([]);
  const [selectedRouteId, setSelectedRouteId] = useState<string>("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Initialize locations and first route calculation
  useEffect(() => {
    const locs = api.getRouteLocations();
    setLocations(locs);
    calculateRoutes("LOC-01", "LOC-04", "fastest");
  }, []);

  const calculateRoutes = async (orig: string, dest: string, pref: "fastest" | "least_congested" | "eco") => {
    setLoading(true);
    try {
      const res = await api.optimizeRoute(orig, dest, pref);
      setRecommendedRoute(res.recommended);
      setAlternateRoutes(res.alternates);
      setSelectedRouteId(res.recommended.route_id);
    } catch (err) {
      console.error("Route calculation error", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    const temp = originId;
    setOriginId(destinationId);
    setDestinationId(temp);
    calculateRoutes(destinationId, temp, preference);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const activePlan =
    selectedRouteId === recommendedRoute?.route_id
      ? recommendedRoute
      : alternateRoutes.find((a) => a.route_id === selectedRouteId) || recommendedRoute;

  // Build Leaflet Markers
  const origObj = locations.find((l) => l.id === originId);
  const destObj = locations.find((l) => l.id === destinationId);

  const mapMarkers: MapMarker[] = [];
  if (origObj) {
    mapMarkers.push({
      position: origObj.coordinates,
      title: `Origin: ${origObj.name}`,
      type: "origin",
      popupHtml: `
        <div style="padding: 2px;">
          <strong style="color: #10b981; font-size: 13px;">🟢 Origin Point</strong>
          <div style="font-weight: bold; font-size: 12px; margin-top: 2px; color: #f1f5f9;">${origObj.name}</div>
          <div style="font-size: 11px; color: #94a3b8;">${origObj.address}</div>
        </div>
      `,
    });
  }

  if (destObj) {
    mapMarkers.push({
      position: destObj.coordinates,
      title: `Destination: ${destObj.name}`,
      type: "destination",
      popupHtml: `
        <div style="padding: 2px;">
          <strong style="color: #ef4444; font-size: 13px;">🏁 Destination</strong>
          <div style="font-weight: bold; font-size: 12px; margin-top: 2px; color: #f1f5f9;">${destObj.name}</div>
          <div style="font-size: 11px; color: #94a3b8;">${destObj.address}</div>
        </div>
      `,
    });
  }

  // Build Leaflet Polylines
  const mapRoutes: MapRoute[] = [];
  if (recommendedRoute) {
    mapRoutes.push({
      id: recommendedRoute.route_id,
      coordinates: recommendedRoute.coordinates,
      color: "#06b6d4", // Neon Cyan
      weight: 6,
      opacity: 0.95,
      popupHtml: `
        <div>
          <strong style="color: #06b6d4;">⚡ ${recommendedRoute.name}</strong>
          <div style="font-size: 11px; margin-top: 2px;">${recommendedRoute.travel_time_minutes} min • ${recommendedRoute.distance_km} km • ${recommendedRoute.average_speed_kmh} km/h</div>
          <div style="font-size: 10px; color: #10b981; font-weight: bold;">Saves ${recommendedRoute.savings_minutes} min vs gridlock</div>
        </div>
      `,
    });
  }

  alternateRoutes.forEach((alt, idx) => {
    mapRoutes.push({
      id: alt.route_id,
      coordinates: alt.coordinates,
      color: idx === 0 ? "#f59e0b" : "#a855f7", // Amber or Purple
      weight: 5,
      opacity: 0.8,
      dashArray: "8, 6",
      popupHtml: `
        <div>
          <strong style="color: ${idx === 0 ? "#f59e0b" : "#a855f7"};">🚗 ${alt.name}</strong>
          <div style="font-size: 11px; margin-top: 2px;">${alt.travel_time_minutes} min • ${alt.distance_km} km</div>
          <div style="font-size: 10px; color: #94a3b8;">${alt.summary}</div>
        </div>
      `,
    });
  });

  return (
    <Layout>
      <div className="space-y-6">
        {/* Toast Feedback */}
        {toastMessage && (
          <div className="fixed top-16 right-6 z-50 rounded-xl border border-cyan-500/40 bg-slate-900/95 p-4 text-xs font-semibold text-cyan-300 shadow-2xl backdrop-blur-xl animate-fadeIn">
            ✓ {toastMessage}
          </div>
        )}

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>TrafficVision AI</span>
              <span>›</span>
              <span className="text-cyan-400 font-semibold">Milestone 2</span>
              <span>›</span>
              <span className="text-slate-200">Route Analysis</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1 flex items-center gap-2.5">
              <span>Intelligent Route Optimization & Telemetry</span>
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Leaflet + OSM
              </span>
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => showToast("Route diversion advisory dispatched to regional variable message displays.")}
              className="flex items-center gap-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 px-3.5 py-2 text-xs font-semibold text-slate-200 transition shadow-sm"
            >
              <span>📡</span>
              <span>Broadcast Route Advisory</span>
            </button>
          </div>
        </div>

        {/* Main Grid: Parameters & Interactive Leaflet Map */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Route Query & Controls */}
          <div className="space-y-4">
            <Card
              title="Route Parameters"
              subtitle="Select origin & destination network nodes"
              icon="🧭"
            >
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  calculateRoutes(originId, destinationId, preference);
                }}
                className="space-y-4 mt-2"
              >
                {/* Origin Selector */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-400"></span> Origin Node
                  </label>
                  <select
                    value={originId}
                    onChange={(e) => setOriginId(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none transition"
                  >
                    {locations.map((loc) => (
                      <option key={loc.id} value={loc.id} disabled={loc.id === destinationId}>
                        {loc.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Swap Button */}
                <div className="flex justify-center -my-1">
                  <button
                    type="button"
                    onClick={handleSwap}
                    className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-800 hover:bg-cyan-600 hover:text-white text-slate-400 border border-slate-700 text-xs transition"
                    title="Swap Origin and Destination"
                  >
                    ⇅
                  </button>
                </div>

                {/* Destination Selector */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-rose-500"></span> Destination Node
                  </label>
                  <select
                    value={destinationId}
                    onChange={(e) => setDestinationId(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none transition"
                  >
                    {locations.map((loc) => (
                      <option key={loc.id} value={loc.id} disabled={loc.id === originId}>
                        {loc.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Optimization Preference */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Optimization Objective
                  </label>
                  <div className="grid grid-cols-3 gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px]">
                    <button
                      type="button"
                      onClick={() => setPreference("fastest")}
                      className={`py-1.5 px-2 rounded-lg font-semibold transition text-center ${
                        preference === "fastest"
                          ? "bg-cyan-600 text-white shadow"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      ⚡ Fastest
                    </button>
                    <button
                      type="button"
                      onClick={() => setPreference("least_congested")}
                      className={`py-1.5 px-2 rounded-lg font-semibold transition text-center ${
                        preference === "least_congested"
                          ? "bg-cyan-600 text-white shadow"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      🚗 Fluid Flow
                    </button>
                    <button
                      type="button"
                      onClick={() => setPreference("eco")}
                      className={`py-1.5 px-2 rounded-lg font-semibold transition text-center ${
                        preference === "eco"
                          ? "bg-cyan-600 text-white shadow"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      🌿 Eco-Route
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:brightness-110 py-3 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 transition flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin">🔄</span>
                      <span>Calculating Congestion Paths...</span>
                    </>
                  ) : (
                    <span>Calculate Intelligent Route →</span>
                  )}
                </button>
              </form>
            </Card>

            {/* Quick Route Summary Card */}
            {activePlan && (
              <Card
                title={activePlan.name}
                subtitle={`${activePlan.distance_km} km • ${activePlan.travel_time_minutes} min estimated`}
                icon="⚡"
                badge={
                  <Badge variant={activePlan.congestion_level}>
                    {activePlan.congestion_level} Congestion
                  </Badge>
                }
              >
                <div className="space-y-3 mt-1 text-xs">
                  <p className="text-slate-300 leading-relaxed">{activePlan.summary}</p>

                  <div className="grid grid-cols-2 gap-2 text-center pt-1">
                    <div className="rounded-xl bg-slate-950 p-2.5 border border-slate-800">
                      <div className="text-[10px] text-slate-400">Time Penalty</div>
                      <div className="text-base font-extrabold text-amber-400 mt-0.5">
                        +{activePlan.congestion_delay_minutes} min
                      </div>
                    </div>
                    <div className="rounded-xl bg-slate-950 p-2.5 border border-slate-800">
                      <div className="text-[10px] text-slate-400">Eco Score</div>
                      <div className="text-base font-extrabold text-emerald-400 mt-0.5">
                        {activePlan.eco_score} / 100
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Right Columns: Interactive Leaflet Map (2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 shadow-2xl">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
                <div className="flex items-center gap-2">
                  <span className="flex h-2.5 w-2.5 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-200">
                    OPENSTREETMAP CARRIER ENGINE • ROUTE VECTORS ACTIVE
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-5 rounded bg-cyan-500 inline-block"></span> Recommended
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-5 rounded bg-amber-500 border-dashed border border-amber-300 inline-block"></span> Alternate 1
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-5 rounded bg-purple-500 border-dashed border border-purple-300 inline-block"></span> Alternate 2
                  </span>
                </div>
              </div>

              {/* Dynamic Leaflet Map */}
              <LeafletMapWrapper
                center={[12.9716, 77.5946]}
                zoom={12}
                markers={mapMarkers}
                routes={mapRoutes}
                selectedRouteId={selectedRouteId}
                onRouteClick={(id) => setSelectedRouteId(id)}
                height="460px"
              />
            </div>
          </div>
        </div>

        {/* Multi-Route Side-by-Side Comparison Cards */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <span>📊</span> Multi-Route Comparison (Consuming /route/travel)
            </h3>
            <span className="text-xs text-slate-500">Click any card to highlight route on map</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Recommended Route Card */}
            {recommendedRoute && (
              <div
                onClick={() => setSelectedRouteId(recommendedRoute.route_id)}
                className={`rounded-2xl border p-5 transition cursor-pointer relative ${
                  selectedRouteId === recommendedRoute.route_id
                    ? "border-cyan-500 bg-cyan-950/20 shadow-lg shadow-cyan-500/10"
                    : "border-slate-800 bg-slate-900/60 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                    ⚡ AI Recommended
                  </span>
                  <span className="text-xs font-extrabold text-emerald-400">
                    Saves {recommendedRoute.savings_minutes} min
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white mt-3">{recommendedRoute.name}</h4>

                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-2xl font-black text-cyan-400">
                    {recommendedRoute.travel_time_minutes} min
                  </span>
                  <span className="text-xs text-slate-400">
                    {recommendedRoute.distance_km} km • {recommendedRoute.average_speed_kmh} km/h avg
                  </span>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-800 text-[11px] text-slate-300 space-y-1">
                  <div>Baseline Time: {recommendedRoute.baseline_time_minutes} min (Delay: +{recommendedRoute.congestion_delay_minutes}m)</div>
                  <div>Traversed: {recommendedRoute.corridors.join(" → ")}</div>
                </div>
              </div>
            )}

            {/* Alternate 1 Card */}
            {alternateRoutes[0] && (
              <div
                onClick={() => setSelectedRouteId(alternateRoutes[0].route_id)}
                className={`rounded-2xl border p-5 transition cursor-pointer ${
                  selectedRouteId === alternateRoutes[0].route_id
                    ? "border-amber-500 bg-amber-950/20 shadow-lg shadow-amber-500/10"
                    : "border-slate-800 bg-slate-900/60 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    🚗 Alternate 1 (Direct)
                  </span>
                  <span className="text-xs font-semibold text-rose-400">
                    +{alternateRoutes[0].travel_time_minutes - (recommendedRoute?.travel_time_minutes || 0)} min slower
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white mt-3">{alternateRoutes[0].name}</h4>

                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-2xl font-black text-amber-400">
                    {alternateRoutes[0].travel_time_minutes} min
                  </span>
                  <span className="text-xs text-slate-400">
                    {alternateRoutes[0].distance_km} km • {alternateRoutes[0].average_speed_kmh} km/h avg
                  </span>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-800 text-[11px] text-slate-300 space-y-1">
                  <div>Congestion Delay: +{alternateRoutes[0].congestion_delay_minutes} min (High Queueing)</div>
                  <div className="text-slate-400">{alternateRoutes[0].summary}</div>
                </div>
              </div>
            )}

            {/* Alternate 2 Card */}
            {alternateRoutes[1] && (
              <div
                onClick={() => setSelectedRouteId(alternateRoutes[1].route_id)}
                className={`rounded-2xl border p-5 transition cursor-pointer ${
                  selectedRouteId === alternateRoutes[1].route_id
                    ? "border-purple-500 bg-purple-950/20 shadow-lg shadow-purple-500/10"
                    : "border-slate-800 bg-slate-900/60 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40">
                    🌿 Alternate 2 (Eco)
                  </span>
                  <span className="text-xs font-semibold text-emerald-400">
                    Eco Score: {alternateRoutes[1].eco_score}/100
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white mt-3">{alternateRoutes[1].name}</h4>

                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-2xl font-black text-purple-400">
                    {alternateRoutes[1].travel_time_minutes} min
                  </span>
                  <span className="text-xs text-slate-400">
                    {alternateRoutes[1].distance_km} km • {alternateRoutes[1].average_speed_kmh} km/h avg
                  </span>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-800 text-[11px] text-slate-300 space-y-1">
                  <div>Zero stop-and-go idling • Smooth perimeter cruise</div>
                  <div className="text-slate-400">{alternateRoutes[1].summary}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Road Conditions Breakdown Table (Consuming /route/travel) */}
        {activePlan && activePlan.segments && (
          <Card
            title={`Corridor Telemetry & Road Conditions — ${activePlan.name}`}
            subtitle="Real-time telemetry per segment along the active path"
            icon="🛣️"
          >
            <div className="overflow-x-auto mt-2">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                    <th className="pb-3 font-semibold">Corridor Segment</th>
                    <th className="pb-3 font-semibold">Distance</th>
                    <th className="pb-3 font-semibold">Velocity</th>
                    <th className="pb-3 font-semibold">Density</th>
                    <th className="pb-3 font-semibold">Surface Condition</th>
                    <th className="pb-3 font-semibold">Incident Risk</th>
                    <th className="pb-3 font-semibold text-right">Delay Penalty</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {activePlan.segments.map((seg) => (
                    <tr key={seg.segment_id} className="hover:bg-slate-900/50 transition">
                      <td className="py-3">
                        <div className="font-semibold text-slate-100">{seg.road_name}</div>
                        <div className="text-[10px] font-mono text-slate-500">{seg.road_id}</div>
                      </td>
                      <td className="py-3 font-mono text-slate-300">{seg.length_km} km</td>
                      <td className="py-3 font-mono font-bold text-emerald-400">{seg.current_speed} km/h</td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{seg.current_density}%</span>
                          <Badge variant={seg.congestion_level}>{seg.congestion_level}</Badge>
                        </div>
                      </td>
                      <td className="py-3">
                        <span className="text-slate-300 flex items-center gap-1.5">
                          <span>🛣️</span> {seg.surface_condition}
                        </span>
                      </td>
                      <td className="py-3">
                        {seg.incident_active ? (
                          <span className="inline-flex items-center gap-1 text-rose-400 font-semibold text-[11px]">
                            ⚠️ Active Bottleneck
                          </span>
                        ) : (
                          <span className="text-emerald-400 font-semibold text-[11px]">
                            ✓ Clear Route
                          </span>
                        )}
                      </td>
                      <td className="py-3 text-right font-mono font-bold text-slate-200">
                        +{seg.estimated_delay_sec}s
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
}
