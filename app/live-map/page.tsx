"use client";

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { api, TrafficRoad } from "../lib/api";

export default function LiveMapPage() {
  const [roads, setRoads] = useState<TrafficRoad[]>([]);
  const [selectedRoad, setSelectedRoad] = useState<TrafficRoad | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getLiveTraffic()
      .then((data) => {
        setRoads(data);
        if (data.length > 0) setSelectedRoad(data[0]);
      })
      .catch((err) => {
        console.error("Failed to load map data", err);
      })
      .finally(() => setLoading(false));
  }, []);

  const lowCount = roads.filter((r) => r.congestion_level === "Low").length;
  const medCount = roads.filter((r) => r.congestion_level === "Medium").length;
  const highCount = roads.filter((r) => r.congestion_level === "High").length;

  const getPinColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "bg-red-500 ring-red-300";
      case "medium":
        return "bg-amber-500 ring-amber-300";
      default:
        return "bg-emerald-500 ring-emerald-300";
    }
  };

  const coordinates: Record<string, { top: string; left: string }> = {
    R001: { top: "25%", left: "30%" },
    R002: { top: "35%", left: "65%" },
    R003: { top: "60%", left: "20%" },
    R004: { top: "75%", left: "70%" },
    R005: { top: "50%", left: "45%" },
  };

  return (
    <Layout>
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
          Live Traffic Map
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Geographic spatial visualization of monitored road corridors and live congestion bottlenecks
        </p>
      </div>

      {/* Traffic Summary Cards */}
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="rounded-xl bg-white p-5 shadow-sm border border-emerald-100">
          <h2 className="text-xs font-bold uppercase text-emerald-800 tracking-wider">
            Normal Flow (Low)
          </h2>
          <p className="mt-2 text-2xl font-black text-emerald-600">
            {lowCount} Corridors
          </p>
          <span className="text-xs text-gray-500">Density &lt; 20%</span>
        </div>

        <div className="rounded-xl bg-white p-5 shadow-sm border border-amber-100">
          <h2 className="text-xs font-bold uppercase text-amber-800 tracking-wider">
            Moderate Traffic (Medium)
          </h2>
          <p className="mt-2 text-2xl font-black text-amber-600">
            {medCount} Corridors
          </p>
          <span className="text-xs text-gray-500">Density 20% – 50%</span>
        </div>

        <div className="rounded-xl bg-white p-5 shadow-sm border border-red-100">
          <h2 className="text-xs font-bold uppercase text-red-800 tracking-wider">
            Heavy Congestion (High)
          </h2>
          <p className="mt-2 text-2xl font-black text-red-600">
            {highCount} Corridors
          </p>
          <span className="text-xs text-gray-500">Density &gt; 50%</span>
        </div>
      </div>

      {/* Interactive Map Visualizer */}
      <div className="mt-8 rounded-xl bg-white p-6 shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-100 gap-2">
          <div>
            <h2 className="text-lg font-bold text-gray-900">
              City Arterial Network Map
            </h2>
            <p className="text-xs text-gray-500">
              Click any pin or road card below to inspect corridor telemetry
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-50 text-blue-700 border border-blue-200">
            Interactive GIS Layer
          </span>
        </div>

        <div className="relative mt-5 h-96 rounded-xl bg-slate-900 overflow-hidden border border-slate-700 shadow-inner flex items-center justify-center">
          {/* Simulated Highway Grid Lines */}
          <svg className="absolute inset-0 w-full h-full stroke-slate-700/60" xmlns="http://www.w3.org/2000/svg">
            <line x1="30%" y1="25%" x2="45%" y2="50%" strokeWidth="4" />
            <line x1="45%" y1="50%" x2="65%" y2="35%" strokeWidth="4" />
            <line x1="45%" y1="50%" x2="20%" y2="60%" strokeWidth="4" />
            <line x1="45%" y1="50%" x2="70%" y2="75%" strokeWidth="4" />
            <circle cx="50%" cy="50%" r="140" fill="none" strokeDasharray="4" strokeWidth="1" stroke="rgb(71 85 105 / 0.5)" />
          </svg>

          {/* Road Corridor Nodes / Pins */}
          {roads.map((road) => {
            const coord = coordinates[road.road_id] || { top: "50%", left: "50%" };
            const isSelected = selectedRoad?.road_id === road.road_id;
            return (
              <button
                key={road.road_id}
                onClick={() => setSelectedRoad(road)}
                style={{ top: coord.top, left: coord.left }}
                className={`absolute -translate-x-1/2 -translate-y-1/2 group flex flex-col items-center focus:outline-none transition-transform ${
                  isSelected ? "scale-125 z-30" : "z-20 hover:scale-110"
                }`}
              >
                <div
                  className={`h-5 w-5 rounded-full ring-4 shadow-lg flex items-center justify-center transition ${getPinColor(
                    road.congestion_level
                  )}`}
                >
                  <div className="h-2 w-2 rounded-full bg-white"></div>
                </div>
                <span className="mt-1 px-1.5 py-0.5 rounded text-[10px] font-bold text-white bg-slate-800/90 border border-slate-600 whitespace-nowrap shadow">
                  {road.road_id}
                </span>
              </button>
            );
          })}

          {/* Active Corridor Popup Box */}
          {selectedRoad && (
            <div className="absolute bottom-4 left-4 z-40 rounded-xl bg-slate-800/95 p-4 text-white border border-slate-600 shadow-2xl backdrop-blur-md max-w-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-mono font-bold text-blue-400">{selectedRoad.road_id}</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-700 text-slate-200">
                  {selectedRoad.congestion_level}
                </span>
              </div>
              <h3 className="font-bold text-sm text-white mt-1">{selectedRoad.name}</h3>
              <div className="mt-2 text-xs text-slate-300 space-y-1">
                <div>Density: <span className="font-mono font-bold text-white">{selectedRoad.density}%</span></div>
                <div>Volume: <span className="font-mono font-bold text-white">{selectedRoad.vehicle_count} veh/hr</span></div>
              </div>
            </div>
          )}
        </div>

        {/* Corridor Quick-Selector Cards */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-5 gap-3">
          {roads.map((road) => (
            <div
              key={road.road_id}
              onClick={() => setSelectedRoad(road)}
              className={`cursor-pointer rounded-lg p-3 border text-xs transition ${
                selectedRoad?.road_id === road.road_id
                  ? "border-blue-500 bg-blue-50 shadow-sm"
                  : "border-gray-200 hover:border-blue-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold">{road.road_id}</span>
                <span className="font-bold">{road.density}%</span>
              </div>
              <p className="font-semibold text-gray-800 mt-1 truncate">{road.name}</p>
              <div className="mt-2">
                <span
                  className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    road.congestion_level === "High"
                      ? "bg-red-100 text-red-800"
                      : road.congestion_level === "Medium"
                      ? "bg-amber-100 text-amber-800"
                      : "bg-emerald-100 text-emerald-800"
                  }`}
                >
                  {road.congestion_level}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}