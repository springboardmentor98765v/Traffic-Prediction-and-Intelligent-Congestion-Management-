"use client";

import React, { useState, useEffect } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import LeafletMapWrapper from "../components/LeafletMapWrapper";
import type { MapMarker, MapRoute } from "../components/LeafletMap";
import { api, RouteLocation, RoutePlan, RouteSegment } from "../lib/api";
import { useAuth } from "../lib/auth-context";

interface SelectedPoint {
  id: string;
  name: string;
  coordinates: [number, number];
  address?: string;
  isCustom?: boolean;
}

export default function RouteAnalysisPage() {
  const { role } = useAuth();
  const [locations, setLocations] = useState<RouteLocation[]>([]);

  // Dynamic Origin and Destination Points
  const [originPoint, setOriginPoint] = useState<SelectedPoint>({
    id: "LOC-01",
    name: "Station Road Rail & Transit Hub",
    coordinates: [12.9784, 77.5684],
    address: "Station Road Central Concourse, Zone 1",
    isCustom: false,
  });

  const [destPoint, setDestPoint] = useState<SelectedPoint>({
    id: "LOC-04",
    name: "Airport Expressway Terminal",
    coordinates: [13.0125, 77.6582],
    address: "Airport Northern Access Highway, Sector 9",
    isCustom: false,
  });

  // Map Interaction & Selection Modes
  const [selectionMode, setSelectionMode] = useState<"none" | "origin" | "destination">("none");
  const [showAllNodes, setShowAllNodes] = useState<boolean>(true);
  const [showManualInputs, setShowManualInputs] = useState<boolean>(false);

  // Manual Coordinates Input States
  const [manualOrigLat, setManualOrigLat] = useState<string>("12.9784");
  const [manualOrigLng, setManualOrigLng] = useState<string>("77.5684");
  const [manualDestLat, setManualDestLat] = useState<string>("13.0125");
  const [manualDestLng, setManualDestLng] = useState<string>("77.6582");

  const [preference, setPreference] = useState<"fastest" | "least_congested" | "eco">("fastest");
  const [loading, setLoading] = useState<boolean>(false);

  const [recommendedRoute, setRecommendedRoute] = useState<RoutePlan | null>(null);
  const [alternateRoutes, setAlternateRoutes] = useState<RoutePlan[]>([]);
  const [selectedRouteId, setSelectedRouteId] = useState<string>("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Initialize locations and initial route
  useEffect(() => {
    const locs = api.getRouteLocations();
    setLocations(locs);
    calculateRoutes(originPoint, destPoint, "fastest");
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const calculateRoutes = async (
    orig: SelectedPoint,
    dest: SelectedPoint,
    pref: "fastest" | "least_congested" | "eco"
  ) => {
    setLoading(true);
    try {
      const res = await api.optimizeRoute(
        { id: orig.id, name: orig.name, coordinates: orig.coordinates },
        { id: dest.id, name: dest.name, coordinates: dest.coordinates },
        pref
      );
      setRecommendedRoute(res.recommended);
      setAlternateRoutes(res.alternates);
      setSelectedRouteId(res.recommended.route_id);
    } catch (err) {
      console.error("Route calculation error", err);
      showToast("Error calculating dynamic route path");
    } finally {
      setLoading(false);
    }
  };

  // Handle Point Selection from Map Click or Popup Buttons
  const handleSelectPoint = (
    type: "origin" | "destination",
    coords: [number, number],
    label?: string
  ) => {
    // Check if coords match an existing landmark within 0.005 distance
    const matchedLoc = locations.find(
      (loc) =>
        Math.abs(loc.coordinates[0] - coords[0]) < 0.005 &&
        Math.abs(loc.coordinates[1] - coords[1]) < 0.005
    );

    const pointName =
      matchedLoc?.name || label || `Map Point (${coords[0].toFixed(4)}, ${coords[1].toFixed(4)})`;
    const pointAddress =
      matchedLoc?.address || `Custom GPS: ${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}`;

    if (type === "origin") {
      const newOrig: SelectedPoint = {
        id: matchedLoc ? matchedLoc.id : "CUSTOM-ORIG",
        name: pointName,
        coordinates: coords,
        address: pointAddress,
        isCustom: !matchedLoc,
      };
      setOriginPoint(newOrig);
      setManualOrigLat(coords[0].toFixed(4));
      setManualOrigLng(coords[1].toFixed(4));
      setSelectionMode("none");
      showToast(`🟢 Origin set: ${pointName}`);
      calculateRoutes(newOrig, destPoint, preference);
    } else {
      const newDest: SelectedPoint = {
        id: matchedLoc ? matchedLoc.id : "CUSTOM-DEST",
        name: pointName,
        coordinates: coords,
        address: pointAddress,
        isCustom: !matchedLoc,
      };
      setDestPoint(newDest);
      setManualDestLat(coords[0].toFixed(4));
      setManualDestLng(coords[1].toFixed(4));
      setSelectionMode("none");
      showToast(`🏁 Destination set: ${pointName}`);
      calculateRoutes(originPoint, newDest, preference);
    }
  };

  // Quick Dropdown Change for Origin
  const handleOriginDropdownChange = (val: string) => {
    if (val === "custom") return;
    const loc = locations.find((l) => l.id === val);
    if (loc) {
      const newOrig: SelectedPoint = {
        id: loc.id,
        name: loc.name,
        coordinates: loc.coordinates,
        address: loc.address,
        isCustom: false,
      };
      setOriginPoint(newOrig);
      setManualOrigLat(loc.coordinates[0].toFixed(4));
      setManualOrigLng(loc.coordinates[1].toFixed(4));
      calculateRoutes(newOrig, destPoint, preference);
    }
  };

  // Quick Dropdown Change for Destination
  const handleDestDropdownChange = (val: string) => {
    if (val === "custom") return;
    const loc = locations.find((l) => l.id === val);
    if (loc) {
      const newDest: SelectedPoint = {
        id: loc.id,
        name: loc.name,
        coordinates: loc.coordinates,
        address: loc.address,
        isCustom: false,
      };
      setDestPoint(newDest);
      setManualDestLat(loc.coordinates[0].toFixed(4));
      setManualDestLng(loc.coordinates[1].toFixed(4));
      calculateRoutes(originPoint, newDest, preference);
    }
  };

  // Swap Origin and Destination
  const handleSwap = () => {
    const tempOrig = originPoint;
    const tempDest = destPoint;
    setOriginPoint(tempDest);
    setDestPoint(tempOrig);
    setManualOrigLat(tempDest.coordinates[0].toFixed(4));
    setManualOrigLng(tempDest.coordinates[1].toFixed(4));
    setManualDestLat(tempOrig.coordinates[0].toFixed(4));
    setManualDestLng(tempOrig.coordinates[1].toFixed(4));
    showToast("Swapped Origin & Destination");
    calculateRoutes(tempDest, tempOrig, preference);
  };

  // Device Geolocation (HTML5 GPS)
  const handleUseGeolocation = () => {
    if (!navigator.geolocation) {
      showToast("Geolocation is not supported by your browser");
      return;
    }

    showToast("Detecting your live device GPS location...");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords: [number, number] = [
          Math.round(pos.coords.latitude * 10000) / 10000,
          Math.round(pos.coords.longitude * 10000) / 10000,
        ];
        const newOrig: SelectedPoint = {
          id: "GPS-LIVE",
          name: "My Live GPS Location",
          coordinates: coords,
          address: `Live Device Coordinates: ${coords[0]}, ${coords[1]}`,
          isCustom: true,
        };
        setOriginPoint(newOrig);
        setManualOrigLat(coords[0].toFixed(4));
        setManualOrigLng(coords[1].toFixed(4));
        showToast("🟢 Origin set to your current device location!");
        calculateRoutes(newOrig, destPoint, preference);
      },
      (err) => {
        console.warn("Geolocation permission error", err);
        // Fallback demo location near Bangalore Center
        const demoCoords: [number, number] = [12.9752, 77.6012];
        const newOrig: SelectedPoint = {
          id: "GPS-DEMO",
          name: "Live GPS (Simulated Fix: Brigade Road)",
          coordinates: demoCoords,
          address: "Brigade Road Commercial Hub, Central Zone",
          isCustom: true,
        };
        setOriginPoint(newOrig);
        setManualOrigLat(demoCoords[0].toFixed(4));
        setManualOrigLng(demoCoords[1].toFixed(4));
        showToast("📍 Using simulated live GPS location (Brigade Road)");
        calculateRoutes(newOrig, destPoint, preference);
      },
      { timeout: 7000 }
    );
  };

  // Manual Coordinates Apply
  const handleApplyManualCoords = (e: React.FormEvent) => {
    e.preventDefault();
    const oLat = parseFloat(manualOrigLat);
    const oLng = parseFloat(manualOrigLng);
    const dLat = parseFloat(manualDestLat);
    const dLng = parseFloat(manualDestLng);

    if (isNaN(oLat) || isNaN(oLng) || isNaN(dLat) || isNaN(dLng)) {
      showToast("Please enter valid decimal coordinates");
      return;
    }

    const newOrig: SelectedPoint = {
      id: "MANUAL-ORIG",
      name: `Point (${oLat.toFixed(4)}, ${oLng.toFixed(4)})`,
      coordinates: [oLat, oLng],
      address: `Custom Lat: ${oLat}, Lng: ${oLng}`,
      isCustom: true,
    };

    const newDest: SelectedPoint = {
      id: "MANUAL-DEST",
      name: `Point (${dLat.toFixed(4)}, ${dLng.toFixed(4)})`,
      coordinates: [dLat, dLng],
      address: `Custom Lat: ${dLat}, Lng: ${dLng}`,
      isCustom: true,
    };

    setOriginPoint(newOrig);
    setDestPoint(newDest);
    showToast("Applied custom GPS coordinates to route analysis");
    calculateRoutes(newOrig, newDest, preference);
  };

  const activePlan =
    selectedRouteId === recommendedRoute?.route_id
      ? recommendedRoute
      : alternateRoutes.find((a) => a.route_id === selectedRouteId) || recommendedRoute;

  // Build Leaflet Markers
  const mapMarkers: MapMarker[] = [];

  // 1. All Predefined Landmark Nodes (if toggled on)
  if (showAllNodes) {
    locations.forEach((loc) => {
      // Don't show generic node marker if it's the active origin or destination (they have special markers)
      const isOrigin =
        Math.abs(loc.coordinates[0] - originPoint.coordinates[0]) < 0.001 &&
        Math.abs(loc.coordinates[1] - originPoint.coordinates[1]) < 0.001;
      const isDest =
        Math.abs(loc.coordinates[0] - destPoint.coordinates[0]) < 0.001 &&
        Math.abs(loc.coordinates[1] - destPoint.coordinates[1]) < 0.001;

      if (!isOrigin && !isDest) {
        mapMarkers.push({
          id: loc.id,
          position: loc.coordinates,
          title: loc.name,
          type: "node",
          category: loc.category,
        });
      }
    });
  }

  // 2. Origin Marker (Green Pulse)
  mapMarkers.push({
    position: originPoint.coordinates,
    title: `Origin: ${originPoint.name}`,
    type: "origin",
    popupHtml: `
      <div style="padding: 4px; min-width: 190px;">
        <strong style="color: #10b981; font-size: 13px;">🟢 Origin Point</strong>
        <div style="font-weight: bold; font-size: 12px; margin-top: 3px; color: #f1f5f9;">${originPoint.name}</div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: 1px;">${originPoint.address || ""}</div>
        <div style="font-size: 10px; font-family: monospace; color: #64748b; margin-top: 4px;">
          ${originPoint.coordinates[0].toFixed(4)}, ${originPoint.coordinates[1].toFixed(4)}
        </div>
      </div>
    `,
  });

  // 3. Destination Marker (Red Pulse)
  mapMarkers.push({
    position: destPoint.coordinates,
    title: `Destination: ${destPoint.name}`,
    type: "destination",
    popupHtml: `
      <div style="padding: 4px; min-width: 190px;">
        <strong style="color: #ef4444; font-size: 13px;">🏁 Destination</strong>
        <div style="font-weight: bold; font-size: 12px; margin-top: 3px; color: #f1f5f9;">${destPoint.name}</div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: 1px;">${destPoint.address || ""}</div>
        <div style="font-size: 10px; font-family: monospace; color: #64748b; margin-top: 4px;">
          ${destPoint.coordinates[0].toFixed(4)}, ${destPoint.coordinates[1].toFixed(4)}
        </div>
      </div>
    `,
  });

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
              <span className="text-cyan-400 font-semibold">Milestone 2 & 3</span>
              <span>›</span>
              <span className="text-slate-200">Interactive Route Analysis</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1 flex items-center gap-2.5">
              <span>Intelligent Route Optimization & Dynamic Map Pinning</span>
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Interactive Pinning
              </span>
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => showToast("Route diversion advisory dispatched to regional digital variable message displays.")}
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
              title="Dynamic Route Parameters"
              subtitle="Pick on map, select nodes, or use live GPS"
              icon="🧭"
            >
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  calculateRoutes(originPoint, destPoint, preference);
                }}
                className="space-y-4 mt-2"
              >
                {/* Origin Selector */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span> Origin Point
                    </label>
                    <button
                      type="button"
                      onClick={() => setSelectionMode(selectionMode === "origin" ? "none" : "origin")}
                      className={`text-[11px] px-2 py-0.5 rounded-md font-bold transition flex items-center gap-1 border ${
                        selectionMode === "origin"
                          ? "bg-emerald-500 text-slate-950 border-emerald-400 shadow-lg shadow-emerald-500/30"
                          : "bg-slate-900 hover:bg-slate-800 text-emerald-400 border-emerald-500/30"
                      }`}
                    >
                      <span>📍</span>
                      <span>{selectionMode === "origin" ? "Click Map Now" : "Pick on Map"}</span>
                    </button>
                  </div>

                  <select
                    value={originPoint.isCustom ? "custom" : originPoint.id}
                    onChange={(e) => handleOriginDropdownChange(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none transition"
                  >
                    {originPoint.isCustom && (
                      <option value="custom">📍 {originPoint.name}</option>
                    )}
                    {locations.map((loc) => (
                      <option key={loc.id} value={loc.id} disabled={loc.id === destPoint.id && !destPoint.isCustom}>
                        {loc.name}
                      </option>
                    ))}
                  </select>

                  <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>GPS: {originPoint.coordinates[0].toFixed(4)}, {originPoint.coordinates[1].toFixed(4)}</span>
                    <button
                      type="button"
                      onClick={handleUseGeolocation}
                      className="text-cyan-400 hover:underline flex items-center gap-1 text-[10px]"
                      title="Set origin to your device's live GPS"
                    >
                      <span>📱</span> My Location
                    </button>
                  </div>
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
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <span className="h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse"></span> Destination Point
                    </label>
                    <button
                      type="button"
                      onClick={() => setSelectionMode(selectionMode === "destination" ? "none" : "destination")}
                      className={`text-[11px] px-2 py-0.5 rounded-md font-bold transition flex items-center gap-1 border ${
                        selectionMode === "destination"
                          ? "bg-rose-500 text-white border-rose-400 shadow-lg shadow-rose-500/30"
                          : "bg-slate-900 hover:bg-slate-800 text-rose-400 border-rose-500/30"
                      }`}
                    >
                      <span>🏁</span>
                      <span>{selectionMode === "destination" ? "Click Map Now" : "Pick on Map"}</span>
                    </button>
                  </div>

                  <select
                    value={destPoint.isCustom ? "custom" : destPoint.id}
                    onChange={(e) => handleDestDropdownChange(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none transition"
                  >
                    {destPoint.isCustom && (
                      <option value="custom">🏁 {destPoint.name}</option>
                    )}
                    {locations.map((loc) => (
                      <option key={loc.id} value={loc.id} disabled={loc.id === originPoint.id && !originPoint.isCustom}>
                        {loc.name}
                      </option>
                    ))}
                  </select>

                  <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>GPS: {destPoint.coordinates[0].toFixed(4)}, {destPoint.coordinates[1].toFixed(4)}</span>
                  </div>
                </div>

                {/* Advanced Coordinate Inputs Toggle */}
                <div className="pt-1 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowManualInputs(!showManualInputs)}
                    className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 font-semibold"
                  >
                    <span>{showManualInputs ? "▼" : "▶"}</span>
                    <span>Exact GPS Coordinates Editor</span>
                  </button>

                  {showManualInputs && (
                    <div className="mt-3 p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 space-y-2.5 animate-fadeIn">
                      <div className="text-[10px] text-slate-400">Origin Latitude / Longitude:</div>
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="number"
                          step="any"
                          value={manualOrigLat}
                          onChange={(e) => setManualOrigLat(e.target.value)}
                          placeholder="Lat"
                          className="rounded-lg border border-slate-800 bg-slate-900 px-2 py-1 text-xs text-white"
                        />
                        <input
                          type="number"
                          step="any"
                          value={manualOrigLng}
                          onChange={(e) => setManualOrigLng(e.target.value)}
                          placeholder="Lng"
                          className="rounded-lg border border-slate-800 bg-slate-900 px-2 py-1 text-xs text-white"
                        />
                      </div>

                      <div className="text-[10px] text-slate-400 pt-1">Destination Latitude / Longitude:</div>
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="number"
                          step="any"
                          value={manualDestLat}
                          onChange={(e) => setManualDestLat(e.target.value)}
                          placeholder="Lat"
                          className="rounded-lg border border-slate-800 bg-slate-900 px-2 py-1 text-xs text-white"
                        />
                        <input
                          type="number"
                          step="any"
                          value={manualDestLng}
                          onChange={(e) => setManualDestLng(e.target.value)}
                          placeholder="Lng"
                          className="rounded-lg border border-slate-800 bg-slate-900 px-2 py-1 text-xs text-white"
                        />
                      </div>

                      <button
                        type="button"
                        onClick={handleApplyManualCoords}
                        className="w-full mt-2 rounded-lg bg-slate-800 hover:bg-slate-700 py-1.5 text-[11px] font-bold text-cyan-300 transition"
                      >
                        Apply GPS Coordinates
                      </button>
                    </div>
                  )}
                </div>

                {/* Optimization Preference */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Optimization Objective
                  </label>
                  <div className="grid grid-cols-3 gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px]">
                    <button
                      type="button"
                      onClick={() => {
                        setPreference("fastest");
                        calculateRoutes(originPoint, destPoint, "fastest");
                      }}
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
                      onClick={() => {
                        setPreference("least_congested");
                        calculateRoutes(originPoint, destPoint, "least_congested");
                      }}
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
                      onClick={() => {
                        setPreference("eco");
                        calculateRoutes(originPoint, destPoint, "eco");
                      }}
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
                    <span>Recalculate Dynamic Route →</span>
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
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 shadow-2xl relative">
              {/* Top Interactive Map Control Strip */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80 mb-3">
                <div className="flex items-center gap-2">
                  <span className="flex h-2.5 w-2.5 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-200">
                    OPENSTREETMAP • DYNAMIC GEOSPATIAL VECTORING
                  </span>
                </div>

                {/* Map Quick Action Buttons */}
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setSelectionMode(selectionMode === "origin" ? "none" : "origin")}
                    className={`text-xs px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1.5 ${
                      selectionMode === "origin"
                        ? "bg-emerald-500 text-slate-950 border-emerald-400 font-bold shadow-md shadow-emerald-500/20 animate-pulse"
                        : "bg-slate-900 hover:bg-slate-800 text-emerald-400 border-slate-700"
                    }`}
                  >
                    <span>🟢</span>
                    <span>Pick Origin</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectionMode(selectionMode === "destination" ? "none" : "destination")}
                    className={`text-xs px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1.5 ${
                      selectionMode === "destination"
                        ? "bg-rose-500 text-white border-rose-400 font-bold shadow-md shadow-rose-500/20 animate-pulse"
                        : "bg-slate-900 hover:bg-slate-800 text-rose-400 border-slate-700"
                    }`}
                  >
                    <span>🏁</span>
                    <span>Pick Destination</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowAllNodes(!showAllNodes)}
                    className={`text-xs px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1.5 ${
                      showAllNodes
                        ? "bg-cyan-950/80 text-cyan-300 border-cyan-500/40"
                        : "bg-slate-900 text-slate-400 border-slate-800"
                    }`}
                    title="Toggle display of city landmark nodes"
                  >
                    <span>🗺️</span>
                    <span>Landmarks ({locations.length})</span>
                  </button>
                </div>
              </div>

              {/* Map Selection Mode Floating Banner */}
              {selectionMode !== "none" && (
                <div className="mb-3 p-2.5 rounded-xl border border-cyan-500/40 bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 flex items-center justify-between text-xs animate-fadeIn">
                  <div className="flex items-center gap-2">
                    <span className="text-base animate-bounce">
                      {selectionMode === "origin" ? "🟢" : "🏁"}
                    </span>
                    <span className="font-semibold text-cyan-200">
                      Click anywhere on the map or click a landmark to place your{" "}
                      <span className="underline decoration-cyan-400 font-bold">
                        {selectionMode === "origin" ? "Origin (Start)" : "Destination (End)"}
                      </span>
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectionMode("none")}
                    className="text-[11px] px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                  >
                    ✕ Cancel
                  </button>
                </div>
              )}

              {/* Dynamic Leaflet Map */}
              <LeafletMapWrapper
                center={originPoint.coordinates}
                zoom={12}
                markers={mapMarkers}
                routes={mapRoutes}
                selectedRouteId={selectedRouteId}
                onRouteClick={(id) => setSelectedRouteId(id)}
                onSelectPoint={handleSelectPoint}
                selectionMode={selectionMode}
                height="460px"
              />

              {/* Legend & Instructions */}
              <div className="mt-3 flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-5 rounded bg-cyan-500 inline-block"></span> Recommended Path
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-5 rounded bg-amber-500 border-dashed border border-amber-300 inline-block"></span> Alternate 1
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-5 rounded bg-purple-500 border-dashed border border-purple-300 inline-block"></span> Alternate 2
                  </span>
                </div>
                <div className="text-slate-500">
                  Tip: Click any point on the map to set Origin or Destination
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Multi-Route Side-by-Side Comparison Cards */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <span>📊</span> Dynamic Multi-Route Comparison
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

        {/* Road Conditions Breakdown Table */}
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
