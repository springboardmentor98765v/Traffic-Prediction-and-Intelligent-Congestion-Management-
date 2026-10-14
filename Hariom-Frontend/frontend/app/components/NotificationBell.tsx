"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useTraffic } from "../lib/traffic-context";
import { TrafficAlert } from "../lib/api";
import Badge from "./Badge";

export default function NotificationBell() {
  const { alerts, acknowledgeAlert, resolveAlert } = useTraffic();
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"all" | "critical" | "warning" | "advisory">("all");
  const [processingId, setProcessingId] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // Active / unresolved alerts
  const activeAlerts = alerts.filter((a) => a.status !== "resolved");
  const criticalCount = activeAlerts.filter((a) => a.severity === "critical").length;
  const warningCount = activeAlerts.filter((a) => a.severity === "warning").length;
  const advisoryCount = activeAlerts.filter((a) => a.severity === "advisory").length;

  const filteredAlerts = (activeTab === "all"
    ? activeAlerts
    : activeAlerts.filter((a) => a.severity === activeTab)
  ).slice(0, 8); // show latest 8 in drop

  // Close when clicking outside or pressing Escape
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  const handleAcknowledge = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setProcessingId(id);
    try {
      await acknowledgeAlert(id);
    } finally {
      setProcessingId(null);
    }
  };

  const handleResolve = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setProcessingId(id);
    try {
      await resolveAlert(id);
    } finally {
      setProcessingId(null);
    }
  };

  const handleResolveAll = async () => {
    for (const a of activeAlerts) {
      await resolveAlert(a.id);
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const diffMs = Date.now() - new Date(timestamp).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ago`;
  };

  return (
    <div className="relative inline-block" ref={panelRef}>
      {/* Bell Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open Alerts & Notifications"
        aria-expanded={isOpen}
        className={`relative flex h-9 w-9 items-center justify-center rounded-xl border transition-all ${
          isOpen
            ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300 shadow-lg shadow-cyan-500/20"
            : criticalCount > 0
            ? "bg-rose-500/15 border-rose-500/40 text-rose-300 hover:bg-rose-500/25"
            : activeAlerts.length > 0
            ? "bg-amber-500/15 border-amber-500/40 text-amber-300 hover:bg-amber-500/25"
            : "bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 hover:text-white"
        }`}
        title={`${activeAlerts.length} Active Incident Alerts`}
      >
        <span className="text-base">🔔</span>

        {/* Unread Count Badge */}
        {activeAlerts.length > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 min-w-[20px] items-center justify-center">
            {criticalCount > 0 && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            )}
            <span
              className={`relative inline-flex h-5 min-w-[20px] items-center justify-center rounded-full px-1 text-[10px] font-black text-white shadow-md ${
                criticalCount > 0 ? "bg-rose-600" : "bg-amber-600"
              }`}
            >
              {activeAlerts.length}
            </span>
          </span>
        )}
      </button>

      {/* Flyout Alerts Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-slate-700/80 bg-slate-950/95 shadow-2xl backdrop-blur-2xl z-50 overflow-hidden animate-fadeIn">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-3 bg-slate-900/60">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white">Live Incident Alerts</span>
              {activeAlerts.length > 0 && (
                <span className="rounded-full bg-rose-500/20 px-2 py-0.5 text-[10px] font-extrabold text-rose-400 border border-rose-500/30">
                  {activeAlerts.length} active
                </span>
              )}
            </div>

            {activeAlerts.length > 0 && (
              <button
                onClick={handleResolveAll}
                className="text-[11px] font-medium text-slate-400 hover:text-cyan-400 transition"
                title="Mark all as resolved"
              >
                Resolve All
              </button>
            )}
          </div>

          {/* Severity Tabs */}
          <div className="flex items-center border-b border-slate-800/70 bg-slate-950 px-3 py-1.5 gap-1 text-[11px]">
            <button
              onClick={() => setActiveTab("all")}
              className={`px-2.5 py-1 rounded-lg font-semibold transition ${
                activeTab === "all"
                  ? "bg-slate-800 text-cyan-300"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              All ({activeAlerts.length})
            </button>
            <button
              onClick={() => setActiveTab("critical")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-semibold transition ${
                activeTab === "critical"
                  ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                  : "text-slate-400 hover:text-rose-400"
              }`}
            >
              <span>Critical</span>
              <span className="rounded-full bg-rose-500/30 px-1 text-[10px]">{criticalCount}</span>
            </button>
            <button
              onClick={() => setActiveTab("warning")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-semibold transition ${
                activeTab === "warning"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                  : "text-slate-400 hover:text-amber-400"
              }`}
            >
              <span>Warning</span>
              <span className="rounded-full bg-amber-500/30 px-1 text-[10px]">{warningCount}</span>
            </button>
            <button
              onClick={() => setActiveTab("advisory")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-semibold transition ${
                activeTab === "advisory"
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                  : "text-slate-400 hover:text-cyan-400"
              }`}
            >
              <span>Advisory</span>
              <span className="rounded-full bg-cyan-500/30 px-1 text-[10px]">{advisoryCount}</span>
            </button>
          </div>

          {/* Alert List */}
          <div className="max-h-80 overflow-y-auto divide-y divide-slate-850 p-2 space-y-1">
            {filteredAlerts.length === 0 ? (
              <div className="py-8 text-center">
                <div className="text-2xl">✨</div>
                <div className="text-xs font-semibold text-slate-300 mt-1">No Active {activeTab !== "all" ? activeTab : ""} Alerts</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Corridors operating within normal parameters</div>
              </div>
            ) : (
              filteredAlerts.map((alert: TrafficAlert) => {
                const isCritical = alert.severity === "critical";
                const isWarning = alert.severity === "warning";
                const isProcessing = processingId === alert.id;

                return (
                  <div
                    key={alert.id}
                    className={`p-2.5 rounded-xl transition border ${
                      isCritical
                        ? "bg-rose-950/20 border-rose-500/30 hover:bg-rose-950/30"
                        : isWarning
                        ? "bg-amber-950/20 border-amber-500/30 hover:bg-amber-950/30"
                        : "bg-slate-900/40 border-slate-800 hover:bg-slate-900/80"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`flex h-2 w-2 rounded-full ${
                            isCritical ? "bg-rose-400 animate-ping" : isWarning ? "bg-amber-400" : "bg-cyan-400"
                          }`}
                        />
                        <span className="text-xs font-bold text-white tracking-tight">{alert.road_name}</span>
                        <Badge variant={alert.severity}>{alert.severity}</Badge>
                      </div>
                      <span className="text-[10px] font-mono text-slate-500">
                        {formatTimeAgo(alert.timestamp)}
                      </span>
                    </div>

                    <p className="text-xs font-semibold text-slate-200 mt-1.5 leading-snug">
                      {alert.title}
                    </p>
                    <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">
                      {alert.message}
                    </p>

                    {alert.action_recommended && (
                      <div className="mt-2 rounded-lg bg-slate-950/80 p-1.5 border border-slate-800 text-[10px] text-cyan-300 flex items-start gap-1">
                        <span className="text-cyan-400">🤖</span>
                        <span className="leading-tight">{alert.action_recommended}</span>
                      </div>
                    )}

                    {/* Quick Card Actions */}
                    <div className="mt-2.5 flex items-center justify-between border-t border-slate-800/60 pt-2">
                      <span className="text-[10px] text-slate-500 uppercase font-mono">
                        {alert.status}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {alert.status === "active" && (
                          <button
                            onClick={(e) => handleAcknowledge(e, alert.id)}
                            disabled={isProcessing}
                            className="rounded-md bg-slate-800 hover:bg-slate-700 px-2 py-0.5 text-[10px] font-semibold text-slate-200 transition border border-slate-700"
                          >
                            Ack
                          </button>
                        )}
                        <button
                          onClick={(e) => handleResolve(e, alert.id)}
                          disabled={isProcessing}
                          className="rounded-md bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-semibold transition"
                        >
                          Resolve
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-slate-800/80 bg-slate-900/60 px-4 py-2.5 text-center">
            <Link
              href="/alerts"
              onClick={() => setIsOpen(false)}
              className="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition flex items-center justify-center gap-1.5"
            >
              <span>View Full Incident Center</span>
              <span>→</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
