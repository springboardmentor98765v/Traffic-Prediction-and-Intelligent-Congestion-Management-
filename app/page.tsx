
"use client";

import { useState } from "react";
import NotificationBell from "./components/NotificationBell";

const trafficData = [
  {
    road: "Park Street",
    area: "Central Kolkata",
    status: "Heavy",
    vehicles: 1240,
    delay: "18 min",
  },
  {
    road: "EM Bypass",
    area: "East Kolkata",
    status: "Moderate",
    vehicles: 860,
    delay: "9 min",
  },
  {
    road: "VIP Road",
    area: "Airport Zone",
    status: "Clear",
    vehicles: 420,
    delay: "2 min",
  },
  {
    road: "Howrah Bridge",
    area: "Howrah",
    status: "Heavy",
    vehicles: 1510,
    delay: "22 min",
  },
];

const navigation = [
  "Overview",
  "Live Traffic",
  "Route Analysis",
  "Alerts",
  "Analytics",
  "AI Insights",
];

export default function Home() {
  const [activePage, setActivePage] = useState("Overview");
  const [search, setSearch] = useState("");

  const filteredTraffic = trafficData.filter((item) =>
    `${item.road} ${item.area} ${item.status}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const metrics = [
    {
      label: "Roads monitored",
      value: "24",
      note: "Demo metric",
      color: "text-cyan-400",
    },
    {
      label: "Heavy congestion",
      value: "08",
      note: "Illustrative count",
      color: "text-rose-400",
    },
    {
      label: "Average traffic",
      value: "Moderate",
      note: "Sample status",
      color: "text-amber-400",
    },
    {
      label: "Active alerts",
      value: "05",
      note: "Sample alerts",
      color: "text-violet-400",
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-slate-800 bg-slate-900 p-6 lg:block">
        <div className="mb-10 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400 text-xl font-black text-slate-950">
            TV
          </div>

          <div>
            <h1 className="text-lg font-bold">TrafficVision</h1>
            <p className="text-xs text-cyan-400">
              AI TRAFFIC INTELLIGENCE
            </p>
          </div>
        </div>

        <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Workspace
        </p>

        <nav className="space-y-2">
          {navigation.map((item, index) => (
            <button
              key={item}
              onClick={() => setActivePage(item)}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm transition ${
                activePage === item
                  ? "bg-cyan-400 font-semibold text-slate-950"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <span>{["◈", "◎", "⇄", "♧", "▥", "✦"][index]}</span>
              {item}
            </button>
          ))}
        </nav>

        <div className="absolute bottom-6 left-6 right-6 rounded-xl border border-slate-700 p-4">
          <p className="text-sm font-semibold">System status</p>
          <p className="mt-2 text-xs text-amber-400">Demo data mode</p>
          <p className="mt-1 text-xs text-slate-500">
            Live API not connected yet
          </p>
        </div>
      </aside>

      <main className="min-h-screen lg:ml-64">
        <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 bg-slate-950/95 px-5 py-5 backdrop-blur md:px-8">
          <div>
            <p className="text-xs text-slate-500">
              TRAFFICVISION AI / WORKSPACE
            </p>
            <h2 className="mt-1 text-xl font-bold md:text-2xl">
              {activePage}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <NotificationBell />

            <span className="hidden rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-400 sm:block">
              ● Interface ready
            </span>

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 font-bold text-cyan-300">
              OP
            </div>
          </div>
        </header>

        <div className="space-y-7 p-5 md:p-8">
          <section className="relative overflow-hidden rounded-2xl border border-cyan-500/20 bg-linear-to-r from-cyan-950 via-slate-900 to-slate-900 p-6 md:p-8">
            <div className="relative z-10 max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Smart mobility dashboard
              </p>

              <h3 className="mt-3 text-3xl font-bold leading-tight md:text-4xl">
                Understand traffic.
                <br />
                Move smarter.
              </h3>

              <p className="mt-3 max-w-lg text-sm leading-6 text-slate-300">
                Monitor road conditions, review congestion indicators and
                explore intelligent traffic management tools.
              </p>

              <button
                onClick={() => setActivePage("Live Traffic")}
                className="mt-6 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-300"
              >
                Explore traffic →
              </button>
            </div>

            <div className="pointer-events-none absolute -right-8 -top-16 h-64 w-64 rounded-full border border-cyan-400/10 md:right-12">
              <div className="absolute inset-8 rounded-full border border-cyan-400/20">
                <div className="absolute inset-8 rounded-full border border-cyan-400/30" />
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map((metric) => (
              <div
                key={metric.label}
                className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
              >
                <p className="text-sm text-slate-400">{metric.label}</p>
                <p className={`mt-4 text-2xl font-bold ${metric.color}`}>
                  {metric.value}
                </p>
                <p className="mt-2 text-xs text-slate-500">{metric.note}</p>
              </div>
            ))}
          </section>

          <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 xl:col-span-2 md:p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-bold">Road traffic overview</h3>
                  <p className="mt-1 text-sm text-slate-400">
                    Illustrative traffic records
                  </p>
                </div>

                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search roads..."
                  aria-label="Search roads"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-400 sm:w-48"
                />
              </div>

              <div className="mt-6 overflow-x-auto">
                <table className="w-full min-w-130 text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-xs uppercase text-slate-500">
                      <th className="pb-4 pr-4">Road</th>
                      <th className="pb-4 pr-4">Status</th>
                      <th className="pb-4 pr-4">Vehicles</th>
                      <th className="pb-4">Delay</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredTraffic.map((item) => (
                      <tr
                        key={item.road}
                        className="border-b border-slate-800/70"
                      >
                        <td className="py-4 pr-4">
                          <p className="font-medium">{item.road}</p>
                          <p className="mt-1 text-xs text-slate-500">
                            {item.area}
                          </p>
                        </td>

                        <td className="py-4 pr-4">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs ${
                              item.status === "Heavy"
                                ? "bg-rose-500/10 text-rose-400"
                                : item.status === "Moderate"
                                  ? "bg-amber-500/10 text-amber-400"
                                  : "bg-emerald-500/10 text-emerald-400"
                            }`}
                          >
                            {item.status}
                          </span>
                        </td>

                        <td className="py-4 pr-4 text-slate-300">
                          {item.vehicles.toLocaleString()}
                        </td>

                        <td className="py-4 text-slate-300">{item.delay}</td>
                      </tr>
                    ))}

                    {filteredTraffic.length === 0 && (
                      <tr>
                        <td
                          colSpan={4}
                          className="py-8 text-center text-slate-500"
                        >
                          No matching roads found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 md:p-6">
              <h3 className="text-lg font-bold">Traffic insights</h3>
              <p className="mt-1 text-sm text-slate-400">
                Sample recommendations
              </p>

              <div className="mt-6 space-y-4">
                <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-4">
                  <p className="text-xs font-semibold text-rose-400">
                    HIGH PRIORITY
                  </p>
                  <p className="mt-2 text-sm font-semibold">
                    Congestion review
                  </p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">
                    Review heavy-traffic corridors and consider alternate
                    routes.
                  </p>
                </div>

                <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
                  <p className="text-xs font-semibold text-cyan-400">
                    ROUTE TIP
                  </p>
                  <p className="mt-2 text-sm font-semibold">
                    Compare travel delays
                  </p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">
                    Check available route information before choosing a
                    journey.
                  </p>
                </div>

                <div className="rounded-xl border border-slate-700 p-4">
                  <p className="text-sm font-semibold">Data connection</p>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    Sample data only. Actual predictions and alerts require
                    the project&apos;s backend APIs.
                  </p>
                </div>
              </div>

              <button
                onClick={() => setActivePage("AI Insights")}
                className="mt-5 w-full rounded-xl border border-slate-700 px-4 py-3 text-sm font-semibold transition hover:border-cyan-400 hover:text-cyan-300"
              >
                View AI insights →
              </button>
            </div>
          </section>

          <footer className="border-t border-slate-800 py-5 text-xs text-slate-500">
            TrafficVision AI · Smart Traffic Prediction &amp; Congestion
            Management
            <span className="mt-1 block">
              Frontend preview · Metrics are illustrative, not live traffic
              data.
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}
