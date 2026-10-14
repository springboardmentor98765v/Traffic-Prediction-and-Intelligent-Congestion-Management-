"use client";

import React, { useState } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import RoadDetailModal from "../components/RoadDetailModal";
import { useTraffic } from "../lib/traffic-context";
import { TrafficRoad } from "../lib/api";

export default function LiveMapPage() {
  const { roads, metrics } = useTraffic();
  const [selectedRoad, setSelectedRoad] = useState<TrafficRoad | null>(roads[0] || null);
  const [modalRoad, setModalRoad] = useState<TrafficRoad | null>(null);
  const [filterLevel, setFilterLevel] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [animationSpeed, setAnimationSpeed] = useState<boolean>(true);

  // Filtered roads
  const filteredRoads = roads.filter((r) => {
    const matchesFilter =
      filterLevel === "all" || r.congestion_level.toLowerCase() === filterLevel.toLowerCase();
    const matchesSearch =
      r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.road_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getCorridorColor = (road: TrafficRoad) => {
    if (road.density > 50) return "#f43f5e"; // Rose
    if (road.density >= 20) return "#f59e0b"; // Amber
    return "#10b981"; // Emerald
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>TrafficVision AI</span>
              <span>›</span>
              <span className="text-cyan-400 font-semibold">Live Traffic Map</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1">
              Interactive Arterial Network Map
            </h1>
          </div>

          {/* Quick Filters */}
          <div className="flex items-center gap-2">
            <div className="flex bg-slate-900 rounded-xl p-1 border border-slate-800 text-xs">
              {["all", "high", "medium", "low"].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setFilterLevel(lvl)}
                  className={`px-3 py-1.5 rounded-lg capitalize font-semibold transition ${
                    filterLevel === lvl
                      ? "bg-cyan-600 text-white shadow-md"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>

            <button
              onClick={() => setAnimationSpeed(!animationSpeed)}
              className={`hidden sm:flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition ${
                animationSpeed
                  ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/30"
                  : "bg-slate-900 text-slate-400 border-slate-800"
              }`}
            >
              <span>{animationSpeed ? "⚡ Particle Flow: ON" : "⏸️ Particles: PAUSED"}</span>
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="w-full">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter map nodes by road name or ID (e.g. Airport Road, MG Road)..."
            className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        {/* Interactive Map Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* SVG Map Canvas (2 cols) */}
          <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-950/90 p-4 relative overflow-hidden shadow-2xl flex flex-col justify-between min-h-[460px]">
            {/* Top Bar inside Map */}
            <div className="relative z-10 flex items-center justify-between pb-3 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span className="text-xs font-mono text-slate-300">
                  METRO NETWORK TELEMETRY • LIVE CARRIER DENSITY
                </span>
              </div>
              <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                5 ARTERIAL ARCS
              </span>
            </div>

            {/* Interactive Vector Topology */}
            <div className="relative w-full h-[360px] my-auto">
              <svg
                viewBox="0 0 700 400"
                className="w-full h-full select-none"
                preserveAspectRatio="xMidYMid meet"
              >
                <defs>
                  {/* Grid background pattern */}
                  <pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(30, 41, 59, 0.4)" strokeWidth="0.8" />
                  </pattern>

                  {/* Neon Glow Filters */}
                  <filter id="glow-rose" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                  <filter id="glow-amber" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                  <filter id="glow-emerald" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>

                {/* Cyber Grid Background */}
                <rect width="700" height="400" fill="url(#grid-pattern)" />

                {/* Outer Ring Beltway (R002: Ring Road) */}
                <path
                  d="M 100 200 C 100 80, 600 80, 600 200 C 600 320, 100 320, 100 200 Z"
                  fill="none"
                  stroke={roads[1] ? getCorridorColor(roads[1]) : "#f59e0b"}
                  strokeWidth="8"
                  strokeOpacity="0.4"
                  className="cursor-pointer hover:stroke-opacity-90 transition"
                  onClick={() => setSelectedRoad(roads[1] || null)}
                />
                {animationSpeed && (
                  <path
                    d="M 100 200 C 100 80, 600 80, 600 200 C 600 320, 100 320, 100 200 Z"
                    fill="none"
                    stroke="#ffffff"
                    strokeWidth="2"
                    strokeOpacity="0.8"
                    className="flow-dash pointer-events-none"
                  />
                )}

                {/* Central Corridor (R001: MG Road) */}
                <line
                  x1="180"
                  y1="200"
                  x2="520"
                  y2="200"
                  stroke={roads[0] ? getCorridorColor(roads[0]) : "#f43f5e"}
                  strokeWidth="10"
                  strokeLinecap="round"
                  className="cursor-pointer hover:brightness-125 transition"
                  onClick={() => setSelectedRoad(roads[0] || null)}
                />
                {animationSpeed && (
                  <line
                    x1="180"
                    y1="200"
                    x2="520"
                    y2="200"
                    stroke="#ffffff"
                    strokeWidth="2.5"
                    className="flow-dash-fast pointer-events-none"
                  />
                )}

                {/* North Express Corridor (R004: Airport Road) */}
                <path
                  d="M 350 200 L 350 60 L 520 60"
                  fill="none"
                  stroke={roads[3] ? getCorridorColor(roads[3]) : "#10b981"}
                  strokeWidth="8"
                  strokeLinecap="round"
                  className="cursor-pointer hover:brightness-125 transition"
                  onClick={() => setSelectedRoad(roads[3] || null)}
                />
                {animationSpeed && (
                  <path
                    d="M 350 200 L 350 60 L 520 60"
                    fill="none"
                    stroke="#ffffff"
                    strokeWidth="2"
                    className="flow-dash pointer-events-none"
                  />
                )}

                {/* Transit Junction Corridor (R003: Station Road) */}
                <path
                  d="M 180 200 L 250 110 L 350 200"
                  fill="none"
                  stroke={roads[2] ? getCorridorColor(roads[2]) : "#f43f5e"}
                  strokeWidth="9"
                  strokeLinecap="round"
                  className="cursor-pointer hover:brightness-125 transition"
                  onClick={() => setSelectedRoad(roads[2] || null)}
                />

                {/* Southwest Heritage Sector (R005: Civil Lines) */}
                <path
                  d="M 350 200 L 350 330 L 460 330"
                  fill="none"
                  stroke={roads[4] ? getCorridorColor(roads[4]) : "#10b981"}
                  strokeWidth="7"
                  strokeLinecap="round"
                  className="cursor-pointer hover:brightness-125 transition"
                  onClick={() => setSelectedRoad(roads[4] || null)}
                />

                {/* Interactive Map Nodes / Pins */}
                {roads.map((road, i) => {
                  const nodeCoords: Record<string, [number, number]> = {
                    R001: [350, 200], // Central Junction
                    R002: [580, 150], // Outer Belt
                    R003: [240, 140], // Station Junction
                    R004: [460, 60],  // Airport North
                    R005: [410, 330], // Civil Lines South
                  };
                  const [cx, cy] = nodeCoords[road.road_id] || [300 + i * 50, 200];
                  const isSelected = selectedRoad?.road_id === road.road_id;
                  const color = getCorridorColor(road);

                  return (
                    <g
                      key={road.road_id}
                      className="cursor-pointer group"
                      onClick={() => setSelectedRoad(road)}
                    >
                      {/* Pulse Circle */}
                      <circle
                        cx={cx}
                        cy={cy}
                        r={isSelected ? 18 : 14}
                        fill={color}
                        fillOpacity="0.25"
                        className="animate-ping"
                      />
                      {/* Outer Ring */}
                      <circle
                        cx={cx}
                        cy={cy}
                        r={isSelected ? 14 : 10}
                        fill="#090d16"
                        stroke={color}
                        strokeWidth="3"
                      />
                      {/* Inner Dot */}
                      <circle
                        cx={cx}
                        cy={cy}
                        r={isSelected ? 6 : 4}
                        fill={color}
                      />

                      {/* Road Name Label */}
                      <rect
                        x={cx - 45}
                        y={cy - 30}
                        width="90"
                        height="18"
                        rx="4"
                        fill="#0f172a"
                        stroke={isSelected ? "#06b6d4" : "#334155"}
                        strokeWidth="1"
                      />
                      <text
                        x={cx}
                        y={cy - 17}
                        textAnchor="middle"
                        fill="#f1f5f9"
                        fontSize="9"
                        fontWeight="bold"
                        fontFamily="sans-serif"
                      >
                        {road.name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Bottom Map Legend */}
            <div className="relative z-10 flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-slate-800/80 text-xs text-slate-400">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-500"></span>
                  <span>Low (&lt;20%)</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-amber-400 shadow-sm shadow-amber-500"></span>
                  <span>Medium (20-50%)</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500"></span>
                  <span>High (&gt;50%)</span>
                </span>
              </div>
              <span className="text-[11px] text-slate-500">
                Click pins or road arcs to inspect telemetry
              </span>
            </div>
          </div>

          {/* Selected Corridor Telemetry & AI Prediction Panel (1 col) */}
          <div className="space-y-4">
            {selectedRoad ? (
              <Card
                title={selectedRoad.name}
                subtitle={`ID: ${selectedRoad.road_id} • Arterial Node`}
                icon="📍"
                badge={
                  <Badge variant={selectedRoad.congestion_level} pulse>
                    {selectedRoad.congestion_level}
                  </Badge>
                }
              >
                <div className="space-y-4 mt-2">
                  <div className="grid grid-cols-2 gap-2 text-center">
                    <div className="rounded-xl bg-slate-950 p-3 border border-slate-800">
                      <div className="text-[10px] text-slate-400 uppercase">Current Density</div>
                      <div className="text-xl font-extrabold text-cyan-400 mt-1">
                        {selectedRoad.density}%
                      </div>
                    </div>
                    <div className="rounded-xl bg-slate-950 p-3 border border-slate-800">
                      <div className="text-[10px] text-slate-400 uppercase">Velocity</div>
                      <div className="text-xl font-extrabold text-emerald-400 mt-1">
                        {selectedRoad.speed} km/h
                      </div>
                    </div>
                  </div>

                  <div className="rounded-xl bg-slate-950 p-3 border border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-slate-400">Flow Volume:</span>
                    <span className="font-mono font-bold text-slate-200">
                      {selectedRoad.vehicle_count} vehicles/min
                    </span>
                  </div>

                  {/* AI Prediction Snippet */}
                  <div className="rounded-xl border border-indigo-500/30 bg-indigo-950/20 p-3.5 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-indigo-300 font-bold text-xs">
                        <span>🤖</span> AI Congestion Forecast
                      </div>
                      <span className="text-[10px] bg-indigo-500/30 text-indigo-200 px-2 py-0.5 rounded font-mono">
                        86% Conf.
                      </span>
                    </div>
                    <p className="text-xs text-slate-300">
                      {selectedRoad.density > 50
                        ? "Peak queueing risk active. Recommend diverting transit volume toward Ring Road."
                        : "Corridor throughput stable. No impending queue accumulation detected."}
                    </p>
                  </div>

                  <button
                    onClick={() => setModalRoad(selectedRoad)}
                    className="w-full rounded-xl bg-cyan-600 hover:bg-cyan-500 py-2.5 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 transition flex items-center justify-center gap-2"
                  >
                    <span>📊</span>
                    <span>View 24h Telemetry Profile & Recommendations</span>
                  </button>
                </div>
              </Card>
            ) : (
              <Card title="Corridor Inspector" icon="📍">
                <div className="py-12 text-center text-slate-500 text-xs">
                  Click any road corridor on the map to view instant telemetry.
                </div>
              </Card>
            )}

            {/* Quick Road List Selector */}
            <Card title="All Monitored Arcs" icon="🛣️">
              <div className="space-y-2">
                {filteredRoads.map((road) => (
                  <div
                    key={road.road_id}
                    onClick={() => setSelectedRoad(road)}
                    className={`flex items-center justify-between p-2.5 rounded-xl border transition cursor-pointer ${
                      selectedRoad?.road_id === road.road_id
                        ? "bg-cyan-500/15 border-cyan-500/40 text-white"
                        : "bg-slate-950/60 border-slate-800/80 text-slate-300 hover:bg-slate-900"
                    }`}
                  >
                    <div>
                      <div className="text-xs font-semibold">{road.name}</div>
                      <div className="text-[10px] text-slate-500 font-mono">{road.road_id}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold">{road.speed} km/h</span>
                      <Badge variant={road.congestion_level}>{road.congestion_level}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Deep-dive Modal */}
      <RoadDetailModal road={modalRoad} onClose={() => setModalRoad(null)} />
    </Layout>
  );
}
