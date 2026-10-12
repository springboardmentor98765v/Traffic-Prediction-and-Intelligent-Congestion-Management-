"use client";

import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Map,
  Route,
  ShieldAlert,
  Users,
  Gauge,
  Radio,
} from "lucide-react";

const modules = [
  {
    title: "Traffic Dashboard",
    description: "View traffic conditions and key monitoring metrics.",
    href: "/dashboard",
    icon: Gauge,
    label: "Monitoring",
  },
  {
    title: "Traffic Analytics",
    description: "Explore historical traffic trends, congestion and heatmaps.",
    href: "/analytics",
    icon: BarChart3,
    label: "Insights",
  },
  {
    title: "Live Traffic Map",
    description: "Open the map interface for road and traffic monitoring.",
    href: "/live-map",
    icon: Map,
    label: "Live view",
  },
  {
    title: "Incident Management",
    description: "Review the incident monitoring interface.",
    href: "/incidents",
    icon: ShieldAlert,
    label: "Incidents",
  },
  {
    title: "Route Analysis",
    description: "Explore route analysis and congestion-aware planning.",
    href: "/route-analysis",
    icon: Route,
    label: "Planning",
  },
  {
    title: "User Management",
    description: "Open the user administration interface.",
    href: "/users",
    icon: Users,
    label: "Administration",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10 bg-slate-950/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-5">
          <Link href="/" className="flex items-center gap-3">
            <div className="rounded-xl bg-cyan-400/15 p-2.5 text-cyan-300">
              <Activity size={25} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                TrafficVision <span className="text-cyan-300">AI</span>
              </h1>
              <p className="text-xs text-slate-400">
                Intelligent Traffic Management
              </p>
            </div>
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-white/15 px-4 py-2 text-sm font-medium transition hover:border-cyan-300 hover:text-cyan-300"
          >
            Sign in <ArrowRight className="ml-2 inline" size={15} />
          </Link>
        </div>
      </header>

      <section className="relative overflow-hidden border-b border-white/10">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(8,145,178,0.18),transparent_55%)]" />
        <div className="relative mx-auto grid max-w-7xl gap-10 px-6 py-20 md:grid-cols-[1.3fr_0.7fr] md:items-center md:py-28">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1.5 text-sm text-cyan-200">
              <Radio size={15} />
              Smart mobility intelligence platform
            </div>
            <h2 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-5xl md:text-6xl">
              Smarter roads.
              <span className="block text-cyan-300">
                Better journeys.
              </span>
            </h2>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
              Monitor traffic, explore congestion patterns and access
              intelligent traffic management tools from one central workspace.
            </p>
            <div className="mt-9 flex flex-wrap gap-4">
              <Link
                href="/dashboard"
                className="rounded-xl bg-cyan-400 px-6 py-3.5 font-semibold text-slate-950 transition hover:bg-cyan-300"
              >
                Open Dashboard <ArrowRight className="ml-2 inline" size={18} />
              </Link>
              <Link
                href="/analytics"
                className="rounded-xl border border-white/15 px-6 py-3.5 font-semibold transition hover:border-cyan-300 hover:text-cyan-300"
              >
                Explore Analytics
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-2xl shadow-cyan-950/20 sm:p-8">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Platform overview</p>
                <h3 className="mt-1 text-xl font-semibold">
                  Your traffic workspace
                </h3>
              </div>
              <div className="rounded-xl bg-cyan-300/10 p-3 text-cyan-300">
                <Activity size={24} />
              </div>
            </div>
            <div className="mt-7 space-y-4">
              {[
                ["Traffic monitoring", "dashboard"],
                ["Historical analytics", "analytics"],
                ["Road map interface", "live-map"],
              ].map(([label, key]) => (
                <div
                  key={key}
                  className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-4"
                >
                  <div className="h-2.5 w-2.5 rounded-full bg-cyan-300" />
                  <span className="flex-1 text-sm text-slate-200">{label}</span>
                  <span className="text-xs text-slate-500">Available page</span>
                </div>
              ))}
            </div>
            <p className="mt-5 text-xs leading-5 text-slate-500">
              This overview links to your existing frontend modules. Live
              status and data availability depend on each module's integration.
            </p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-16 sm:py-20">
        <div className="mb-9 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">
              Platform modules
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Everything in one place
            </h2>
            <p className="mt-3 max-w-2xl text-slate-400">
              Choose a module to explore the pages already available in your
              TrafficVision project.
            </p>
          </div>
          <span className="rounded-full border border-white/10 px-3 py-1.5 text-sm text-slate-400">
            6 modules
          </span>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link
                href={module.href}
                key={module.href}
                className="group rounded-2xl border border-white/10 bg-slate-900/60 p-6 transition duration-200 hover:-translate-y-1 hover:border-cyan-300/40 hover:bg-slate-900"
              >
                <div className="flex items-start justify-between">
                  <div className="rounded-xl bg-cyan-300/10 p-3 text-cyan-300 transition group-hover:bg-cyan-300/20">
                    <Icon size={24} />
                  </div>
                  <ArrowRight
                    size={19}
                    className="text-slate-600 transition group-hover:translate-x-1 group-hover:text-cyan-300"
                  />
                </div>
                <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-cyan-300">
                  {module.label}
                </p>
                <h3 className="mt-2 text-xl font-semibold">{module.title}</h3>
                <p className="mt-3 min-h-12 text-sm leading-6 text-slate-400">
                  {module.description}
                </p>
                <p className="mt-5 text-sm font-medium text-slate-300 group-hover:text-cyan-300">
                  Open module
                </p>
              </Link>
            );
          })}
        </div>
      </section>

      <footer className="border-t border-white/10">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-6 text-sm text-slate-500">
          <p>TrafficVision AI · Intelligent Congestion Management</p>
          <p>Traffic insights for smarter mobility</p>
        </div>
      </footer>
    </main>
  );
}
