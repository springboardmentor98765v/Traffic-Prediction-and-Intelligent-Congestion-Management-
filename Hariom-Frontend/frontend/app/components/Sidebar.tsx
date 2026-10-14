"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../lib/auth-context";
import { useTraffic } from "../lib/traffic-context";
import Badge from "./Badge";

export default function Sidebar() {
  const pathname = usePathname();
  const { role, user, setRoleOverride } = useAuth();
  const { metrics, autoRefresh, setAutoRefresh, refreshData, isLoading } = useTraffic();

  const menuItems = [
    { href: "/dashboard", label: "Dashboard", icon: "📊", desc: "Real-time KPIs & Telemetry" },
    { href: "/live-map", label: "Live Traffic Map", icon: "🗺️", desc: "Corridor Flow & Map Pins" },
    { href: "/route-analysis", label: "Route Analysis", icon: "🧭", desc: "Leaflet Map & AI Detours" },
    { href: "/predictions", label: "AI Predictions", icon: "🤖", desc: "Horizon Forecast & Sandbox" },
    { href: "/alerts", label: "Incident Alerts", icon: "⚠️", desc: "Congestion & Dispatch Feed" },
    { href: "/analytics", label: "Flow Analytics", icon: "📈", desc: "Rush Hour & AI Forecasting" },
  ];


  return (
    <aside className="w-64 shrink-0 hidden lg:flex flex-col justify-between border-r border-slate-800/80 bg-slate-950/60 p-4 min-h-[calc(100vh-61px)]">
      <div className="space-y-6">
        {/* User Role Card */}
        <div className="rounded-xl border border-slate-800/90 bg-slate-900/60 p-3.5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Active Role</span>
            <Badge variant={role} pulse>
              {role}
            </Badge>
          </div>
          <div className="mt-2 text-xs font-medium text-slate-200 truncate">
            {user?.email || "operator@trafficvision.ai"}
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            {role === "admin" && "Full administrative & override access"}
            {role === "operator" && "Dispatch & incident acknowledge privileges"}
            {role === "public" && "Commuter read-only view"}
          </div>
        </div>

        {/* Navigation Menu */}
        <div>
          <div className="px-2 pb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Navigation
          </div>
          <div className="space-y-1">
            {menuItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-start gap-3 rounded-xl px-3 py-2.5 transition-all ${
                    isActive
                      ? "bg-cyan-500/15 border border-cyan-500/30 text-white shadow-sm"
                      : "text-slate-300 hover:bg-slate-900 hover:text-white border border-transparent"
                  }`}
                >
                  <span className="text-lg mt-0.5">{item.icon}</span>
                  <div>
                    <div className="text-xs font-semibold">{item.label}</div>
                    <div className="text-[10px] text-slate-400">{item.desc}</div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Live Network Snapshot */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-3.5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-300">Network Telemetry</span>
            <span className="flex items-center gap-1 text-[10px] text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Polling
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="rounded-lg bg-slate-950/70 p-2 border border-slate-800">
              <div className="text-[10px] text-slate-400">Avg Density</div>
              <div className="text-sm font-bold text-cyan-400 mt-0.5">{metrics.average_density}%</div>
            </div>
            <div className="rounded-lg bg-slate-950/70 p-2 border border-slate-800">
              <div className="text-[10px] text-slate-400">Avg Speed</div>
              <div className="text-sm font-bold text-emerald-400 mt-0.5">{metrics.network_speed_avg} km/h</div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1 text-[11px] text-slate-400">
            <span>Congested Corridors:</span>
            <span className="font-semibold text-rose-400">{metrics.congested_roads} / {metrics.total_roads}</span>
          </div>
        </div>
      </div>

      {/* Auto-Refresh Toggle & Manual Sync */}
      <div className="pt-4 border-t border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs text-slate-400">Auto Poll (5s)</span>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full transition-colors ${
              autoRefresh ? "bg-cyan-600" : "bg-slate-700"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                autoRefresh ? "translate-x-4 mt-0.5" : "translate-x-0.5 mt-0.5"
              }`}
            />
          </button>
        </div>

        <button
          onClick={() => refreshData()}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 py-2 text-xs font-semibold text-slate-200 transition"
        >
          <span className={isLoading ? "animate-spin" : ""}>🔄</span>
          <span>{isLoading ? "Syncing..." : "Sync Telemetry"}</span>
        </button>
      </div>
    </aside>
  );
}
