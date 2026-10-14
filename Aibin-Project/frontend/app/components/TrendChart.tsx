"use client";

import React, { useState, useEffect, useMemo } from "react";
import { api, HistoricalTimeSeriesPoint, TrafficRoad } from "../lib/api";
import { useTraffic } from "../lib/traffic-context";

interface TrendChartProps {
  initialTimeframe?: "24h" | "7d" | "30d";
}

const CORRIDOR_COLORS: Record<string, { stroke: string; fill: string; name: string }> = {
  R001: { stroke: "#f59e0b", fill: "rgba(245, 158, 11, 0.15)", name: "MG Road" },
  R002: { stroke: "#3b82f6", fill: "rgba(59, 130, 246, 0.15)", name: "Ring Road" },
  R003: { stroke: "#ef4444", fill: "rgba(239, 68, 68, 0.15)", name: "Station Road" },
  R004: { stroke: "#10b981", fill: "rgba(16, 185, 129, 0.15)", name: "Airport Road" },
  R005: { stroke: "#8b5cf6", fill: "rgba(139, 92, 246, 0.15)", name: "Civil Lines" },
};

export default function TrendChart({ initialTimeframe = "24h" }: TrendChartProps) {
  const { roads } = useTraffic();
  const [timeframe, setTimeframe] = useState<"24h" | "7d" | "30d">(initialTimeframe);
  const [chartMode, setChartMode] = useState<"network" | "corridors">("network");
  const [activeCorridors, setActiveCorridors] = useState<Record<string, boolean>>({
    R001: true,
    R002: true,
    R003: true,
    R004: true,
    R005: true,
  });

  const [data, setData] = useState<{
    points: HistoricalTimeSeriesPoint[];
    summary: { avgDensity: number; avgSpeed: number; peakDensity: number; peakHour: string; totalVolume: number };
  } | null>(null);

  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchTrends = () => {
    setIsLoading(true);
    setErrorMessage(null);
    api
      .getHistoricalAnalytics(timeframe)
      .then((res) => {
        setData(res);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load trend analytics", err);
        setErrorMessage("Failed to load trend analytics telemetry. Please retry.");
        setIsLoading(false);
      });
  };

  // Fetch trend data whenever timeframe changes
  useEffect(() => {
    fetchTrends();
  }, [timeframe]);

  const toggleCorridor = (id: string) => {
    setActiveCorridors((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  // SVG Geometry Calculation
  const width = 800;
  const height = 280;
  const padLeft = 45;
  const padRight = 20;
  const padTop = 25;
  const padBottom = 35;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const points = data?.points || [];

  const getX = (index: number) => {
    if (points.length <= 1) return padLeft;
    return padLeft + (index / (points.length - 1)) * chartW;
  };

  const getYDensity = (densityVal: number) => {
    const clamped = Math.max(0, Math.min(100, densityVal));
    return padTop + chartH - (clamped / 100) * chartH;
  };

  // Build SVG path strings
  const networkLine = useMemo(() => {
    if (points.length === 0) return "";
    return points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getYDensity(p.network_avg_density).toFixed(1)}`)
      .join(" ");
  }, [points]);

  const networkArea = useMemo(() => {
    if (points.length === 0) return "";
    const line = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getYDensity(p.network_avg_density).toFixed(1)}`)
      .join(" ");
    const bottom = padTop + chartH;
    return `${line} L ${getX(points.length - 1).toFixed(1)} ${bottom} L ${padLeft} ${bottom} Z`;
  }, [points]);

  // Corridor lines
  const corridorLines = useMemo(() => {
    if (points.length === 0 || chartMode !== "corridors") return [];
    return Object.keys(activeCorridors)
      .filter((id) => activeCorridors[id])
      .map((id) => {
        const path = points
          .map((p, i) => {
            const val = p.corridor_densities[id] || 0;
            return `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getYDensity(val).toFixed(1)}`;
          })
          .join(" ");
        return {
          id,
          path,
          color: CORRIDOR_COLORS[id]?.stroke || "#06b6d4",
          name: CORRIDOR_COLORS[id]?.name || id,
        };
      });
  }, [points, chartMode, activeCorridors]);

  const activePoint = hoverIndex !== null && points[hoverIndex] ? points[hoverIndex] : null;

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base">📈</span>
            <h3 className="text-base font-bold text-white tracking-tight">
              Traffic Density & Flow Velocity Trends
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            {timeframe === "24h"
              ? "Diurnal 24-hour cycle showing morning (08:00–10:00) and evening commute crests"
              : timeframe === "7d"
              ? "7-day continuous longitudinal trend comparing weekday vs weekend flow profiles"
              : "30-day aggregate historical velocity and capacity saturation index"}
          </p>
        </div>

        {/* View Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Chart Mode Toggle */}
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-0.5 text-xs">
            <button
              onClick={() => setChartMode("network")}
              className={`px-3 py-1 font-semibold rounded-lg transition ${
                chartMode === "network"
                  ? "bg-cyan-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Citywide Average
            </button>
            <button
              onClick={() => setChartMode("corridors")}
              className={`px-3 py-1 font-semibold rounded-lg transition ${
                chartMode === "corridors"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Corridor Comparison
            </button>
          </div>

          {/* Timeframe Selector */}
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-0.5 text-xs">
            {(["24h", "7d", "30d"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTimeframe(t)}
                className={`px-2.5 py-1 font-semibold rounded-lg transition uppercase ${
                  timeframe === t
                    ? "bg-slate-800 text-cyan-300"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Corridor Filter Toggles (when in corridor comparison mode) */}
      {chartMode === "corridors" && (
        <div className="flex flex-wrap items-center gap-2 pt-3 pb-1 border-b border-slate-800/60 text-xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Toggle Corridors:
          </span>
          {Object.keys(CORRIDOR_COLORS).map((id) => {
            const conf = CORRIDOR_COLORS[id];
            const isEnabled = activeCorridors[id];
            return (
              <button
                key={id}
                onClick={() => toggleCorridor(id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition ${
                  isEnabled
                    ? "bg-slate-800 border-slate-700 text-slate-200"
                    : "bg-slate-950 border-slate-900 text-slate-600 opacity-60"
                }`}
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: conf.stroke }}
                />
                <span>{conf.name}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* SVG Time Series Chart Container */}
      <div className="relative mt-4 w-full">
        {isLoading ? (
          <div className="h-64 flex items-center justify-center text-xs text-slate-400">
            <span className="animate-spin text-lg mr-2">🔄</span> Loading trend telemetry...
          </div>
        ) : errorMessage ? (
          <div className="h-64 flex flex-col items-center justify-center text-xs text-rose-400 gap-2">
            <span>⚠️ {errorMessage}</span>
            <button
              onClick={fetchTrends}
              className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition"
            >
              Retry Loading Trends
            </button>
          </div>
        ) : (
          <div className="relative w-full overflow-hidden">
            <svg
              viewBox={`0 0 ${width} ${height}`}
              className="w-full h-auto select-none"
              onMouseLeave={() => setHoverIndex(null)}
              onMouseMove={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left) * (width / rect.width);
                const relX = mouseX - padLeft;
                const ratio = Math.max(0, Math.min(1, relX / chartW));
                const idx = Math.round(ratio * (points.length - 1));
                setHoverIndex(idx);
              }}
            >
              <defs>
                {/* Cyan Gradient for Network Avg */}
                <linearGradient id="networkGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.45" />
                  <stop offset="70%" stopColor="#06b6d4" stopOpacity="0.05" />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
                </linearGradient>

                {/* Critical Zone Gradient */}
                <linearGradient id="criticalZone" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.08" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Critical Congestion Warning Zone Background (>65%) */}
              <rect
                x={padLeft}
                y={padTop}
                width={chartW}
                height={chartH * 0.35}
                fill="url(#criticalZone)"
              />

              {/* Dotted Warning Line at 65% Density */}
              <line
                x1={padLeft}
                y1={getYDensity(65)}
                x2={padLeft + chartW}
                y2={getYDensity(65)}
                stroke="#ef4444"
                strokeWidth="1"
                strokeDasharray="4 4"
                opacity="0.6"
              />
              <text
                x={padLeft + chartW - 5}
                y={getYDensity(65) - 4}
                textAnchor="end"
                className="text-[9px] fill-rose-400 font-mono font-semibold"
              >
                Critical Congestion Threshold (65%)
              </text>

              {/* Grid Lines & Y Axis Labels */}
              {[0, 25, 50, 75, 100].map((val) => {
                const y = getYDensity(val);
                return (
                  <g key={val}>
                    <line
                      x1={padLeft}
                      y1={y}
                      x2={padLeft + chartW}
                      y2={y}
                      stroke="#334155"
                      strokeWidth="1"
                      strokeDasharray="2 3"
                      opacity="0.4"
                    />
                    <text
                      x={padLeft - 8}
                      y={y + 3}
                      textAnchor="end"
                      className="text-[10px] fill-slate-500 font-mono"
                    >
                      {val}%
                    </text>
                  </g>
                );
              })}

              {/* X Axis Ticks */}
              {points.map((p, i) => {
                // Show every nth label to avoid crowding
                const step = timeframe === "24h" ? 2 : timeframe === "7d" ? 1 : 4;
                if (i % step !== 0 && i !== points.length - 1) return null;
                const x = getX(i);
                return (
                  <g key={i}>
                    <line
                      x1={x}
                      y1={padTop + chartH}
                      x2={x}
                      y2={padTop + chartH + 4}
                      stroke="#475569"
                      strokeWidth="1"
                    />
                    <text
                      x={x}
                      y={padTop + chartH + 16}
                      textAnchor="middle"
                      className="text-[10px] fill-slate-400 font-mono"
                    >
                      {p.label}
                    </text>
                  </g>
                );
              })}

              {/* Chart Mode: Network Average Mode */}
              {chartMode === "network" && (
                <>
                  <path d={networkArea} fill="url(#networkGradient)" />
                  <path
                    d={networkLine}
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </>
              )}

              {/* Chart Mode: Corridor Comparison Mode */}
              {chartMode === "corridors" &&
                corridorLines.map((line) => (
                  <path
                    key={line.id}
                    d={line.path}
                    fill="none"
                    stroke={line.color}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                ))}

              {/* Hover Guideline & Indicator */}
              {hoverIndex !== null && (
                <>
                  <line
                    x1={getX(hoverIndex)}
                    y1={padTop}
                    x2={getX(hoverIndex)}
                    y2={padTop + chartH}
                    stroke="#94a3b8"
                    strokeWidth="1.2"
                    strokeDasharray="3 3"
                  />

                  {chartMode === "network" && (
                    <circle
                      cx={getX(hoverIndex)}
                      cy={getYDensity(points[hoverIndex].network_avg_density)}
                      r="5"
                      fill="#06b6d4"
                      stroke="#ffffff"
                      strokeWidth="2"
                      className="transition-all"
                    />
                  )}

                  {chartMode === "corridors" &&
                    Object.keys(activeCorridors)
                      .filter((id) => activeCorridors[id])
                      .map((id) => {
                        const val = points[hoverIndex].corridor_densities[id] || 0;
                        return (
                          <circle
                            key={id}
                            cx={getX(hoverIndex)}
                            cy={getYDensity(val)}
                            r="4"
                            fill={CORRIDOR_COLORS[id]?.stroke || "#fff"}
                            stroke="#ffffff"
                            strokeWidth="1.5"
                          />
                        );
                      })}
                </>
              )}
            </svg>

            {/* Interactive Tooltip Card */}
            {activePoint && hoverIndex !== null && (
              <div
                className="pointer-events-none absolute -top-2 z-20 w-56 rounded-xl border border-slate-700 bg-slate-950/95 p-2.5 shadow-2xl backdrop-blur-xl transition-transform"
                style={{
                  left: `${Math.min(
                    70,
                    Math.max(10, ((getX(hoverIndex) - padLeft) / chartW) * 100)
                  )}%`,
                  transform: "translateX(-50%) translateY(-100%)",
                }}
              >
                <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-[11px]">
                  <span className="font-bold text-white font-mono">{activePoint.label}</span>
                  <span className="text-[10px] text-cyan-400 font-semibold">
                    Flow: {activePoint.network_avg_speed} km/h
                  </span>
                </div>

                {chartMode === "network" ? (
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Network Density:</span>
                      <span
                        className={`font-black ${
                          activePoint.network_avg_density > 65
                            ? "text-rose-400"
                            : activePoint.network_avg_density >= 35
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {activePoint.network_avg_density}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-slate-500">
                      <span>Condition:</span>
                      <span className="font-semibold text-slate-300">
                        {activePoint.network_avg_density > 65
                          ? "Gridlock Surge"
                          : activePoint.network_avg_density >= 35
                          ? "Moderate Influx"
                          : "Free Flow"}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="mt-1.5 space-y-1 max-h-32 overflow-y-auto divide-y divide-slate-850">
                    {Object.keys(activeCorridors)
                      .filter((id) => activeCorridors[id])
                      .map((id) => (
                        <div key={id} className="flex justify-between items-center text-[11px] pt-1">
                          <span className="flex items-center gap-1 text-slate-300">
                            <span
                              className="h-1.5 w-1.5 rounded-full"
                              style={{ backgroundColor: CORRIDOR_COLORS[id]?.stroke }}
                            />
                            <span>{CORRIDOR_COLORS[id]?.name}</span>
                          </span>
                          <span className="font-bold text-slate-200">
                            {activePoint.corridor_densities[id]}%
                          </span>
                        </div>
                      ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* KPI Summary Footer */}
      {data?.summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-800/80 text-xs">
          <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Average Density
            </div>
            <div className="text-xl font-black text-cyan-400 mt-0.5">
              {data.summary.avgDensity}%
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Mean Network Speed
            </div>
            <div className="text-xl font-black text-emerald-400 mt-0.5">
              {data.summary.avgSpeed} <span className="text-xs font-normal text-slate-400">km/h</span>
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Peak Crest Density
            </div>
            <div className="text-xl font-black text-rose-400 mt-0.5">
              {data.summary.peakDensity}%
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Peak Bottleneck Window
            </div>
            <div className="text-xl font-black text-indigo-400 mt-0.5">
              {data.summary.peakHour}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
