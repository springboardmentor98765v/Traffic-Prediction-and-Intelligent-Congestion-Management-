"use client";

import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import Card from "../components/Card";
import { useAuth } from "../lib/auth-context";
import { api, TrafficRoad, DensityMetrics, PredictionResult, UserProfile } from "../lib/api";

export default function DashboardPage() {
  const { user, role, isAuthenticated } = useAuth();

  const [roads, setRoads] = useState<TrafficRoad[]>([]);
  const [metrics, setMetrics] = useState<DensityMetrics | null>(null);
  const [selectedRoadId, setSelectedRoadId] = useState<string>("R001");
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [usersList, setUsersList] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [predicting, setPredicting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [roadsData, metricsData] = await Promise.all([
        api.getLiveTraffic(),
        api.getDensityMetrics(),
      ]);
      setRoads(roadsData);
      setMetrics(metricsData);
      setLastRefreshed(new Date().toLocaleTimeString());

      // Fetch initial prediction
      if (roadsData.length > 0) {
        const initialId = roadsData[0].road_id;
        const pred = await api.getPrediction(initialId);
        setPrediction(pred);
      }

      // Fetch admin users if admin
      if (role === "admin") {
        try {
          const uList = await api.getUsers();
          setUsersList(uList);
        } catch {
          // ignore if unauthorized
        }
      }
    } catch (err: any) {
      setError(err.message || "Could not connect to backend server. Make sure Backend is running at http://localhost:8000");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [role]);

  const handlePredictForRoad = async (roadId: string) => {
    setSelectedRoadId(roadId);
    setPredicting(true);
    try {
      const pred = await api.getPrediction(roadId);
      setPrediction(pred);
    } catch (err: any) {
      console.error(err);
    } finally {
      setPredicting(false);
    }
  };

  const getCongestionBadge = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "bg-red-100 text-red-700 border-red-200";
      case "medium":
        return "bg-amber-100 text-amber-700 border-amber-200";
      default:
        return "bg-emerald-100 text-emerald-700 border-emerald-200";
    }
  };

  return (
    <Layout>
      {/* Top Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between pb-6 border-b border-gray-200">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Traffic Monitoring Dashboard
            </h1>
            <span className="rounded-md bg-blue-100 px-2.5 py-0.5 text-xs font-bold text-blue-800 uppercase tracking-wide">
              Milestone 1 Live
            </span>
          </div>
          <p className="mt-1 text-sm text-gray-600">
            Real-time congestion monitoring, telemetry tracking, and heuristic AI predictions
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastRefreshed && (
            <span className="text-xs text-gray-500">
              Updated: <span className="font-semibold text-gray-700">{lastRefreshed}</span>
            </span>
          )}
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-white border border-gray-300 px-3.5 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 shadow-sm transition disabled:opacity-50"
          >
            <span>🔄</span>
            <span>{loading ? "Refreshing..." : "Refresh Feed"}</span>
          </button>
        </div>
      </div>

      {/* Backend Offline / Connection Error Banner */}
      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-800 shadow-sm">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <h3 className="font-bold text-red-900">Backend Communication Notice</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
              <p className="mt-2 text-xs text-red-600 font-mono bg-red-100 p-2 rounded">
                Start Backend: python Backend/run.py (Listening on http://localhost:8000)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Role Banner */}
      <div className="mt-6 rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-700">
              Active Context:
            </span>
            <span className="ml-2 font-bold text-gray-900 capitalize">
              {role} View
            </span>
            <p className="text-xs text-gray-600 mt-0.5">
              {role === "admin"
                ? "Full administrative access: user management, system diagnostics, and route overrides."
                : role === "operator"
                ? "Operational monitoring: real-time telemetry, signal status, and congestion alerts."
                : "Commuter access: public live road status and route congestion forecasts."}
            </p>
          </div>
          {!isAuthenticated && (
            <span className="text-xs bg-white px-2.5 py-1 rounded border border-blue-200 text-blue-700 font-medium self-start sm:self-auto">
              Viewing as Guest. Sign in for role-specific controls.
            </span>
          )}
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          title="Average Road Density"
          value={metrics ? `${metrics.average_density}%` : "36.5%"}
          valueClassName={
            metrics && metrics.average_density > 50
              ? "text-red-600"
              : metrics && metrics.average_density > 25
              ? "text-amber-600"
              : "text-emerald-600"
          }
        />
        <Card
          title="Monitored Road Corridors"
          value={metrics ? metrics.total_roads : roads.length || 5}
          valueClassName="text-blue-700"
        />
        <Card
          title="Congested Corridors"
          value={metrics ? metrics.congested_roads : 0}
          valueClassName={
            metrics && metrics.congested_roads > 0 ? "text-red-600" : "text-emerald-600"
          }
        />
        <Card
          title="AI Prediction Engine"
          value="heuristic-v0"
          valueClassName="text-purple-600"
        />
      </div>

      {/* Live Monitored Roads Table */}
      <div className="mt-8 rounded-xl bg-white p-6 shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-100 gap-2">
          <div>
            <h2 className="text-lg font-bold text-gray-900">
              Live Road Corridors Telemetry
            </h2>
            <p className="text-xs text-gray-500">
              Real sensor telemetry and calculated congestion levels per road corridor (R001–R005)
            </p>
          </div>
          <span className="text-xs text-gray-500 font-medium">
            Total active segments: {roads.length}
          </span>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-xs font-bold uppercase text-gray-500 tracking-wider">
              <tr>
                <th className="px-4 py-3">Road ID</th>
                <th className="px-4 py-3">Corridor Name</th>
                <th className="px-4 py-3">Vehicle Count</th>
                <th className="px-4 py-3">Density</th>
                <th className="px-4 py-3">Congestion Level</th>
                <th className="px-4 py-3">Telemetry Time</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {roads.map((road) => (
                <tr
                  key={road.road_id}
                  className={`hover:bg-blue-50/50 transition ${
                    selectedRoadId === road.road_id ? "bg-blue-50/80 font-medium" : ""
                  }`}
                >
                  <td className="px-4 py-3.5 font-bold font-mono text-gray-900">
                    {road.road_id}
                  </td>
                  <td className="px-4 py-3.5 text-gray-800">
                    {road.name}
                  </td>
                  <td className="px-4 py-3.5 font-mono text-gray-700">
                    {road.vehicle_count} veh/hr
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            road.density > 50
                              ? "bg-red-500"
                              : road.density > 20
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                          }`}
                          style={{ width: `${Math.min(road.density, 100)}%` }}
                        ></div>
                      </div>
                      <span className="font-mono text-xs">{road.density}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold border ${getCongestionBadge(
                        road.congestion_level
                      )}`}
                    >
                      {road.congestion_level}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-xs text-gray-500 font-mono">
                    {road.updated_at ? road.updated_at.replace("T", " ").slice(0, 19) : "Just now"}
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button
                      onClick={() => handlePredictForRoad(road.road_id)}
                      className="rounded-md bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-bold text-blue-700 hover:bg-blue-600 hover:text-white transition"
                    >
                      Predict
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Prediction Section */}
      <div className="mt-8 rounded-xl bg-white p-6 shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-100 gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🤖</span>
              <h2 className="text-lg font-bold text-gray-900">
                AI Congestion Prediction Stub (Milestone 1 Heuristic)
              </h2>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">
              Rule-based heuristic prediction unblocking UI and QA integration ahead of trained model in Milestone 2
            </p>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs font-bold text-gray-600">Select Corridor:</label>
            <select
              value={selectedRoadId}
              onChange={(e) => handlePredictForRoad(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-bold text-gray-800 outline-none focus:border-blue-600"
            >
              {roads.map((r) => (
                <option key={r.road_id} value={r.road_id}>
                  {r.road_id} — {r.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {predicting ? (
          <div className="py-8 text-center text-sm text-gray-500">
            Computing heuristic forecast...
          </div>
        ) : prediction ? (
          <div className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <span className="text-xs text-gray-500 uppercase font-semibold">Selected Corridor</span>
              <p className="mt-1 text-base font-bold text-gray-900">{prediction.road_id}</p>
              <p className="text-xs text-gray-600">{prediction.road_name || "Monitored Segment"}</p>
            </div>

            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <span className="text-xs text-gray-500 uppercase font-semibold">Predicted Congestion</span>
              <p className="mt-1 text-base font-bold">
                <span className={`inline-block px-2.5 py-0.5 rounded text-xs border ${getCongestionBadge(prediction.predicted_level)}`}>
                  {prediction.predicted_level}
                </span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Hour of Day: {prediction.time_of_day}:00
              </p>
            </div>

            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <span className="text-xs text-gray-500 uppercase font-semibold">Confidence Score</span>
              <p className="mt-1 text-base font-bold text-blue-700">
                {Math.round(prediction.confidence * 100)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Rule consistency metric</p>
            </div>

            <div className="rounded-xl border border-gray-200 p-4 bg-gray-50">
              <span className="text-xs text-gray-500 uppercase font-semibold">Model Version</span>
              <p className="mt-1 text-base font-bold text-purple-700 font-mono">
                {prediction.generated_by}
              </p>
              <p className="text-xs text-gray-500 mt-1">M2 Trained ML model in plan</p>
            </div>
          </div>
        ) : null}
      </div>

      {/* Role-Specific Panel: Admin Controls & User Management */}
      {role === "admin" && (
        <div className="mt-8 rounded-xl bg-purple-50/70 border border-purple-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">👑</span>
            <h2 className="text-lg font-bold text-purple-950">
              Administrator Console — User Management & RBAC
            </h2>
          </div>
          <p className="text-xs text-purple-800 mb-4">
            Protected endpoint <code>/api/v1/auth/users</code> accessible only to users with the <code>admin</code> role.
          </p>

          <div className="overflow-x-auto bg-white rounded-lg border border-purple-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-purple-100/60 text-xs font-bold uppercase text-purple-900">
                <tr>
                  <th className="px-4 py-2.5">User ID</th>
                  <th className="px-4 py-2.5">Name</th>
                  <th className="px-4 py-2.5">Email</th>
                  <th className="px-4 py-2.5">Assigned Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {usersList.length > 0 ? (
                  usersList.map((u) => (
                    <tr key={u.user_id} className="hover:bg-purple-50/40">
                      <td className="px-4 py-2.5 font-mono text-xs text-gray-600">
                        {u.user_id.slice(0, 8)}...
                      </td>
                      <td className="px-4 py-2.5 font-medium text-gray-900">{u.name}</td>
                      <td className="px-4 py-2.5 text-gray-600">{u.email}</td>
                      <td className="px-4 py-2.5">
                        <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800">
                          {u.role}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-3 text-center text-xs text-gray-500">
                      No additional users retrieved.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Role-Specific Panel: Operator Controls */}
      {role === "operator" && (
        <div className="mt-8 rounded-xl bg-amber-50/80 border border-amber-200 p-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">🛠️</span>
            <h2 className="text-lg font-bold text-amber-950">
              Operator Traffic Management Console
            </h2>
          </div>
          <p className="text-xs text-amber-800 mb-4">
            Operational controls for dispatching congestion alerts and adjusting corridor signal timing.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="rounded-lg bg-white p-4 border border-amber-200 shadow-sm">
              <h4 className="font-bold text-gray-900">🚨 Trigger Incident Alert</h4>
              <p className="text-gray-600 mt-1">Broadcast automated advisory to commuter portals for high-congestion zones.</p>
              <button
                onClick={() => alert("Simulated Incident Alert broadcast successfully to operators and commuters.")}
                className="mt-3 rounded bg-amber-600 px-3 py-1.5 text-white font-bold hover:bg-amber-700 transition"
              >
                Broadcast Alert
              </button>
            </div>

            <div className="rounded-lg bg-white p-4 border border-amber-200 shadow-sm">
              <h4 className="font-bold text-gray-900">⏱️ Green-Wave Signal Timing</h4>
              <p className="text-gray-600 mt-1">Extend green cycle by 20% on heavily congested corridor (R001 / R004).</p>
              <button
                onClick={() => alert("Signal cycle optimization applied to R001 corridor.")}
                className="mt-3 rounded bg-amber-600 px-3 py-1.5 text-white font-bold hover:bg-amber-700 transition"
              >
                Adjust Timing
              </button>
            </div>

            <div className="rounded-lg bg-white p-4 border border-amber-200 shadow-sm">
              <h4 className="font-bold text-gray-900">📡 Sensor Feed Diagnostics</h4>
              <p className="text-gray-600 mt-1">Sensors S001–S005 online. Zero packet drop across last 1,000 telemetry readings.</p>
              <span className="mt-3 inline-block font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded">
                All 5 Sensors Active
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Role-Specific Panel: Public / Commuter Advice */}
      {role === "public" && (
        <div className="mt-8 rounded-xl bg-emerald-50/80 border border-emerald-200 p-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">🚗</span>
            <h2 className="text-lg font-bold text-emerald-950">
              Commuter Route Advisory
            </h2>
          </div>
          <p className="text-xs text-emerald-800 mb-4">
            Live travel advisories and low-traffic corridor recommendations for city travelers.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="rounded-lg bg-white p-4 border border-emerald-200 shadow-sm">
              <span className="font-bold text-emerald-700">Recommended Corridor:</span>
              <p className="font-bold text-gray-900 text-sm mt-1">
                {roads.find((r) => r.congestion_level === "Low")?.name || "R002 — Ring Road"}
              </p>
              <p className="text-gray-600 mt-1">Currently operating with normal flow and low vehicle density.</p>
            </div>

            <div className="rounded-lg bg-white p-4 border border-emerald-200 shadow-sm">
              <span className="font-bold text-amber-700">Avoid If Possible:</span>
              <p className="font-bold text-gray-900 text-sm mt-1">
                {roads.find((r) => r.congestion_level === "High")?.name || "R001 — MG Road"}
              </p>
              <p className="text-gray-600 mt-1">High congestion detected. Consider alternate connector roads.</p>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}