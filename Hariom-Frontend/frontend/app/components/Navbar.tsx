"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../lib/auth-context";
import { useTraffic } from "../lib/traffic-context";
import Badge from "./Badge";
import NotificationBell from "./NotificationBell";

export default function Navbar() {
  const pathname = usePathname();
  const { user, role, setRoleOverride, logout, isSimulationMode, toggleSimulationMode, isAuthenticated } = useAuth();
  const { isLiveBackend, alerts } = useTraffic();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const activeAlertsCount = alerts.filter((a) => a.status === "active").length;

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: "📊" },
    { href: "/live-map", label: "Live Map", icon: "🗺️" },
    { href: "/route-analysis", label: "Route Analysis", icon: "🧭" },
    { href: "/predictions", label: "Predictions", icon: "🤖" },
    { href: "/alerts", label: "Alerts", icon: "⚠️", badge: activeAlertsCount > 0 ? activeAlertsCount : null },
    { href: "/analytics", label: "Analytics", icon: "📈" },
  ];


  return (
    <nav className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl transition-all">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-lg shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition">
              <span>🚦</span>
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base font-extrabold tracking-tight text-white group-hover:text-cyan-400 transition">
                  TrafficVision
                </span>
                <span className="rounded-md bg-cyan-500/10 px-1.5 py-0.2 text-[10px] font-bold text-cyan-400 border border-cyan-500/20 uppercase tracking-wider">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-slate-400 tracking-wide">Intelligent Congestion Management</p>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                    isActive
                      ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                  }`}
                >
                  <span>{link.icon}</span>
                  <span>{link.label}</span>
                  {link.badge && (
                    <span className="flex h-4 min-w-[16px] items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white shadow-sm">
                      {link.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Right Controls: Backend Toggle, Role Switcher, Profile */}
        <div className="flex items-center gap-3">
          {/* Dual Mock/Live Backend Pill */}
          <button
            onClick={toggleSimulationMode}
            title="Click to toggle between FastAPI Backend and Local Telemetry Simulation"
            className={`hidden sm:flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium border transition-all ${
              !isSimulationMode && isLiveBackend
                ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/40 hover:bg-emerald-500/25"
                : "bg-amber-500/15 text-amber-300 border-amber-500/40 hover:bg-amber-500/25"
            }`}
          >
            <span className="relative flex h-2 w-2">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  !isSimulationMode && isLiveBackend ? "bg-emerald-400" : "bg-amber-400"
                }`}
              ></span>
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  !isSimulationMode && isLiveBackend ? "bg-emerald-500" : "bg-amber-500"
                }`}
              ></span>
            </span>
            <span>{!isSimulationMode && isLiveBackend ? "Live API (8000)" : "Simulation Mode"}</span>
          </button>

          {/* Quick RBAC Role Pill Selector */}
          <div className="hidden lg:flex items-center bg-slate-900/90 border border-slate-800 rounded-lg p-0.5">
            <button
              onClick={() => setRoleOverride("admin")}
              className={`px-2 py-0.5 text-[11px] font-bold rounded-md transition ${
                role === "admin"
                  ? "bg-purple-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Admin
            </button>
            <button
              onClick={() => setRoleOverride("operator")}
              className={`px-2 py-0.5 text-[11px] font-bold rounded-md transition ${
                role === "operator"
                  ? "bg-cyan-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Operator
            </button>
            <button
              onClick={() => setRoleOverride("public")}
              className={`px-2 py-0.5 text-[11px] font-bold rounded-md transition ${
                role === "public"
                  ? "bg-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Commuter
            </button>
          </div>

          {/* Notification Bell / Alerts Drawer */}
          <NotificationBell />

          {/* Current User Pill / Logout */}
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex flex-col items-end text-right">
                <span className="text-xs font-semibold text-slate-200 leading-none">{user?.name || "Officer"}</span>
                <span className="text-[10px] text-slate-400 mt-0.5 uppercase tracking-wider">{role}</span>
              </div>
              <button
                onClick={logout}
                className="rounded-lg bg-slate-800/80 hover:bg-rose-500/20 hover:text-rose-300 hover:border-rose-500/40 border border-slate-700/60 px-2.5 py-1 text-xs font-medium text-slate-300 transition"
                title="Sign Out"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-cyan-500 transition shadow-sm"
              >
                Sign In
              </Link>
            </div>
          )}

          {/* Mobile hamburger button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 text-slate-300"
          >
            {mobileMenuOpen ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-800/90 bg-slate-950 px-4 py-3 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
            >
              <span className="flex items-center gap-2">
                <span>{link.icon}</span>
                <span>{link.label}</span>
              </span>
              {link.badge && (
                <span className="rounded-full bg-rose-500 px-2 py-0.5 text-xs font-bold text-white">
                  {link.badge}
                </span>
              )}
            </Link>
          ))}
          <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-400">Switch Role:</span>
            <div className="flex gap-1">
              <button
                onClick={() => setRoleOverride("admin")}
                className={`px-2 py-0.5 text-xs rounded ${role === "admin" ? "bg-purple-600 text-white" : "bg-slate-800 text-slate-300"}`}
              >
                Admin
              </button>
              <button
                onClick={() => setRoleOverride("operator")}
                className={`px-2 py-0.5 text-xs rounded ${role === "operator" ? "bg-cyan-600 text-white" : "bg-slate-800 text-slate-300"}`}
              >
                Operator
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
