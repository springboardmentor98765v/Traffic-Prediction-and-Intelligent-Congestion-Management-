"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "./lib/auth-context";

export default function HomePage() {
  const { isAuthenticated, role, loginAsDemo } = useAuth();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#090d16] text-white flex flex-col justify-between selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Banner */}
      <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-xl shadow-lg shadow-cyan-500/20">
            🚦
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              TrafficVision <span className="text-cyan-400 font-extrabold text-sm px-1.5 py-0.2 rounded bg-cyan-500/10 border border-cyan-500/30">AI</span>
            </h1>
            <p className="text-xs text-slate-400">Intelligent Congestion Management & Prediction</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition"
          >
            Sign In
          </Link>
          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-cyan-400 to-teal-400 hover:brightness-110 transition shadow-lg shadow-cyan-500/20"
          >
            Launch Command Center →
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-6 py-16 text-center flex flex-col items-center justify-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-6">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
          </span>
          Milestone 1 — Real-Time Traffic & AI Congestion Engine Active
        </div>

        <h2 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-3xl leading-tight">
          Next-Generation <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400">Smart Traffic Intelligence</span>
        </h2>

        <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-2xl leading-relaxed">
          Monitor arterial corridors in real time, forecast bottleneck surges with AI heuristic predictions, dispatch incident advisories, and streamline urban mobility.
        </p>

        {/* Quick Launch Action Buttons */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="px-6 py-3.5 rounded-xl text-sm font-bold text-slate-950 bg-gradient-to-r from-cyan-400 to-teal-400 hover:brightness-110 transition shadow-xl shadow-cyan-500/25 flex items-center gap-2"
          >
            <span>📊</span> Enter Live Dashboard
          </Link>
          <Link
            href="/live-map"
            className="px-6 py-3.5 rounded-xl text-sm font-semibold text-white bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 transition flex items-center gap-2"
          >
            <span>🗺️</span> View Interactive Live Map
          </Link>
        </div>

        {/* Instant Evaluation Demo Profiles */}
        <div className="mt-14 w-full max-w-2xl rounded-2xl border border-slate-800/90 bg-slate-900/40 p-6 backdrop-blur-md">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
            ⚡ Quick 1-Click Evaluation Profiles (No login credentials needed)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              onClick={async () => {
                await loginAsDemo("admin");
                router.push("/dashboard");
              }}
              className="group flex flex-col items-center justify-center p-3.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 transition text-center"
            >
              <span className="text-xl mb-1 group-hover:scale-110 transition">🛡️</span>
              <span className="text-xs font-bold text-purple-300">Demo Admin</span>
              <span className="text-[10px] text-slate-400 mt-0.5">Signal override & user admin</span>
            </button>

            <button
              onClick={async () => {
                await loginAsDemo("operator");
                router.push("/dashboard");
              }}
              className="group flex flex-col items-center justify-center p-3.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 transition text-center"
            >
              <span className="text-xl mb-1 group-hover:scale-110 transition">🚦</span>
              <span className="text-xs font-bold text-cyan-300">Demo Operator</span>
              <span className="text-[10px] text-slate-400 mt-0.5">Dispatch & alert resolution</span>
            </button>

            <button
              onClick={async () => {
                await loginAsDemo("public");
                router.push("/dashboard");
              }}
              className="group flex flex-col items-center justify-center p-3.5 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 transition text-center"
            >
              <span className="text-xl mb-1 group-hover:scale-110 transition">🚗</span>
              <span className="text-xs font-bold text-blue-300">Demo Commuter</span>
              <span className="text-[10px] text-slate-400 mt-0.5">Public road flow views</span>
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 px-6 py-4 text-center text-xs text-slate-500">
        TrafficVision AI — Smart Traffic Prediction & Intelligent Congestion Management • Milestone 1 Architecture
      </footer>
    </div>
  );
}
