"use client";

import React, { useState } from "react";
import { useTraffic } from "../lib/traffic-context";
import { AIRecommendation } from "../lib/api";
import Badge from "./Badge";

interface AIRecommendationsPanelProps {
  compact?: boolean;
  limit?: number;
}

export default function AIRecommendationsPanel({
  compact = false,
  limit,
}: AIRecommendationsPanelProps) {
  const { recommendations, applyRecommendation, dismissRecommendation } = useTraffic();
  const [statusFilter, setStatusFilter] = useState<"all" | "pending" | "applied" | "dismissed">("pending");
  const [activeSimulation, setActiveSimulation] = useState<AIRecommendation | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleApply = async (id: string, title: string) => {
    setActionLoadingId(id);
    try {
      await applyRecommendation(id);
      showToast(`Optimization Applied: "${title}". Signal timings and detour signs updated.`);
      if (activeSimulation?.id === id) {
        setActiveSimulation(null);
      }
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDismiss = async (id: string) => {
    setActionLoadingId(id);
    try {
      await dismissRecommendation(id);
      showToast("Recommendation dismissed from active queue.");
      if (activeSimulation?.id === id) {
        setActiveSimulation(null);
      }
    } finally {
      setActionLoadingId(null);
    }
  };

  const filtered = recommendations.filter((r) => {
    if (statusFilter === "all") return true;
    return r.status === statusFilter;
  });

  const displayList = limit ? filtered.slice(0, limit) : filtered;

  const pendingCount = recommendations.filter((r) => r.status === "pending").length;
  const appliedCount = recommendations.filter((r) => r.status === "applied").length;

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "signal_retiming":
        return "🚦";
      case "detour_routing":
        return "🧭";
      case "ramp_metering":
        return "🛑";
      case "green_wave":
        return "🌊";
      case "vms_advisory":
        return "📢";
      default:
        return "🤖";
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl space-y-4">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 rounded-xl border border-cyan-500/40 bg-slate-900/95 p-4 text-xs font-semibold text-cyan-300 shadow-2xl backdrop-blur-xl animate-fadeIn">
          ✓ {toastMessage}
        </div>
      )}

      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base">🤖</span>
            <h3 className="text-base font-bold text-white tracking-tight">
              AI Decision Support & Mitigation Recommendations
            </h3>
            {pendingCount > 0 && (
              <span className="rounded-full bg-cyan-500/15 border border-cyan-500/30 px-2 py-0.5 text-[10px] font-extrabold text-cyan-400">
                {pendingCount} actionable
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Machine learning heuristic engine dynamically suggesting signal phase offsets, variable detours, and ramp metering.
          </p>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-0.5 text-xs">
          <button
            onClick={() => setStatusFilter("pending")}
            className={`px-3 py-1 font-semibold rounded-lg transition ${
              statusFilter === "pending"
                ? "bg-cyan-600 text-white shadow"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Pending ({pendingCount})
          </button>
          <button
            onClick={() => setStatusFilter("applied")}
            className={`px-3 py-1 font-semibold rounded-lg transition ${
              statusFilter === "applied"
                ? "bg-emerald-600 text-white shadow"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Applied ({appliedCount})
          </button>
          <button
            onClick={() => setStatusFilter("all")}
            className={`px-3 py-1 font-semibold rounded-lg transition ${
              statusFilter === "all"
                ? "bg-slate-800 text-cyan-300 shadow"
                : "text-slate-400 hover:text-white"
            }`}
          >
            All ({recommendations.length})
          </button>
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      <div className={`grid gap-4 ${compact ? "grid-cols-1" : "grid-cols-1 lg:grid-cols-2"}`}>
        {displayList.length === 0 ? (
          <div className="col-span-full py-12 text-center rounded-xl border border-slate-800/80 bg-slate-950/40">
            <span className="text-3xl">✨</span>
            <div className="text-sm font-semibold text-slate-300 mt-2">
              No recommendations in "{statusFilter}" status
            </div>
            <p className="text-xs text-slate-500 mt-1">
              All monitored intersections are currently operating at optimal cycle offsets.
            </p>
          </div>
        ) : (
          displayList.map((rec) => {
            const isPending = rec.status === "pending";
            const isApplied = rec.status === "applied";
            const isLoadingThis = actionLoadingId === rec.id;

            return (
              <div
                key={rec.id}
                className={`relative flex flex-col justify-between rounded-xl border p-4.5 transition-all ${
                  isApplied
                    ? "bg-emerald-950/15 border-emerald-500/30"
                    : rec.priority === "critical"
                    ? "bg-rose-950/20 border-rose-500/40 shadow-lg shadow-rose-950/20"
                    : rec.priority === "high"
                    ? "bg-amber-950/20 border-amber-500/40 shadow-lg shadow-amber-950/20"
                    : "bg-slate-950/70 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div>
                  {/* Top Badges & Meta */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-sm">{getCategoryIcon(rec.category)}</span>
                      <span className="text-xs font-bold text-slate-200">{rec.target_corridor_name}</span>
                      <span className="text-[10px] text-slate-500 font-mono">({rec.target_corridor_id})</span>
                      <Badge variant={rec.priority}>{rec.priority}</Badge>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                        isApplied
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : rec.status === "dismissed"
                          ? "bg-slate-800 text-slate-400"
                          : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                      }`}
                    >
                      {rec.status}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <h4 className="text-sm font-bold text-white mt-2 leading-snug">
                    {rec.title}
                  </h4>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {rec.description}
                  </p>

                  {/* Action Plan Strip */}
                  <div className="mt-3 rounded-lg bg-slate-900/90 border border-slate-800 p-2.5 text-xs text-cyan-300">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Proposed Automated Execution:
                    </div>
                    <div className="mt-0.5 text-slate-200 font-medium">{rec.action_plan}</div>
                  </div>

                  {/* Projected Impact Metrics Row */}
                  <div className="grid grid-cols-4 gap-2 mt-3 pt-3 border-t border-slate-800/80 text-center">
                    <div className="rounded-lg bg-slate-900/60 p-1.5 border border-slate-800">
                      <div className="text-[9px] text-slate-400 uppercase">Delay Cut</div>
                      <div className="text-xs font-black text-emerald-400">
                        -{rec.impact_delay_reduction_pct}%
                      </div>
                    </div>
                    <div className="rounded-lg bg-slate-900/60 p-1.5 border border-slate-800">
                      <div className="text-[9px] text-slate-400 uppercase">Speed Gain</div>
                      <div className="text-xs font-black text-cyan-400">
                        +{rec.impact_speed_gain_kmh} <span className="text-[9px]">km/h</span>
                      </div>
                    </div>
                    <div className="rounded-lg bg-slate-900/60 p-1.5 border border-slate-800">
                      <div className="text-[9px] text-slate-400 uppercase">CO2 Offset</div>
                      <div className="text-xs font-black text-teal-400">
                        -{rec.impact_co2_offset_pct}%
                      </div>
                    </div>
                    <div className="rounded-lg bg-slate-900/60 p-1.5 border border-slate-800">
                      <div className="text-[9px] text-slate-400 uppercase">Confidence</div>
                      <div className="text-xs font-black text-indigo-300">
                        {(rec.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Action Buttons */}
                <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-slate-800/70">
                  <button
                    onClick={() => setActiveSimulation(rec)}
                    className="flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition"
                  >
                    <span>🔬</span>
                    <span>Simulate Impact</span>
                  </button>

                  <div className="flex items-center gap-2">
                    {isPending && (
                      <button
                        onClick={() => handleDismiss(rec.id)}
                        disabled={isLoadingThis}
                        className="rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 px-2.5 py-1.5 text-xs font-semibold transition"
                      >
                        Dismiss
                      </button>
                    )}

                    {isPending ? (
                      <button
                        onClick={() => handleApply(rec.id, rec.title)}
                        disabled={isLoadingThis}
                        className="flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:brightness-110 text-white px-3.5 py-1.5 text-xs font-bold shadow-md shadow-cyan-600/20 transition disabled:opacity-50"
                      >
                        {isLoadingThis && <span className="animate-spin text-xs">🔄</span>}
                        <span>⚡ Apply Optimization</span>
                      </button>
                    ) : isApplied ? (
                      <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
                        <span>✓ Active & Applied</span>
                      </span>
                    ) : null}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Before / After Simulation Modal */}
      {activeSimulation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-lg rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-start justify-between border-b border-slate-800 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">🔬</span>
                  <h3 className="text-base font-bold text-white">
                    Traffic Intervention Simulation
                  </h3>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Algorithmic Before vs After Outcome Comparison
                </p>
              </div>
              <button
                onClick={() => setActiveSimulation(null)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="rounded-xl bg-slate-950 p-3 border border-slate-800">
              <div className="text-xs font-bold text-cyan-300">{activeSimulation.title}</div>
              <div className="text-[11px] text-slate-400 mt-1">{activeSimulation.action_plan}</div>
            </div>

            {/* Before vs After Metric Comparison Bars */}
            <div className="space-y-3 text-xs">
              {/* Metric 1: Corridor Travel Delay */}
              <div>
                <div className="flex justify-between font-semibold text-slate-300 mb-1">
                  <span>Corridor Transit Delay (minutes)</span>
                  <span className="text-emerald-400 font-bold">
                    -{activeSimulation.impact_delay_reduction_pct}% Reduction
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-16 text-[10px] text-slate-400 font-mono">Baseline:</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-rose-500 h-full rounded-full"
                        style={{ width: "85%" }}
                      />
                    </div>
                    <span className="w-16 text-right font-mono text-rose-400 font-bold">
                      {activeSimulation.simulation.baseline_delay_min} min
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-16 text-[10px] text-cyan-400 font-mono">Simulated:</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all duration-700"
                        style={{ width: "45%" }}
                      />
                    </div>
                    <span className="w-16 text-right font-mono text-emerald-400 font-bold">
                      {activeSimulation.simulation.optimized_delay_min} min
                    </span>
                  </div>
                </div>
              </div>

              {/* Metric 2: Corridor Density */}
              <div>
                <div className="flex justify-between font-semibold text-slate-300 mb-1">
                  <span>Congestion Density (%)</span>
                  <span className="text-cyan-400 font-bold">
                    {activeSimulation.simulation.baseline_density_pct}% →{" "}
                    {activeSimulation.simulation.optimized_density_pct}%
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-16 text-[10px] text-slate-400 font-mono">Baseline:</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-amber-500 h-full rounded-full"
                        style={{ width: `${activeSimulation.simulation.baseline_density_pct}%` }}
                      />
                    </div>
                    <span className="w-16 text-right font-mono text-slate-200">
                      {activeSimulation.simulation.baseline_density_pct}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-16 text-[10px] text-cyan-400 font-mono">Simulated:</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-cyan-500 h-full rounded-full transition-all duration-700"
                        style={{ width: `${activeSimulation.simulation.optimized_density_pct}%` }}
                      />
                    </div>
                    <span className="w-16 text-right font-mono text-cyan-300 font-bold">
                      {activeSimulation.simulation.optimized_density_pct}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Metric 3: Queue Length Spillback */}
              <div>
                <div className="flex justify-between font-semibold text-slate-300 mb-1">
                  <span>Queue Spillback Physical Length</span>
                  <span className="text-indigo-300 font-bold">
                    -{Math.round(((activeSimulation.simulation.queue_length_meters_before - activeSimulation.simulation.queue_length_meters_after) / activeSimulation.simulation.queue_length_meters_before) * 100)}% Length
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-16 text-[10px] text-slate-400 font-mono">Baseline:</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div className="bg-slate-500 h-full rounded-full" style={{ width: "90%" }} />
                    </div>
                    <span className="w-16 text-right font-mono text-slate-300">
                      {activeSimulation.simulation.queue_length_meters_before}m
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-16 text-[10px] text-cyan-400 font-mono">Simulated:</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-indigo-500 h-full rounded-full transition-all duration-700"
                        style={{ width: "35%" }}
                      />
                    </div>
                    <span className="w-16 text-right font-mono text-indigo-300 font-bold">
                      {activeSimulation.simulation.queue_length_meters_after}m
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setActiveSimulation(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs font-semibold text-slate-300 hover:bg-slate-700 transition"
              >
                Close Simulation
              </button>

              {activeSimulation.status === "pending" && (
                <button
                  onClick={() => handleApply(activeSimulation.id, activeSimulation.title)}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:brightness-110 text-xs font-bold text-white shadow-lg shadow-cyan-600/20 transition"
                >
                  ⚡ Apply Optimization Now
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
