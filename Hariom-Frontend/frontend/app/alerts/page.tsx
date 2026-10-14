"use client";

import React, { useState } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import { useTraffic } from "../lib/traffic-context";
import { useAuth } from "../lib/auth-context";

export default function AlertsPage() {
  const { role } = useAuth();
  const { alerts, acknowledgeAlert, resolveAlert, broadcastIncident, roads } = useTraffic();

  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [broadcastModalOpen, setBroadcastModalOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // New incident form
  const [targetRoadId, setTargetRoadId] = useState<string>(roads[0]?.road_id || "R001");
  const [incidentTitle, setIncidentTitle] = useState<string>("");
  const [incidentMessage, setIncidentMessage] = useState<string>("");
  const [incidentSeverity, setIncidentSeverity] = useState<"critical" | "warning" | "advisory">("critical");

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleAcknowledge = async (id: string) => {
    await acknowledgeAlert(id);
    showToast("Incident acknowledged by operator. Dispatch units alerted.");
  };

  const handleResolve = async (id: string) => {
    await resolveAlert(id);
    showToast("Incident marked resolved. Traffic flow normalized.");
  };

  const handleCreateBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!incidentTitle.trim() || !incidentMessage.trim()) return;

    await broadcastIncident(targetRoadId, incidentTitle, incidentMessage, incidentSeverity);
    setBroadcastModalOpen(false);
    setIncidentTitle("");
    setIncidentMessage("");
    showToast("Emergency incident broadcast published to all operators and digital signs.");
  };

  const filteredAlerts = alerts.filter((a) => {
    const matchesSev = severityFilter === "all" || a.severity === severityFilter;
    const matchesStat = statusFilter === "all" || a.status === statusFilter;
    return matchesSev && matchesStat;
  });

  const criticalCount = alerts.filter((a) => a.severity === "critical" && a.status !== "resolved").length;
  const warningCount = alerts.filter((a) => a.severity === "warning" && a.status !== "resolved").length;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Toast Notification */}
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
              <span className="text-cyan-400 font-semibold">Incident Management</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1 flex items-center gap-2.5">
              <span>Traffic & Congestion Alerts Center</span>
            </h1>
          </div>

          {(role === "operator" || role === "admin") && (
            <button
              onClick={() => setBroadcastModalOpen(true)}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-rose-600 to-amber-600 hover:brightness-110 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-rose-500/20 transition"
            >
              <span>📢</span>
              <span>Broadcast Incident Alert</span>
            </button>
          )}
        </div>

        {/* KPI Counter Banners */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 backdrop-blur-md">
            <div className="text-xs font-semibold text-rose-300">Critical Incidents</div>
            <div className="text-2xl font-black text-rose-400 mt-1">{criticalCount} Active</div>
            <div className="text-[11px] text-rose-300/70 mt-1">High queue spillback risk</div>
          </div>

          <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 backdrop-blur-md">
            <div className="text-xs font-semibold text-amber-300">Warning Alerts</div>
            <div className="text-2xl font-black text-amber-400 mt-1">{warningCount} Active</div>
            <div className="text-[11px] text-amber-300/70 mt-1">Approaching bottleneck capacity</div>
          </div>

          <div className="rounded-xl border border-cyan-500/30 bg-cyan-950/20 p-4 backdrop-blur-md">
            <div className="text-xs font-semibold text-cyan-300">Total Logged</div>
            <div className="text-2xl font-black text-cyan-400 mt-1">{alerts.length} Total</div>
            <div className="text-[11px] text-cyan-300/70 mt-1">Live telemetry incidents</div>
          </div>

          <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 backdrop-blur-md">
            <div className="text-xs font-semibold text-emerald-300">Resolved Today</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">
              {alerts.filter((a) => a.status === "resolved").length} Cleared
            </div>
            <div className="text-[11px] text-emerald-300/70 mt-1">Flow normalized</div>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-950/60 p-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Severity:</span>
            <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs">
              {["all", "critical", "warning", "advisory"].map((sev) => (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-3 py-1 rounded-md capitalize font-semibold transition ${
                    severityFilter === sev
                      ? "bg-cyan-600 text-white shadow"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Status:</span>
            <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs">
              {["all", "active", "acknowledged", "resolved"].map((stat) => (
                <button
                  key={stat}
                  onClick={() => setStatusFilter(stat)}
                  className={`px-3 py-1 rounded-md capitalize font-semibold transition ${
                    statusFilter === stat
                      ? "bg-slate-700 text-white shadow"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {stat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-3">
          {filteredAlerts.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-12 text-center text-slate-400">
              <span className="text-3xl">✨</span>
              <p className="mt-2 text-sm">No incidents match the active filter criteria.</p>
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`rounded-2xl border p-5 transition-all ${
                  alert.status === "resolved"
                    ? "border-slate-800/60 bg-slate-950/40 opacity-70"
                    : alert.severity === "critical"
                    ? "border-rose-500/40 bg-rose-950/15"
                    : alert.severity === "warning"
                    ? "border-amber-500/40 bg-amber-950/15"
                    : "border-slate-800 bg-slate-900/60"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="space-y-1.5 max-w-2xl">
                    <div className="flex items-center gap-2.5">
                      <Badge variant={alert.severity} pulse={alert.status === "active" && alert.severity === "critical"}>
                        {alert.severity}
                      </Badge>
                      <span className="text-xs font-mono font-bold text-slate-300">
                        {alert.road_name} ({alert.road_id})
                      </span>
                      <span className="text-slate-600">•</span>
                      <span className="text-xs text-slate-500">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${
                          alert.status === "active"
                            ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                            : alert.status === "acknowledged"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                            : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                        }`}
                      >
                        {alert.status}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-white tracking-wide">{alert.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">{alert.message}</p>

                    {alert.action_recommended && (
                      <div className="rounded-lg bg-slate-950/60 p-2 border border-slate-800 text-[11px] text-cyan-300 flex items-center gap-2 mt-2">
                        <span>💡</span>
                        <span>
                          <strong>Dispatch Recommendation:</strong> {alert.action_recommended}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Actions gated by RBAC */}
                  {(role === "operator" || role === "admin") && alert.status !== "resolved" && (
                    <div className="flex sm:flex-col gap-2 shrink-0">
                      {alert.status === "active" && (
                        <button
                          onClick={() => handleAcknowledge(alert.id)}
                          className="px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-xs font-bold text-white transition shadow"
                        >
                          ✔ Acknowledge
                        </button>
                      )}
                      <button
                        onClick={() => handleResolve(alert.id)}
                        className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white transition shadow"
                      >
                        🛠 Mark Resolved
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Broadcast Incident Modal */}
      {broadcastModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-lg rounded-2xl border border-rose-500/40 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>📢</span> Broadcast Emergency Incident
              </h3>
              <button
                onClick={() => setBroadcastModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateBroadcast} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target Arterial Corridor
                </label>
                <select
                  value={targetRoadId}
                  onChange={(e) => setTargetRoadId(e.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white"
                >
                  {roads.map((r) => (
                    <option key={r.road_id} value={r.road_id}>
                      {r.name} ({r.road_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Incident Severity
                </label>
                <select
                  value={incidentSeverity}
                  onChange={(e) => setIncidentSeverity(e.target.value as any)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white"
                >
                  <option value="critical">Critical (Immediate officer dispatch & diversion)</option>
                  <option value="warning">Warning (Congestion buildup warning)</option>
                  <option value="advisory">Advisory (Traffic advisory or planned work)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Incident Summary / Title
                </label>
                <input
                  type="text"
                  value={incidentTitle}
                  onChange={(e) => setIncidentTitle(e.target.value)}
                  placeholder="e.g. Collision blocking inbound lanes near Junction 3"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white placeholder-slate-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Detailed Advisory Message
                </label>
                <textarea
                  rows={3}
                  value={incidentMessage}
                  onChange={(e) => setIncidentMessage(e.target.value)}
                  placeholder="Describe queue length, expected clearing duration, and suggested detour..."
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white placeholder-slate-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setBroadcastModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-xs font-semibold text-slate-300 hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white shadow-lg shadow-rose-500/20 transition"
                >
                  Broadcast Alert Now
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
