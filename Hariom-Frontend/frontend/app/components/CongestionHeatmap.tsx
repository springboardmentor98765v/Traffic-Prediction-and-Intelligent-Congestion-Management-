"use client";

import React, { useState, useEffect } from "react";
import { api, HeatmapCell, TrafficRoad } from "../lib/api";
import { useTraffic } from "../lib/traffic-context";

export default function CongestionHeatmap() {
  const { roads } = useTraffic();
  const [selectedCorridor, setSelectedCorridor] = useState<string>("all");
  const [cells, setCells] = useState<HeatmapCell[]>([]);
  const [hoveredCell, setHoveredCell] = useState<HeatmapCell | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  const fetchHeatmap = () => {
    setIsLoading(true);
    setErrorMessage(null);
    api
      .getCongestionHeatmap(selectedCorridor === "all" ? undefined : selectedCorridor)
      .then((data) => {
        setCells(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load congestion heatmap", err);
        setErrorMessage("Failed to load 7x24 heatmap matrix. Please retry.");
        setIsLoading(false);
      });
  };

  useEffect(() => {
    fetchHeatmap();
  }, [selectedCorridor]);

  // Find cell by day index & hour
  const getCell = (dayIdx: number, hr: number): HeatmapCell | undefined => {
    return cells.find((c) => c.day_index === dayIdx && c.hour === hr);
  };

  // Color generator based on density %
  const getCellColor = (density: number) => {
    if (density < 25) {
      return "bg-emerald-950/70 border-emerald-900/40 text-emerald-300 hover:bg-emerald-800/80";
    }
    if (density < 45) {
      return "bg-teal-900/60 border-teal-800/50 text-teal-200 hover:bg-teal-700/80";
    }
    if (density < 65) {
      return "bg-amber-950/70 border-amber-800/50 text-amber-200 hover:bg-amber-700/80";
    }
    if (density < 82) {
      return "bg-orange-950/80 border-orange-800/60 text-orange-200 hover:bg-orange-600/80";
    }
    return "bg-rose-950/90 border-rose-700/70 text-rose-200 hover:bg-rose-600/90 shadow-sm shadow-rose-900/40";
  };

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl">
      {/* Header & Corridor Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base">🔥</span>
            <h3 className="text-base font-bold text-white tracking-tight">
              7×24 Diurnal Congestion Heatmap Matrix
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluating historical density intensity across 168 time-slots to pinpoint recurrent bottleneck corridors.
          </p>
        </div>

        {/* Corridor Selector */}
        <div className="flex items-center gap-2">
          <label htmlFor="corridor-select" className="text-xs font-semibold text-slate-400">Corridor Scope:</label>
          <select
            id="corridor-select"
            value={selectedCorridor}
            onChange={(e) => setSelectedCorridor(e.target.value)}
            className="rounded-xl bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-200 focus:border-cyan-500 focus:outline-none transition shadow-sm"
          >
            <option value="all">Citywide Network (Combined)</option>
            {roads.map((road) => (
              <option key={road.road_id} value={road.road_id}>
                {road.name} ({road.road_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Heatmap Grid Visual */}
      <div className="mt-5 overflow-x-auto">
        {isLoading ? (
          <div className="h-60 flex items-center justify-center text-xs text-slate-400">
            <span className="animate-spin text-lg mr-2">🔄</span> Generating 168-cell matrix...
          </div>
        ) : errorMessage ? (
          <div className="h-60 flex flex-col items-center justify-center text-xs text-rose-400 gap-2">
            <span>⚠️ {errorMessage}</span>
            <button
              onClick={fetchHeatmap}
              className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition"
            >
              Retry Loading Heatmap
            </button>
          </div>
        ) : (
          <div className="min-w-[700px]">
            {/* Hour Markers (X-Axis) */}
            <div className="flex items-center text-[10px] text-slate-500 font-mono mb-2 pl-12">
              {hours.map((h) => (
                <div key={h} className="flex-1 text-center">
                  {h % 3 === 0 ? `${h < 10 ? "0" + h : h}h` : "·"}
                </div>
              ))}
            </div>

            {/* Matrix Rows (Days) */}
            <div className="space-y-1.5">
              {days.map((dayName, dayIdx) => (
                <div key={dayName} className="flex items-center gap-2">
                  {/* Day Label */}
                  <div className="w-10 text-[11px] font-bold text-slate-400 font-mono uppercase tracking-wider">
                    {dayName}
                  </div>

                  {/* 24 Hour Cells */}
                  <div className="flex-1 flex gap-1">
                    {hours.map((hr) => {
                      const cell = getCell(dayIdx, hr);
                      const density = cell?.density || 0;
                      const isHovered =
                        hoveredCell?.day_index === dayIdx && hoveredCell?.hour === hr;

                      return (
                        <div
                          key={hr}
                          onMouseEnter={() => cell && setHoveredCell(cell)}
                          onMouseLeave={() => setHoveredCell(null)}
                          className={`flex-1 h-8 rounded-md border flex items-center justify-center text-[10px] font-mono cursor-pointer transition-all ${getCellColor(
                            density
                          )} ${
                            isHovered
                              ? "scale-115 z-20 border-white ring-2 ring-cyan-400 font-black shadow-lg"
                              : ""
                          }`}
                          title={`${dayName} ${hr}:00 — Density: ${density}%`}
                        >
                          {density > 75 ? "!" : ""}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Interactive Hover Inspection Strip */}
      <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/80 p-3 min-h-[58px] flex items-center justify-between">
        {hoveredCell ? (
          <div className="flex flex-wrap items-center justify-between w-full gap-4 text-xs">
            <div className="flex items-center gap-3">
              <span className="rounded-lg bg-slate-900 border border-slate-700 px-2.5 py-1 font-bold text-white font-mono">
                {hoveredCell.day_name} • {hoveredCell.hour < 10 ? "0" + hoveredCell.hour : hoveredCell.hour}:00
              </span>
              <span className="text-slate-300">
                Density: <strong className={hoveredCell.density > 65 ? "text-rose-400" : hoveredCell.density >= 35 ? "text-amber-400" : "text-emerald-400"}>{hoveredCell.density}%</strong>
              </span>
              <span className="text-slate-300">
                Speed: <strong className="text-cyan-400 font-mono">{hoveredCell.speed} km/h</strong>
              </span>
              <span className="text-slate-300">
                Estimated Volume: <strong className="text-slate-200">{hoveredCell.volume_count} veh/min</strong>
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-400">Risk Profile:</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                  hoveredCell.incident_risk === "critical"
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                    : hoveredCell.incident_risk === "medium"
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                }`}
              >
                {hoveredCell.incident_risk} bottleneck risk
              </span>
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-400 flex items-center gap-2">
            <span>💡</span>
            <span>Hover over any hour cell to inspect precise speed, density, and bottleneck risk index for that temporal slot.</span>
          </div>
        )}
      </div>

      {/* Heatmap Color Scale Legend */}
      <div className="flex flex-wrap items-center justify-between gap-4 mt-4 pt-3 border-t border-slate-800/60 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300">Density Legend:</span>
          <div className="flex items-center gap-1.5 text-[11px]">
            <span className="h-3 w-4 rounded bg-emerald-950 border border-emerald-800 inline-block"></span>
            <span>Fluid (&lt;25%)</span>
            <span className="h-3 w-4 rounded bg-teal-900 border border-teal-700 inline-block ml-2"></span>
            <span>Moderate (25–45%)</span>
            <span className="h-3 w-4 rounded bg-amber-900 border border-amber-700 inline-block ml-2"></span>
            <span>Heavy (45–65%)</span>
            <span className="h-3 w-4 rounded bg-orange-900 border border-orange-700 inline-block ml-2"></span>
            <span>Severe (65–82%)</span>
            <span className="h-3 w-4 rounded bg-rose-900 border border-rose-700 inline-block ml-2"></span>
            <span>Critical Gridlock (&gt;82%)</span>
          </div>
        </div>

        <div className="text-[11px] text-slate-500 font-mono">
          Recurrent Peak Window: Mon–Fri 08:30 & 18:00
        </div>
      </div>
    </div>
  );
}
