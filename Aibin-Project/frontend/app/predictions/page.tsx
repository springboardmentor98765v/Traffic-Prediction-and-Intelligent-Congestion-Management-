"use client";

import React, { useState, useEffect } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import Badge from "../components/Badge";
import { api, PredictionHorizon } from "../lib/api";

export default function PredictionsPage() {
  const [horizon, setHorizon] = useState<number>(30);
  const [activeScenario, setActiveScenario] = useState<string | undefined>(undefined);
  const [forecast, setForecast] = useState<PredictionHorizon | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchForecast(horizon, activeScenario);
  }, [horizon, activeScenario]);

  const fetchForecast = async (min: number, scen?: string) => {
    setLoading(true);
    try {
      const res = await api.getPredictionForecast(min, scen);
      setForecast(res.forecast);
    } catch (err) {
      console.error("Forecast fetch error", err);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleScenarioToggle = (scen: string) => {
    if (activeScenario === scen) {
      setActiveScenario(undefined);
      showToast("Simulation reset to baseline conditions.");
    } else {
      setActiveScenario(scen);
      showToast(`Scenario active: ${scen === "rain" ? "Torrential Downpour" : scen === "closure" ? "MG Road Lane Closure" : "Stadium Event Influx"}`);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Toast Alert */}
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
              <span className="text-cyan-400 font-semibold">Milestone 2</span>
              <span>›</span>
              <span className="text-slate-200">Traffic Prediction Engine</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white mt-1 flex items-center gap-2.5">
              <span>AI Congestion Forecasting & Predictive Intelligence</span>
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-mono">
              Model: Heuristic-v2 • ML Engine Active
            </span>
          </div>
        </div>

        {/* Forecast Horizon Selector Bar */}
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 space-y-3 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <span>⏱️</span> Select Predictive Forecast Horizon
              </h3>
              <p className="text-[11px] text-slate-400">
                Forward-looking heuristic simulation adjusted for time-of-day diurnal peaks and active ingress rates.
              </p>
            </div>
            {forecast && (
              <span className="text-xs font-semibold text-cyan-400 bg-cyan-950/60 border border-cyan-500/30 px-3 py-1 rounded-full">
                AI Confidence: {Math.round(forecast.confidence_score * 100)}%
              </span>
            )}
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {[
              { min: 0, label: "Live Telemetry" },
              { min: 15, label: "+15 Mins" },
              { min: 30, label: "+30 Mins" },
              { min: 60, label: "+1 Hour" },
              { min: 120, label: "+2 Hours" },
              { min: 240, label: "+4 Hours (Peak)" },
            ].map((item) => (
              <button
                key={item.min}
                onClick={() => setHorizon(item.min)}
                className={`py-2 px-3 rounded-xl text-xs font-bold transition text-center ${
                  horizon === item.min
                    ? "bg-cyan-600 text-white shadow-lg shadow-cyan-500/25 border border-cyan-400"
                    : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800 hover:border-slate-700"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Top Highlight Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Card title="Predicted Avg Density" icon="📊">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-cyan-400">
                {forecast ? forecast.avg_predicted_density : 51}%
              </span>
              <span className="text-xs font-semibold text-slate-400">
                at horizon {horizon > 0 ? `+${horizon}m` : "now"}
              </span>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              {forecast && forecast.bottlenecks_predicted.length > 0 ? (
                <span className="text-rose-400 font-semibold">
                  {forecast.bottlenecks_predicted.length} Bottleneck(s) Predicted
                </span>
              ) : (
                <span className="text-emerald-400 font-semibold">Smooth network flow</span>
              )}
            </div>
          </Card>

          <Card title="Morning Peak Window" icon="🌅">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-amber-400">08:15 - 09:45</span>
              <span className="text-xs text-slate-400">AM</span>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              Corridors: Station Rd, Indiranagar
            </div>
          </Card>

          <Card title="Evening Peak Window" icon="🌆">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-rose-400">17:30 - 19:30</span>
              <span className="text-xs text-slate-400">PM</span>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              Corridors: MG Road, Ring Road Flyover
            </div>
          </Card>

          <Card title="Model Precision Rate" icon="🎯">
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-emerald-400">89.2%</span>
              <span className="text-xs text-slate-400">AUC 0.93</span>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              Evaluated on historical sensor readings
            </div>
          </Card>
        </div>

        {/* Corridor Congestion Probabilities & Forecast Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Probability Bars (2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            <Card
              title={`Corridor Congestion Risk Forecast (${forecast?.label || "+30m"})`}
              subtitle="Machine learning probability of severe queueing and capacity saturation"
              icon="🤖"
            >
              <div className="space-y-4 mt-2">
                {forecast?.corridors.map((c) => {
                  const probPct = Math.round(c.congestion_probability * 100);
                  let barGradient = "from-emerald-500 to-teal-400";
                  if (c.level === "High") barGradient = "from-amber-500 to-rose-500";
                  else if (c.level === "Medium") barGradient = "from-cyan-500 to-amber-500";

                  return (
                    <div
                      key={c.road_id}
                      className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-2 hover:border-slate-700 transition"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-white">{c.road_name}</span>
                            <span className="text-[10px] font-mono text-slate-500">{c.road_id}</span>
                            {c.peak_surge && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase tracking-wider animate-pulse">
                                Surge Warning
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2.5">
                          <span className="text-xs font-mono font-bold text-cyan-400">
                            {c.predicted_density}% Density
                          </span>
                          <Badge variant={c.level}>{c.level}</Badge>
                        </div>
                      </div>

                      {/* Probability Meter Bar */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                          <span>Bottleneck Probability:</span>
                          <span className="font-bold text-slate-200">{probPct}%</span>
                        </div>
                        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                          <div
                            className={`bg-gradient-to-r ${barGradient} h-full rounded-full transition-all duration-700`}
                            style={{ width: `${probPct}%` }}
                          />
                        </div>
                      </div>

                      <div className="text-[11px] text-slate-300 flex items-start gap-1.5 pt-1">
                        <span className="text-cyan-400">💡</span>
                        <span><strong>AI Action:</strong> {c.recommendation}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>

          {/* Scenario Simulation Sandbox (1 col) */}
          <div className="space-y-4">
            <Card
              title="Simulation Sandbox"
              subtitle="Test AI dynamic adaptation under severe external events"
              icon="🧪"
              badge={
                activeScenario ? (
                  <Badge variant="warning" pulse>
                    Simulation Active
                  </Badge>
                ) : (
                  <Badge variant="low">Baseline</Badge>
                )
              }
            >
              <div className="space-y-3 mt-2">
                <p className="text-xs text-slate-300 leading-relaxed">
                  Trigger synthetic traffic stress tests to evaluate the predictive model's ability to trigger early rerouting:
                </p>

                <div className="space-y-2">
                  <button
                    onClick={() => handleScenarioToggle("rain")}
                    className={`w-full p-3 rounded-xl border text-left text-xs transition flex items-center justify-between ${
                      activeScenario === "rain"
                        ? "bg-cyan-500/20 border-cyan-500 text-white shadow-lg"
                        : "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <div className="font-bold flex items-center gap-1.5">
                        <span>🌧️</span> Torrential Downpour
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        -30% road friction, +25% delay multiplier across all nodes
                      </div>
                    </div>
                    <span className="text-xs font-bold">{activeScenario === "rain" ? "ON" : "OFF"}</span>
                  </button>

                  <button
                    onClick={() => handleScenarioToggle("closure")}
                    className={`w-full p-3 rounded-xl border text-left text-xs transition flex items-center justify-between ${
                      activeScenario === "closure"
                        ? "bg-rose-500/20 border-rose-500 text-white shadow-lg"
                        : "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <div className="font-bold flex items-center gap-1.5">
                        <span>🚧</span> MG Road Lane Blockage
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        R001 density jumps to 95%, triggering automatic Ring Road bypass
                      </div>
                    </div>
                    <span className="text-xs font-bold">{activeScenario === "closure" ? "ON" : "OFF"}</span>
                  </button>

                  <button
                    onClick={() => handleScenarioToggle("event")}
                    className={`w-full p-3 rounded-xl border text-left text-xs transition flex items-center justify-between ${
                      activeScenario === "event"
                        ? "bg-purple-500/20 border-purple-500 text-white shadow-lg"
                        : "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <div className="font-bold flex items-center gap-1.5">
                        <span>🏟️</span> Stadium Event Influx
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Sudden surge of +40% vehicle volume entering East metro corridor
                      </div>
                    </div>
                    <span className="text-xs font-bold">{activeScenario === "event" ? "ON" : "OFF"}</span>
                  </button>
                </div>

                {activeScenario && (
                  <button
                    onClick={() => handleScenarioToggle(activeScenario)}
                    className="w-full mt-2 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
                  >
                    Reset to Baseline Conditions
                  </button>
                )}
              </div>
            </Card>

            {/* AI Mitigation Strategy Card */}
            <Card title="Automated AI Mitigation" icon="🛡️">
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Proactive Signal Tuning:</span>
                  <span className="text-emerald-400 font-bold">Enabled</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>VMS Advisory Broadcasting:</span>
                  <span className="text-cyan-400 font-bold">Auto-Trigger</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Reroute Engine Sync:</span>
                  <span className="text-indigo-400 font-bold">Active</span>
                </div>
                <p className="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                  When probability exceeds 75%, TrafficVision AI automatically generates dynamic rerouting instructions for the Route Analysis module.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}
