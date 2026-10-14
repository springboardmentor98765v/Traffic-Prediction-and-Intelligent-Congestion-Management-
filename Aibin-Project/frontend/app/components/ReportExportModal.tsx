"use client";

import React, { useState } from "react";
import { api, HistoricalReportFilter, TrafficRoad } from "../lib/api";
import { useTraffic } from "../lib/traffic-context";

interface ReportExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ReportExportModal({ isOpen, onClose }: ReportExportModalProps) {
  const { roads } = useTraffic();

  const [dateRange, setDateRange] = useState<"24h" | "7d" | "30d" | "custom">("24h");
  const [corridorId, setCorridorId] = useState<string>("all");
  const [includeTelemetry, setIncludeTelemetry] = useState<boolean>(true);
  const [includeAlerts, setIncludeAlerts] = useState<boolean>(true);
  const [includeRecommendations, setIncludeRecommendations] = useState<boolean>(true);
  const [includeCarbonMetrics, setIncludeCarbonMetrics] = useState<boolean>(true);

  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  if (!isOpen) return null;

  const currentFilter: HistoricalReportFilter = {
    dateRange,
    corridorId,
    includeTelemetry,
    includeAlerts,
    includeRecommendations,
    includeCarbonMetrics,
  };

  const handleDownloadCsv = () => {
    setIsExporting(true);
    try {
      api.downloadCsvReport(currentFilter);
      setDownloadSuccess("CSV historical telemetry report downloaded successfully.");
      setTimeout(() => setDownloadSuccess(null), 3500);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadJson = () => {
    setIsExporting(true);
    try {
      api.downloadJsonReport(currentFilter);
      setDownloadSuccess("Structured JSON analytics dataset downloaded successfully.");
      setTimeout(() => setDownloadSuccess(null), 3500);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadHtml = () => {
    setIsExporting(true);
    try {
      api.downloadHtmlExecutiveReport(currentFilter);
      setDownloadSuccess("Executive printable report generated in new tab.");
      setTimeout(() => setDownloadSuccess(null), 3500);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-lg rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">📥</span>
              <h3 className="text-base font-bold text-white tracking-tight">
                Historical Traffic & Congestion Report Export
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Export corridor telemetry, bottleneck incident audits, and AI optimization logs.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-lg font-bold"
          >
            ✕
          </button>
        </div>

        {/* Success Alert Banner */}
        {downloadSuccess && (
          <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/40 p-3 text-xs font-semibold text-emerald-300">
            ✓ {downloadSuccess}
          </div>
        )}

        {/* Parameter Configurations */}
        <div className="space-y-4 text-xs">
          {/* 1. Date Range Selection */}
          <div>
            <label className="block font-semibold text-slate-300 mb-1.5 uppercase text-[10px] tracking-wider">
              Temporal Window
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: "24h", label: "Last 24 Hours", sub: "Hourly data" },
                { id: "7d", label: "Past 7 Days", sub: "Daily trends" },
                { id: "30d", label: "Last 30 Days", sub: "Monthly audit" },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setDateRange(item.id as any)}
                  className={`p-2.5 rounded-xl border text-left transition ${
                    dateRange === item.id
                      ? "bg-cyan-950/50 border-cyan-500 text-cyan-300 shadow-sm"
                      : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <div className="font-bold text-xs">{item.label}</div>
                  <div className="text-[10px] opacity-70">{item.sub}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 2. Corridor Scope Filter */}
          <div>
            <label className="block font-semibold text-slate-300 mb-1.5 uppercase text-[10px] tracking-wider">
              Corridor Scope
            </label>
            <select
              value={corridorId}
              onChange={(e) => setCorridorId(e.target.value)}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs font-medium text-slate-200 focus:border-cyan-500 focus:outline-none transition shadow-sm"
            >
              <option value="all">Entire City Network (All Corridors)</option>
              {roads.map((r) => (
                <option key={r.road_id} value={r.road_id}>
                  {r.name} ({r.road_id})
                </option>
              ))}
            </select>
          </div>

          {/* 3. Included Datasets Checkboxes */}
          <div>
            <label className="block font-semibold text-slate-300 mb-1.5 uppercase text-[10px] tracking-wider">
              Datasets to Include in Export
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="flex items-center gap-2 rounded-xl bg-slate-950/60 border border-slate-800/80 p-2.5 cursor-pointer hover:bg-slate-950">
                <input
                  type="checkbox"
                  checked={includeTelemetry}
                  onChange={(e) => setIncludeTelemetry(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-600 focus:ring-0"
                />
                <span className="text-slate-200 font-medium">Sensor Telemetry</span>
              </label>

              <label className="flex items-center gap-2 rounded-xl bg-slate-950/60 border border-slate-800/80 p-2.5 cursor-pointer hover:bg-slate-950">
                <input
                  type="checkbox"
                  checked={includeAlerts}
                  onChange={(e) => setIncludeAlerts(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-600 focus:ring-0"
                />
                <span className="text-slate-200 font-medium">Incidents & Alerts</span>
              </label>

              <label className="flex items-center gap-2 rounded-xl bg-slate-950/60 border border-slate-800/80 p-2.5 cursor-pointer hover:bg-slate-950">
                <input
                  type="checkbox"
                  checked={includeRecommendations}
                  onChange={(e) => setIncludeRecommendations(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-600 focus:ring-0"
                />
                <span className="text-slate-200 font-medium">AI Decision Logs</span>
              </label>

              <label className="flex items-center gap-2 rounded-xl bg-slate-950/60 border border-slate-800/80 p-2.5 cursor-pointer hover:bg-slate-950">
                <input
                  type="checkbox"
                  checked={includeCarbonMetrics}
                  onChange={(e) => setIncludeCarbonMetrics(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-600 focus:ring-0"
                />
                <span className="text-slate-200 font-medium">CO2 & Eco Metrics</span>
              </label>
            </div>
          </div>
        </div>

        {/* 3 Export Action Buttons */}
        <div className="pt-3 border-t border-slate-800 space-y-2">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Select Export Format:
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {/* CSV */}
            <button
              onClick={handleDownloadCsv}
              disabled={isExporting}
              className="flex items-center justify-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/80 p-3 text-xs font-bold text-slate-200 transition shadow-sm"
            >
              <span>📄</span>
              <span>Download CSV</span>
            </button>

            {/* JSON */}
            <button
              onClick={handleDownloadJson}
              disabled={isExporting}
              className="flex items-center justify-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/80 p-3 text-xs font-bold text-cyan-300 transition shadow-sm"
            >
              <span>⚙️</span>
              <span>Download JSON</span>
            </button>

            {/* Printable HTML / PDF */}
            <button
              onClick={handleDownloadHtml}
              disabled={isExporting}
              className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:brightness-110 p-3 text-xs font-bold text-white transition shadow-lg shadow-cyan-600/20"
            >
              <span>📊</span>
              <span>Executive Report</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
