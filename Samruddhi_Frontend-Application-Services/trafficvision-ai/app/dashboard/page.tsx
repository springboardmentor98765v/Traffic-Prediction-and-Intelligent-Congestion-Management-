'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { Card } from '@/components/Card';
import {
  Radio,
  PlusCircle,
  Users,
  Navigation,
  Route,
  Clock,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';

interface PredictionItem {
  time: string;
  traffic: 'Low' | 'Moderate' | 'Heavy';
  travelTime: number;
  congestion: number;
}

interface RouteOption {
  id: string;
  name: string;
  distance_km: number;
  estimated_minutes: number;
  trafficLevel: 'Low' | 'Moderate' | 'Heavy';
  roadCondition: 'Clear' | 'Road Work' | 'Heavy Traffic';
  estimatedDelay: number;
  hazardInfo: string;
  color: string;
  geometry: [number, number][];
}

interface RouteAnalysisData {
  origin: string;
  destination: string;
  selectedRouteId: string;
  selectedRoute: RouteOption;
  routes: RouteOption[];
  predictionData: PredictionItem[];
  updatedAt: string;
}

export default function DashboardPage() {
  const [role, setRole] = useState('Public');
  const [username, setUsername] = useState('USER');
  const API_BASE = 'http://127.0.0.1:8002/api/v1';
  const [apiCongestion, setApiCongestion] = useState<string | null>(null);
  const [apiConfidence, setApiConfidence] = useState<number | null>(null);
  const [apiPeakWindows, setApiPeakWindows] = useState<Array<{start: string; end: string}>>([]);
  const [apiDelay, setApiDelay] = useState<number | null>(null);
  const [activeIncidentCount, setActiveIncidentCount] = useState<number | null>(null);
  const [dashboardWarning, setDashboardWarning] = useState<string | null>(null);

  const [routeAnalysis, setRouteAnalysis] =
    useState<RouteAnalysisData | null>(null);

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Public');
    setUsername(localStorage.getItem('username') || 'USER');

    const loadRouteAnalysis = () => {
      const savedData = localStorage.getItem(
        'trafficvision_route_analysis'
      );

      if (savedData) {
        try {
          setRouteAnalysis(JSON.parse(savedData));
        } catch (error) {
          console.error(
            'Unable to load route analysis data:',
            error
          );
        }
      }
    };

    loadRouteAnalysis();

    window.addEventListener(
      'trafficvision-route-updated',
      loadRouteAnalysis
    );

    return () => {
      window.removeEventListener(
        'trafficvision-route-updated',
        loadRouteAnalysis
      );
    };
  }, []);


  useEffect(() => {
    let cancelled = false;

    async function loadDashboardData() {
      const errors: string[] = [];

      try {
        const response = await fetch(`${API_BASE}/traffic/nodes`);
        if (!response.ok) throw new Error(`Roads API: HTTP ${response.status}`);

        const payload = await response.json();
        const roads = Array.isArray(payload) ? payload : payload.value;
        if (!Array.isArray(roads) || roads.length === 0) {
          throw new Error('No roads returned by the backend.');
        }

        const roadId = Number(roads[0].id);
        const time = new Date().toISOString().slice(0, 19);

        const results = await Promise.allSettled([
          fetch(`${API_BASE}/predict/congestion?road_id=${roadId}&time=${encodeURIComponent(time)}`)
            .then(async r => {
              if (!r.ok) throw new Error(`Congestion: HTTP ${r.status}`);
              return r.json();
            }),
          fetch(`${API_BASE}/predict/delay?road_id=${roadId}`)
            .then(async r => {
              if (!r.ok) throw new Error(`Delay: HTTP ${r.status}`);
              return r.json();
            }),
          fetch(`${API_BASE}/alerts/active`, {
            headers: localStorage.getItem('access_token')
              ? { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
              : {}
          }).then(async r => {
            if (!r.ok) throw new Error(r.status === 401 ? 'Sign in to view incidents.' : `Alerts: HTTP ${r.status}`);
            return r.json();
          }),
          fetch(`${API_BASE}/predict/peak-hours?road_id=${roadId}`)
            .then(async r => {
              if (!r.ok) throw new Error(`Peak hours: HTTP ${r.status}`);
              return r.json();
            })
        ]);

        if (cancelled) return;

        if (results[0].status === 'fulfilled') {
          setApiCongestion(String(results[0].value.predicted_level ?? 'Unavailable'));
          const confidence = Number(results[0].value.confidence);
          setApiConfidence(Number.isFinite(confidence) ? confidence : null);
        } else {
          errors.push('Congestion prediction unavailable.');
        }

        if (results[1].status === 'fulfilled') {
          const delay = Number(results[1].value.estimated_delay_minutes);
          if (Number.isFinite(delay)) setApiDelay(delay);
          else errors.push('Invalid delay response.');
        } else {
          errors.push('Delay prediction unavailable.');
        }

        if (results[2].status === 'fulfilled') {
          const data = results[2].value;
          const alerts = Array.isArray(data) ? data : data.value ?? data.alerts;
          if (Array.isArray(alerts)) setActiveIncidentCount(alerts.length);
          else errors.push('Unexpected incidents response format.');
        } else {
          errors.push(results[2].reason instanceof Error
            ? results[2].reason.message
            : 'Incidents unavailable.');
        }

        if (results[3].status === 'fulfilled') {
          const windows = results[3].value.peak_windows;
          setApiPeakWindows(Array.isArray(windows) ? windows : []);
        } else {
          errors.push('Peak-hour prediction unavailable.');
        }

        setDashboardWarning(errors.length ? errors.join(' ') : null);
      } catch (error) {
        if (!cancelled) {
          setDashboardWarning(error instanceof Error ? error.message : 'Dashboard API unavailable.');
        }
      }
    }

    loadDashboardData();
    const refreshId = window.setInterval(loadDashboardData, 60000);
    return () => { cancelled = true; window.clearInterval(refreshId); };
  }, []);
  const selectedRoute = routeAnalysis?.selectedRoute;

  const alternativeRoute =
    routeAnalysis?.routes?.find(
      (route) =>
        route.id !== routeAnalysis.selectedRouteId
    );

  const predictionData =
    routeAnalysis?.predictionData || [];

  const currentPrediction =
    predictionData.length > 0
      ? predictionData[0]
      : null;

  const peakPrediction =
    predictionData.length > 0
      ? predictionData.reduce((highest, current) =>
          current.congestion > highest.congestion
            ? current
            : highest
        )
      : null;

  const getTrafficColor = (
    traffic?: 'Low' | 'Moderate' | 'Heavy'
  ) => {
    if (traffic === 'Low') {
      return 'text-emerald-400';
    }

    if (traffic === 'Moderate') {
      return 'text-amber-400';
    }

    if (traffic === 'Heavy') {
      return 'text-red-400';
    }

    return 'text-gray-400';
  };

  const getTrafficBackground = (
    traffic?: 'Low' | 'Moderate' | 'Heavy'
  ) => {
    if (traffic === 'Low') {
      return 'bg-emerald-500/10 border-emerald-500/30';
    }

    if (traffic === 'Moderate') {
      return 'bg-amber-500/10 border-amber-500/30';
    }

    if (traffic === 'Heavy') {
      return 'bg-red-500/10 border-red-500/30';
    }

    return 'bg-[#0d1117] border-[#30363d]';
  };

  return (
    <div className="flex min-h-screen bg-[#0d1117] text-white">

      <Sidebar role={role} />

      <main className="flex-1 p-8 overflow-y-auto">

        <Header
          username={username}
          role={role}
        />

        <div className="space-y-6">

          {/* ================= TOP METRICS ================= */}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            <Card
              title="Current Congestion Index"
              value={
                selectedRoute
                  ? `${selectedRoute.trafficLevel} Traffic`
                  : apiCongestion
                    ? `${apiCongestion} Traffic`
                    : 'Loading...'
              }
              valueColor={
                selectedRoute
                  ? getTrafficColor(selectedRoute.trafficLevel)
                  : apiCongestion
                    ? getTrafficColor(apiCongestion === 'LOW' ? 'Low' : apiCongestion === 'MEDIUM' ? 'Moderate' : apiCongestion === 'HIGH' ? 'Heavy' : undefined)
                    : 'text-amber-400'
              }
            />

            <Card
              title="Active Road Incidents"
              value={activeIncidentCount !== null ? `${activeIncidentCount} Reported` : 'Loading...'}
              valueColor="text-rose-500"
            />

            <Card
              title="Est. Average Delay"
              value={
                selectedRoute
                  ? `+${selectedRoute.estimatedDelay} mins`
                  : apiDelay !== null
                    ? `+${apiDelay} mins`
                    : 'Loading...'
              }
              valueColor="text-cyan-400"
            />

          </div>


          {/* ================= ADMIN / OPERATOR ACTIONS ================= */}

          {(role === 'Admin' ||
            role === 'Operator' ||
            role === 'Traffic Operator') && (

            <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-2xl flex items-center justify-between">

              <div className="flex items-center gap-2">

                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>

                <span className="text-sm font-semibold text-gray-200">
                  Control Panel Actions Available for{' '}
                  {role === 'Admin'
                    ? 'Admins'
                    : 'Operators'}
                </span>

              </div>

              <div className="flex items-center gap-3">

                <Link
                  href="/incidents"
                  className="bg-[#00d2ff] hover:bg-[#00b8e6] text-black font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-all"
                >
                  <PlusCircle size={15} />
                  + Log Incident
                </Link>

                {role === 'Admin' && (

                  <Link
                    href="/users"
                    className="bg-[#a855f7] hover:bg-[#9333ea] text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-all"
                  >
                    <Users size={15} />
                    Manage System Users
                  </Link>

                )}

              </div>

            </div>

          )}


          {/* ================= AI TRAFFIC PREDICTION ================= */}

          <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl">

            <div className="flex items-center justify-between mb-5">

              <div className="flex items-center gap-2">

                <Radio
                  size={18}
                  className="text-[#1f6feb]"
                />

                <div>

                  <h2 className="text-lg font-bold text-white">
                    AI Traffic Prediction
                  </h2>

                  <p className="text-xs text-gray-400 mt-1">
                    Forecasted traffic conditions from the
                    latest route analysis.
                  </p>

                </div>

              </div>

              <span className="bg-[#1f6feb]/20 text-[#58a6ff] text-xs px-3 py-1 rounded-full border border-[#1f6feb]/40">
                Live AI Prediction
              </span>

            </div>


            {/* Connected Route */}

            {routeAnalysis && (

              <div className="mb-4 bg-[#0d1117] border border-[#30363d] rounded-xl p-3">

                <p className="text-[10px] uppercase text-gray-500">
                  Based on latest route analysis
                </p>

                <p className="text-sm font-semibold text-white mt-1">

                  {routeAnalysis.origin}

                  <span className="text-cyan-400 mx-2">
                    â†’
                  </span>

                  {routeAnalysis.destination}

                </p>

              </div>

            )}


            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

              {/* Current Prediction */}

              <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">

                <p className="text-xs text-gray-400 uppercase font-bold">
                  Current Prediction
                </p>

                <p
                  className={`text-xl font-bold mt-2 ${getTrafficColor(
                    currentPrediction?.traffic
                  )}`}
                >
                  {currentPrediction?.traffic || (apiCongestion === 'LOW' ? 'Low' : apiCongestion === 'MEDIUM' ? 'Moderate' : apiCongestion === 'HIGH' ? 'Heavy' : 'Unavailable')}
                  {' Traffic'}
                </p>

                <p className="text-xs text-gray-500 mt-1">
                  Expected around{' '}
                  {currentPrediction?.time || (apiCongestion ? 'Latest backend prediction' : 'Prediction unavailable')}
                </p>

              </div>


              {/* Peak Traffic */}

              <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">

                <p className="text-xs text-gray-400 uppercase font-bold">
                  Peak Traffic
                </p>

                <p
                  className={`text-xl font-bold mt-2 ${getTrafficColor(
                    peakPrediction?.traffic
                  )}`}
                >
                  {peakPrediction?.traffic || (apiCongestion === 'LOW' ? 'Low' : apiCongestion === 'MEDIUM' ? 'Moderate' : apiCongestion === 'HIGH' ? 'Heavy' : 'Unavailable')}
                </p>

                <p className="text-xs text-gray-500 mt-1">
                  Expected around{' '}
                  {peakPrediction?.time || (apiPeakWindows.length ? apiPeakWindows.map(window => `${window.start}-${window.end}`).join('  ') : 'Peak hours unavailable')}
                </p>

              </div>


              {/* {peakPrediction ? 'Maximum Congestion' : 'Model Confidence'} */}

              <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">

                <p className="text-xs text-gray-400 uppercase font-bold">
                  {peakPrediction ? 'Maximum Congestion' : 'Model Confidence'}
                </p>

                <p className="text-xl font-bold text-orange-400 mt-2">
                  {peakPrediction ? `${peakPrediction.congestion}%` : apiConfidence !== null ? `${Math.round(apiConfidence * 100)}%` : 'Unavailable'}
                </p>

                <p className="text-xs text-gray-500 mt-1">
                  {peakPrediction ? 'Predicted peak from route analysis' : 'Backend model confidence'}
                </p>

              </div>

            </div>


            {/* Hourly Prediction */}

            {predictionData.length > 0 && (

              <div className="mt-6">

                <div className="flex justify-between items-center mb-3">

                  <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Hourly Forecast
                  </p>

                  <span className="text-[10px] text-gray-500">
                    Next {predictionData.length} hours
                  </span>

                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">

                  {predictionData.map((prediction) => (

                    <div
                      key={prediction.time}
                      className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4 hover:border-[#58a6ff] transition"
                    >

                      <p className="text-xs font-semibold text-gray-400">
                        {prediction.time}
                      </p>

                      <p
                        className={`text-sm font-semibold mt-3 ${getTrafficColor(
                          prediction.traffic
                        )}`}
                      >
                        {prediction.traffic}
                      </p>

                      <p className="text-[10px] text-gray-500 uppercase mt-3">
                        Travel Time
                      </p>

                      <p className="text-lg font-bold text-white">
                        {prediction.travelTime} min
                      </p>

                      <p className="text-[10px] text-gray-500 uppercase mt-2">
                        Congestion
                      </p>

                      <p className="text-sm font-semibold text-white">
                        {prediction.congestion}%
                      </p>

                    </div>

                  ))}

                </div>

              </div>

            )}


            {/* Peak Alert */}

            {peakPrediction && peakPrediction.congestion >= 70 && (

              <div className="mt-6 bg-red-500/10 border border-red-500/30 rounded-xl p-4">

                <div className="flex items-start gap-3">

                  <AlertTriangle
                    size={18}
                    className="text-red-400 mt-0.5"
                  />

                  <div>

                    <p className="text-sm font-semibold text-red-400">
                      Peak Congestion Expected
                    </p>

                    <p className="text-xs text-gray-300 mt-1">
                      Heavy traffic is predicted around{' '}
                      {peakPrediction.time}. Consider using
                      the alternative route to reduce travel
                      delay.
                    </p>

                  </div>

                </div>

              </div>

            )}


            {/* View Detailed Prediction */}

            <div className="flex justify-end mt-5">

              <Link
                href="/route-analysis"
                className="flex items-center gap-2 bg-[#1f6feb] hover:bg-[#388bfd] px-4 py-2 rounded-xl text-sm font-semibold transition-all"
              >
                View Detailed Prediction
                <ArrowRight size={15} />
              </Link>

            </div>

          </div>


          {/* ================= LATEST ROUTE ANALYSIS ================= */}

          <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl">

            <div className="flex items-center justify-between mb-5">

              <div className="flex items-center gap-2">

                <Route
                  size={18}
                  className="text-[#58a6ff]"
                />

                <div>

                  <h2 className="text-lg font-bold text-white">
                    Latest Route Analysis
                  </h2>

                  <p className="text-xs text-gray-400 mt-1">
                    Latest route selected by the user.
                  </p>

                </div>

              </div>

              <Link
                href="/route-analysis"
                className="text-xs text-[#58a6ff] hover:underline"
              >
                Open Route Analysis
              </Link>

            </div>


            {!routeAnalysis ? (

              /* No route analyzed yet */

              <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-8 text-center">

                <Route
                  size={32}
                  className="mx-auto text-gray-600 mb-3"
                />

                <p className="font-semibold text-gray-300">
                  No route analysis available yet
                </p>

                <p className="text-xs text-gray-500 mt-1">
                  Enter an origin and destination to
                  analyze a route.
                </p>

                <Link
                  href="/route-analysis"
                  className="inline-flex items-center gap-2 mt-4 bg-[#1f6feb] hover:bg-[#388bfd] px-4 py-2 rounded-xl text-sm font-semibold"
                >
                  Analyze Route
                  <ArrowRight size={15} />
                </Link>

              </div>

            ) : (

              <div className="space-y-4">

                {/* Origin â†’ Destination */}

                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-5">

                  <p className="text-[10px] text-gray-500 uppercase tracking-wider">
                    Analyzed Route
                  </p>

                  <div className="flex items-center gap-3 mt-2 flex-wrap">

                    <p className="text-lg font-bold text-white">
                      {routeAnalysis.origin}
                    </p>

                    <ArrowRight
                      size={20}
                      className="text-cyan-400"
                    />

                    <p className="text-lg font-bold text-white">
                      {routeAnalysis.destination}
                    </p>

                  </div>

                </div>


                {/* Selected Route */}

                {selectedRoute && (

                  <div
                    className={`border rounded-xl p-5 ${getTrafficBackground(
                      selectedRoute.trafficLevel
                    )}`}
                  >

                    <div className="flex justify-between items-start gap-4">

                      <div>

                        <p className="text-[10px] uppercase text-gray-500">
                          Selected Optimal Route
                        </p>

                        <h3 className="text-base font-bold text-white mt-1">
                          {selectedRoute.name}
                        </h3>

                      </div>

                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded-full ${getTrafficColor(
                          selectedRoute.trafficLevel
                        )}`}
                      >
                        {selectedRoute.trafficLevel}{' '}
                        Traffic
                      </span>

                    </div>


                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5">

                      {/* Distance */}

                      <div>

                        <p className="text-[10px] text-gray-500 uppercase">
                          Distance
                        </p>

                        <p className="text-sm font-bold text-white mt-1">
                          {selectedRoute.distance_km} km
                        </p>

                      </div>


                      {/* Travel Time */}

                      <div className="flex gap-2">

                        <Clock
                          size={15}
                          className="text-cyan-400 mt-1"
                        />

                        <div>

                          <p className="text-[10px] text-gray-500 uppercase">
                            Travel Time
                          </p>

                          <p className="text-sm font-bold text-white mt-1">
                            {selectedRoute.estimated_minutes}{' '}
                            mins
                          </p>

                        </div>

                      </div>


                      {/* Delay */}

                      <div>

                        <p className="text-[10px] text-gray-500 uppercase">
                          Expected Delay
                        </p>

                        <p className="text-sm font-bold text-amber-400 mt-1">
                          +{selectedRoute.estimatedDelay}{' '}
                          mins
                        </p>

                      </div>


                      {/* Road Condition */}

                      <div>

                        <p className="text-[10px] text-gray-500 uppercase">
                          Road Condition
                        </p>

                        <p
                          className={`text-sm font-bold mt-1 ${
                            selectedRoute.roadCondition ===
                            'Clear'
                              ? 'text-emerald-400'
                              : selectedRoute.roadCondition ===
                                'Road Work'
                              ? 'text-amber-400'
                              : 'text-red-400'
                          }`}
                        >
                          {selectedRoute.roadCondition}
                        </p>

                      </div>

                    </div>


                    {/* Hazard Information */}

                    <div className="flex items-start gap-2 mt-5 text-xs">

                      <AlertTriangle
                        size={15}
                        className="text-amber-400 mt-0.5"
                      />

                      <span className="text-gray-300">
                        {selectedRoute.hazardInfo}
                      </span>

                    </div>

                  </div>

                )}


                {/* Alternative Route */}

                {alternativeRoute && (

                  <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">

                    <div className="flex items-center justify-between gap-4">

                      <div>

                        <p className="text-[10px] uppercase text-gray-500">
                          Alternative Route
                        </p>

                        <p className="text-sm font-semibold text-white mt-1">
                          {alternativeRoute.name}
                        </p>

                      </div>

                      <span
                        className={`text-xs font-semibold ${getTrafficColor(
                          alternativeRoute.trafficLevel
                        )}`}
                      >
                        {alternativeRoute.trafficLevel}{' '}
                        Traffic
                      </span>

                    </div>

                    <div className="flex gap-5 mt-3 text-xs text-gray-400 flex-wrap">

                      <span>
                        {alternativeRoute.distance_km} km
                      </span>

                      <span>
                        {alternativeRoute.estimated_minutes}{' '}
                        mins
                      </span>

                      <span>
                        {alternativeRoute.roadCondition}
                      </span>

                    </div>

                  </div>

                )}


                {/* Open Route Analysis */}

                <div className="flex justify-end">

                  <Link
                    href="/route-analysis"
                    className="flex items-center gap-2 text-sm text-[#58a6ff] hover:underline"
                  >
                    View Full Route Analysis
                    <ArrowRight size={15} />
                  </Link>

                </div>

              </div>

            )}

          </div>


          {/* ================= PUBLIC ROLE: TRAVEL ROUTES ================= */}

          {role === 'Public' && (

            <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl space-y-4">

              <div className="flex items-center gap-2">

                <Navigation
                  size={18}
                  className="text-[#58a6ff]"
                />

                <div>

                  <h2 className="text-lg font-bold text-white">
                    Recommended Travel Routes
                  </h2>

                  <p className="text-xs text-gray-400 mt-1">
                    Recommendations based on the latest
                    route analysis.
                  </p>

                </div>

              </div>


              {routeAnalysis && selectedRoute ? (

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                  {/* Selected Route */}

                  <div
                    className={`p-4 rounded-xl border ${getTrafficBackground(
                      selectedRoute.trafficLevel
                    )}`}
                  >

                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Selected Route
                    </span>

                    <h4 className="font-bold text-white text-sm mt-3">
                      {selectedRoute.name}
                    </h4>

                    <p className="text-xs text-gray-400 mt-2">
                      {selectedRoute.distance_km} km Â·{' '}
                      {selectedRoute.estimated_minutes}{' '}
                      mins Â·{' '}
                      {selectedRoute.trafficLevel} Traffic
                    </p>

                  </div>


                  {/* Alternative Route */}

                  {alternativeRoute ? (

                    <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">

                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                        Alternative
                      </span>

                      <h4 className="font-bold text-white text-sm mt-3">
                        {alternativeRoute.name}
                      </h4>

                      <p className="text-xs text-gray-400 mt-2">
                        {alternativeRoute.distance_km} km Â·{' '}
                        {alternativeRoute.estimated_minutes}{' '}
                        mins Â·{' '}
                        {alternativeRoute.trafficLevel}{' '}
                        Traffic
                      </p>

                    </div>

                  ) : (

                    <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">

                      <span className="text-xs text-gray-500">
                        No alternative route available.
                      </span>

                    </div>

                  )}

                </div>

              ) : (

                <div className="bg-[#0d1117] p-6 rounded-xl border border-[#30363d] text-center">

                  <p className="text-sm font-semibold text-gray-300">
                    No route recommendations available yet.
                  </p>

                  <p className="text-xs text-gray-500 mt-1">
                    Analyze a route to see connected travel
                    recommendations.
                  </p>

                  <Link
                    href="/route-analysis"
                    className="inline-flex items-center gap-2 mt-4 bg-[#1f6feb] hover:bg-[#388bfd] px-4 py-2 rounded-xl text-sm font-semibold"
                  >
                    Find a Route
                    <ArrowRight size={15} />
                  </Link>

                </div>

              )}

            </div>

          )}

        </div>

      </main>

    </div>
  );
}
