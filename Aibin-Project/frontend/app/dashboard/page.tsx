"use client";

import React, { useState } from "react";
import Link from "next/link";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import RoadDetailModal from "../components/RoadDetailModal";
import AIRecommendationsPanel from "../components/AIRecommendationsPanel";
import ReportExportModal from "../components/ReportExportModal";
import { useTraffic } from "../lib/traffic-context";
import { useAuth } from "../lib/auth-context";
import { TrafficRoad } from "../lib/api";

export default function DashboardPage() {
  const { role } = useAuth();
  const { roads, metrics, alerts, isLiveBackend, lastUpdated, refreshData, isLoading } = useTraffic();

  const [selectedRoad, setSelectedRoad] = useState<TrafficRoad | null>(null);
  const [filterLevel, setFilterLevel] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [overrideModalOpen, setOverrideModalOpen] = useState<boolean>(false);
  const [overrideSuccess, setOverrideSuccess] = useState<string | null>(null);
  const [exportModalOpen, setExportModalOpen] = useState<boolean>(false);

  // Filtered roads list
  const filteredRoads = roads.filter((r) => {
    const matchesFilter =
      filterLevel === "all" || r.congestion_level.toLowerCase() === filterLevel.toLowerCase();
    const matchesSearch =
      r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.road_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const handleSignalOverride = (e: React.FormEvent) => {
    e.preventDefault();
    setOverrideSuccess("Emergency green light extension applied across selected corridor (+30s).");
    setTimeout(() => {
      setOverrideSuccess(null);
      setOverrideModalOpen(false);
    }, 2000);
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Top Header & Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>TrafficVision AI</span>
              <span>›</span>
              <span className="text-cyan-400 font-semibold">Situational Dashboard</span>
              <span>›</span>
              <Badge variant={role}>{role} view</Badge>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1 flex items-center gap-2.5">
              <span>Real-Time Traffic Command Center</span>
            </h1>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="hidden sm:flex flex-col items-end text-right">
              <span className="text-[11px] text-slate-400">Last Telemetry Poll</span>
              <span className="text-xs font-mono text-slate-200">
                {lastUpdated.toLocaleTimeString()}
              </span>
            </div>

            <button
              onClick={() => refreshData()}
              disabled={isLoading}
              className="flex items-center gap-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 px-3.5 py-2 text-xs font-semibold text-slate-200 transition shadow-sm"
            >
              <span className={isLoading ? "animate-spin" : ""}>🔄</span>
              <span>{isLoading ? "Refreshing..." : "Refresh"}</span>
            </button>

            <button
              onClick={() => setExportModalOpen(true)}
              className="flex items-center gap-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 px-3.5 py-2 text-xs font-semibold text-cyan-300 transition shadow-sm"
              title="Download historical report in CSV, JSON, or Executive PDF format"
            >
              <span>📥</span>
              <span className="hidden sm:inline">Export Report</span>
            </button>

            {role === "admin" && (
              <button
                onClick={() => setOverrideModalOpen(true)}
                className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:brightness-110 px-3.5 py-2 text-xs font-bold text-white shadow-lg shadow-purple-500/20 transition"
              >
                <span>⚡</span>
                <span>Signal Override</span>
              </button>
            )}
          </div>
        </div>

        {/* 4 Core KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: City Congestion Index */}
          <Card
            title="City Congestion Index"
            icon="🏙️"
            badge={
              <Badge variant={metrics.average_density > 50 ? "high" : metrics.average_density >= 25 ? "medium" : "low"}>
                {metrics.average_density > 50 ? "Heavy" : metrics.average_density >= 25 ? "Moderate" : "Fluid"}
              </Badge>
            }
          >
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black tracking-tight text-white">
                {metrics.average_density}%
              </span>
              <span className="text-xs font-semibold text-rose-400 flex items-center">
                ↑ +3.8% <span className="text-slate-500 ml-1 font-normal">vs 1h</span>
              </span>
            </div>
            <div className="mt-3 w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, metrics.average_density)}%` }}
              />
            </div>
          </Card>

          {/* Card 2: Monitored Corridors */}
          <Card
            title="Monitored Corridors"
            icon="🛣️"
            badge={
              <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                100% Online
              </span>
            }
          >
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black tracking-tight text-cyan-400">
                {metrics.total_roads}
              </span>
              <span className="text-xs text-slate-400">Active Arterial Segments</span>
            </div>
            <div className="mt-3 text-xs text-slate-400 flex items-center justify-between">
              <span>Sensor Health: 99.4%</span>
              <span className="text-cyan-300 font-mono">5/5 live feeds</span>
            </div>
          </Card>

          {/* Card 3: Network Flow Velocity */}
          <Card
            title="Network Flow Speed"
            icon="⚡"
            badge={
              <span className="text-[11px] font-semibold text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Normal Flow
              </span>
            }
          >
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black tracking-tight text-emerald-400">
                {metrics.network_speed_avg}
              </span>
              <span className="text-xs font-semibold text-slate-400">km/h avg</span>
            </div>
            <div className="mt-3 text-xs text-slate-400 flex items-center justify-between">
              <span>Target: &gt; 35 km/h</span>
              <span className="text-emerald-300">Optimal Baseline</span>
            </div>
          </Card>

          {/* Card 4: Active Bottlenecks */}
          <Card
            title="Active Bottlenecks"
            icon="⚠️"
            badge={
              <Badge variant={metrics.congested_roads > 0 ? "high" : "low"} pulse={metrics.congested_roads > 0}>
                {metrics.congested_roads} Congested
              </Badge>
            }
          >
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black tracking-tight text-rose-400">
                {metrics.congested_roads}
              </span>
              <span className="text-xs text-slate-400">of {metrics.total_roads} corridors</span>
            </div>
            <div className="mt-3 text-xs text-slate-400 flex items-center justify-between">
              <span>Urgent Alerts: {alerts.filter((a) => a.status === "active").length}</span>
              <Link href="/alerts" className="text-cyan-400 hover:underline font-semibold">
                View Alerts →
              </Link>
            </div>
          </Card>
        </div>

        {/* RBAC Admin / Operator Special Command Banners */}
        {role === "admin" && (
          <div className="rounded-2xl border border-purple-500/30 bg-purple-950/20 p-4 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-600/30 border border-purple-500/40 text-xl">
                🛡️
              </div>
              <div>
                <h4 className="text-sm font-bold text-purple-200">
                  Administrator Privileges Active
                </h4>
                <p className="text-xs text-purple-300/80">
                  You have full traffic signal override, system diagnostic, and AI model parameter adjustment rights.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setOverrideModalOpen(true)}
                className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-xs font-semibold text-white shadow transition"
              >
                Trigger Signal Override
              </button>
              <Link
                href="/alerts"
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition"
              >
                Broadcast Advisory
              </Link>
            </div>
          </div>
        )}

        {role === "operator" && (
          <div className="rounded-2xl border border-cyan-500/30 bg-cyan-950/20 p-4 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-600/30 border border-cyan-500/40 text-xl">
                🚦
              </div>
              <div>
                <h4 className="text-sm font-bold text-cyan-200">
                  Traffic Dispatcher Console (Operator Role)
                </h4>
                <p className="text-xs text-cyan-300/80">
                  Ready to acknowledge alerts, dispatch field units, and post detour advisories.
                </p>
              </div>
            </div>
            <Link
              href="/alerts"
              className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 transition text-center"
            >
              Open Incident Dispatch Queue ({alerts.filter((a) => a.status === "active").length})
            </Link>
          </div>
        )}

        {/* Main Monitored Corridors Table & Mini Map Radar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Table Section (2 Columns on Large) */}
          <div className="lg:col-span-2 space-y-4">
            <Card
              title="Live Arterial Corridors"
              subtitle="Real-time vehicle density, speed, and AI heuristic predictions"
              icon="📊"
              headerAction={
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 hidden sm:inline">Filter:</span>
                  <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs">
                    {["all", "high", "medium", "low"].map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => setFilterLevel(lvl)}
                        className={`px-2 py-1 rounded-md capitalize font-medium transition ${
                          filterLevel === lvl
                            ? "bg-cyan-600 text-white shadow"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                </div>
              }
            >
              {/* Search Bar */}
              <div className="mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search corridor by name or ID (e.g. MG Road, R001)..."
                  className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-4 py-2 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                />
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800/80 text-slate-400 uppercase tracking-wider">
                      <th className="pb-3 font-semibold">Corridor</th>
                      <th className="pb-3 font-semibold">Density</th>
                      <th className="pb-3 font-semibold">Speed</th>
                      <th className="pb-3 font-semibold">Vehicles</th>
                      <th className="pb-3 font-semibold">Status</th>
                      <th className="pb-3 font-semibold text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850">
                    {filteredRoads.map((road) => (
                      <tr
                        key={road.road_id}
                        onClick={() => setSelectedRoad(road)}
                        className="group hover:bg-slate-800/40 cursor-pointer transition"
                      >
                        <td className="py-3.5">
                          <div className="font-semibold text-slate-100 group-hover:text-cyan-400 transition">
                            {road.name}
                          </div>
                          <div className="text-[10px] font-mono text-slate-500">
                            {road.road_id} • Updated {new Date(road.updated_at).toLocaleTimeString()}
                          </div>
                        </td>
                        <td className="py-3.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-200">{road.density}%</span>
                            <div className="w-14 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  road.density > 50
                                    ? "bg-rose-500"
                                    : road.density >= 20
                                    ? "bg-amber-500"
                                    : "bg-emerald-500"
                                }`}
                                style={{ width: `${Math.min(100, road.density)}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 font-mono text-slate-300">
                          {road.speed} km/h
                        </td>
                        <td className="py-3.5 text-slate-400 font-mono">
                          {road.vehicle_count} v/m
                        </td>
                        <td className="py-3.5">
                          <Badge variant={road.congestion_level} pulse={road.congestion_level === "High"}>
                            {road.congestion_level}
                          </Badge>
                        </td>
                        <td className="py-3.5 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedRoad(road);
                            }}
                            className="rounded-lg bg-slate-800 hover:bg-cyan-600 hover:text-white px-2.5 py-1 text-[11px] font-semibold text-slate-300 transition border border-slate-700/60"
                          >
                            Inspect AI →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Mini Live Map Radar & Quick Incidents */}
          <div className="space-y-4">
            <Card
              title="City Topology Radar"
              subtitle="Live spatial overview"
              icon="🗺️"
              headerAction={
                <Link
                  href="/live-map"
                  className="text-xs font-semibold text-cyan-400 hover:underline"
                >
                  Full Map →
                </Link>
              }
            >
              <div className="relative h-48 w-full rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden">
                {/* Simulated Radar Circles */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-40 w-40 rounded-full border border-cyan-500/10" />
                  <div className="h-28 w-28 rounded-full border border-cyan-500/20" />
                  <div className="h-16 w-16 rounded-full border border-cyan-500/30" />
                  <div className="h-1 w-full border-t border-cyan-500/15" />
                  <div className="w-1 h-full border-l border-cyan-500/15" />
                </div>

                {/* Radar sweep */}
                <div className="absolute inset-0 origin-center animate-radar bg-gradient-to-tr from-cyan-500/10 via-transparent to-transparent pointer-events-none" />

                {/* Active Corridors on Mini Map */}
                <div className="relative z-10 w-full h-full p-4 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] font-mono text-cyan-400 bg-slate-900/90 px-2 py-0.5 rounded border border-slate-800">
                      GRID: NORTH METRO
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-emerald-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                      Active
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    {roads.slice(0, 3).map((r) => (
                      <div
                        key={r.road_id}
                        onClick={() => setSelectedRoad(r)}
                        className="flex items-center justify-between rounded-lg bg-slate-900/80 p-1.5 border border-slate-800 text-[11px] cursor-pointer hover:border-cyan-500/50 transition"
                      >
                        <span className="font-semibold text-slate-200">{r.name}</span>
                        <Badge variant={r.congestion_level}>{r.speed} km/h</Badge>
                      </div>
                    ))}
                  </div>

                  <div className="text-center">
                    <Link
                      href="/live-map"
                      className="inline-block text-[11px] font-bold text-cyan-400 hover:text-cyan-300"
                    >
                      Open Full Interactive Live Map →
                    </Link>
                  </div>
                </div>
              </div>
            </Card>

            {/* Recent Critical Incidents */}
            <Card
              title="Recent Incident Feed"
              subtitle="Prioritized alerts queue"
              icon="⚠️"
              headerAction={
                <Link href="/alerts" className="text-xs font-semibold text-cyan-400 hover:underline">
                  All ({alerts.length})
                </Link>
              }
            >
              <div className="space-y-2.5">
                {alerts.slice(0, 3).map((alert) => (
                  <div
                    key={alert.id}
                    className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 hover:border-slate-700 transition"
                  >
                    <div className="flex items-center justify-between">
                      <Badge variant={alert.severity} pulse={alert.severity === "critical"}>
                        {alert.severity}
                      </Badge>
                      <span className="text-[10px] text-slate-500">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-200 mt-1.5">{alert.title}</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">
                      {alert.message}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* AI Decision Support & Mitigation Recommendations */}
        <AIRecommendationsPanel />
      </div>

      {/* Historical Report Export Dialog */}
      <ReportExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
      />

      {/* Road Detail Telemetry Modal */}
      <RoadDetailModal
        road={selectedRoad}
        onClose={() => setSelectedRoad(null)}
      />

      {/* Admin Signal Override Modal */}
      {overrideModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-md rounded-2xl border border-purple-500/40 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>⚡</span> Emergency Signal Override
              </h3>
              <button
                onClick={() => setOverrideModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {overrideSuccess ? (
              <div className="py-8 text-center text-emerald-400 font-semibold text-sm">
                ✓ {overrideSuccess}
              </div>
            ) : (
              <form onSubmit={handleSignalOverride} className="mt-4 space-y-4">
                <p className="text-xs text-slate-300">
                  Select corridor to initiate dynamic signal priority extension and relieve bottleneck queueing.
                </p>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Target Corridor</label>
                  <select className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white">
                    {roads.map((r) => (
                      <option key={r.road_id} value={r.road_id}>
                        {r.name} ({r.congestion_level} - {r.density}%)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Override Action</label>
                  <select className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white">
                    <option value="extend-green">Extend Green Phase (+30 seconds)</option>
                    <option value="flashing-amber">Activate Flashing Amber Caution</option>
                    <option value="hold-ingress">Hold Ramp Ingress Red</option>
                  </select>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setOverrideModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-xs font-semibold text-slate-300 hover:bg-slate-700 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-bold text-white shadow-lg shadow-purple-500/20 transition"
                  >
                    Execute Override
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </Layout>
  );
}
