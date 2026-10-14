"use client";

import React, { useState } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import TrendChart from "../components/TrendChart";
import CongestionHeatmap from "../components/CongestionHeatmap";
import AIRecommendationsPanel from "../components/AIRecommendationsPanel";
import ReportExportModal from "../components/ReportExportModal";
import { useTraffic } from "../lib/traffic-context";

export default function AnalyticsPage() {
  const { roads, metrics, recommendations } = useTraffic();
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  const appliedInterventionsCount = recommendations.filter((r) => r.status === "applied").length;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header & Export Action */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>TrafficVision AI</span>
              <span>›</span>
              <span className="text-cyan-400 font-semibold">Traffic Analytics</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1">
              Historical Trends, Heatmaps & AI Forecasting
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Diurnal pattern evaluation, 7×24 congestion heatmap matrix, longitudinal trend charts, and automated mitigation intelligence.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setIsExportModalOpen(true)}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:brightness-110 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 transition"
            >
              <span>📥</span>
              <span>Download Historical Report</span>
            </button>
          </div>
        </div>

        {/* 4 Top Highlight Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card title="AI Heuristic Precision" icon="🤖">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-cyan-400">88.4%</span>
              <span className="text-xs text-emerald-400 font-semibold">±2.1% margin</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Trained heuristic stub evaluates time-of-day peak multipliers against active sensor density.
            </p>
          </Card>

          <Card title="Peak Congestion Lead Time" icon="⏱️">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-indigo-400">22 min</span>
              <span className="text-xs text-slate-400">Early bottleneck alert</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Allows dispatchers to adjust signal phases prior to severe physical queue spillback.
            </p>
          </Card>

          <Card title="Estimated Carbon Offset" icon="🌱">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-emerald-400">-14.2%</span>
              <span className="text-xs text-emerald-400 font-semibold">Idle fuel savings</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Achieved via active detour broadcasts diverting vehicles away from Station & MG Road bottlenecks.
            </p>
          </Card>

          <Card title="AI Optimizations Applied" icon="⚡">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-amber-400">
                {appliedInterventionsCount} Active
              </span>
              <span className="text-xs text-slate-400">Of {recommendations.length} proposed</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              Signal cycle extensions and dynamic arterial offsets currently active across corridors.
            </p>
          </Card>
        </div>

        {/* Multi-Metric Longitudinal Trend Chart */}
        <TrendChart initialTimeframe="24h" />

        {/* 7x24 Diurnal Congestion Heatmap Matrix */}
        <CongestionHeatmap />

        {/* AI Decision Support & Mitigation Recommendations */}
        <AIRecommendationsPanel />

        {/* Arterial Road Comparison Matrix */}
        <Card
          title="Arterial Corridor Performance Matrix"
          subtitle="Cross-corridor comparison of capacity, average delay, and AI prediction reliability"
          icon="📊"
        >
          <div className="overflow-x-auto mt-2">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                  <th className="pb-3 font-semibold">Corridor</th>
                  <th className="pb-3 font-semibold">Current Density</th>
                  <th className="pb-3 font-semibold">Avg Speed</th>
                  <th className="pb-3 font-semibold">Peak Delay</th>
                  <th className="pb-3 font-semibold">Congestion Index</th>
                  <th className="pb-3 font-semibold text-right">AI Recommendation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {roads.map((road) => (
                  <tr key={road.road_id} className="hover:bg-slate-900/50 transition">
                    <td className="py-3">
                      <div className="font-semibold text-slate-200">{road.name}</div>
                      <div className="text-[10px] font-mono text-slate-500">{road.road_id}</div>
                    </td>
                    <td className="py-3 font-bold text-slate-100">{road.density}%</td>
                    <td className="py-3 font-mono text-slate-300">{road.speed} km/h</td>
                    <td className="py-3">
                      <span
                        className={`font-semibold ${
                          road.density > 50
                            ? "text-rose-400"
                            : road.density >= 25
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {road.density > 50 ? "+16 min" : road.density >= 25 ? "+5 min" : "0 min"}
                      </span>
                    </td>
                    <td className="py-3">
                      <Badge variant={road.congestion_level}>{road.congestion_level}</Badge>
                    </td>
                    <td className="py-3 text-right text-[11px] text-slate-400 font-medium">
                      {road.density > 50
                        ? "Lengthen green phase & suggest detour"
                        : road.density >= 25
                        ? "Monitor arterial merge rate"
                        : "Optimal corridor velocity"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Historical Report Export Dialog */}
        <ReportExportModal
          isOpen={isExportModalOpen}
          onClose={() => setIsExportModalOpen(false)}
        />
      </div>
    </Layout>
  );
}
