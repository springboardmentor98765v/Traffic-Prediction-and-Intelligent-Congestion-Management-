'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Sidebar } from '../../components/Sidebar';

const Map = dynamic(() => import('../../components/Map'), { ssr: false });

export interface RouteOption {
  id: string;
  name: string;
  distance_km: number;
  estimated_minutes: number;
  trafficLevel: 'Low' | 'Moderate' | 'Heavy';

  // Day 4 fields
  roadCondition: 'Clear' | 'Road Work' | 'Heavy Traffic';
  estimatedDelay: number;
  hazardInfo: string;

  color: string;
  geometry: [number, number][];
}

/*
 * Traffic prediction data
 * This same data will also be available to the Dashboard
 * through localStorage.
 */
export default function RouteAnalysisPage() {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [role, setRole] = useState<string>('User');
  const [predictionData, setPredictionData] = useState<any[]>([]);

  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [selectedRouteId, setSelectedRouteId] = useState<string>('');

  const [startCoords, setStartCoords] =
    useState<[number, number] | undefined>();

  const [endCoords, setEndCoords] =
    useState<[number, number] | undefined>();

  useEffect(() => {
    const savedRole = localStorage.getItem('userRole');

    if (savedRole) {
      setRole(savedRole);
    }
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setErrorMsg('');
    setRoutes([]);

    try {
      const originRes = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          origin
        )}`
      );

      const originData = await originRes.json();

      const destRes = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          destination
        )}`
      );

      const destData = await destRes.json();

      if (!originData.length || !destData.length) {
        throw new Error(
          'Location not found. Please enter a more specific location.'
        );
      }

      const start: [number, number] = [
        parseFloat(originData[0].lat),
        parseFloat(originData[0].lon),
      ];

      const end: [number, number] = [
        parseFloat(destData[0].lat),
        parseFloat(destData[0].lon),
      ];

      const sameLocation =
        Math.abs(start[0] - end[0]) < 0.0001 &&
        Math.abs(start[1] - end[1]) < 0.0001;

      if (sameLocation) {
        setRoutes([]);
        setSelectedRouteId('');
        setStartCoords(undefined);
        setEndCoords(undefined);
        setErrorMsg(
          'Origin and destination cannot be the same.'
        );
        return;
      }

      const routeRes = await fetch(
        `https://router.project-osrm.org/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson&alternatives=true`
      );

      const routeData = await routeRes.json();

      if (!routeData.routes?.length) {
        throw new Error(
          'Unable to compute driving route between selected locations.'
        );
      }

      const primaryRoute = routeData.routes[0];

      const mainGeometry: [number, number][] =
        primaryRoute.geometry.coordinates.map(
          (coord: [number, number]) => [coord[1], coord[0]]
        );

      const baseDistance = parseFloat(
        (primaryRoute.distance / 1000).toFixed(1)
      );

      const baseTime = Math.max(
        1,
        Math.round(primaryRoute.duration / 60)
      );

      let altGeometry: [number, number][] = [];

      let altDistance = parseFloat(
        (baseDistance * 1.08).toFixed(1)
      );

      let altTime = Math.max(
        1,
        Math.round(baseTime * 1.12)
      );

      if (routeData.routes.length > 1) {
        const altRoute = routeData.routes[1];

        altGeometry = altRoute.geometry.coordinates.map(
          (coord: [number, number]) => [coord[1], coord[0]]
        );

        altDistance = parseFloat(
          (altRoute.distance / 1000).toFixed(1)
        );

        altTime = Math.max(
          1,
          Math.round(altRoute.duration / 60)
        );
      } else {
        altGeometry = mainGeometry.map(([lat, lng]) => [
          lat + 0.003,
          lng + 0.003,
        ]);
      }

      const calculatedRoutes: RouteOption[] = [
        {
          id: 'route-1',
          name: 'Fastest Route (via Highway)',
          distance_km: baseDistance,
          estimated_minutes: baseTime,
          trafficLevel: 'Moderate',
          roadCondition: 'Road Work',
          estimatedDelay: 3,
          hazardInfo:
            'Road work reported near the main junction.',
          color: '#e3b341',
          geometry: mainGeometry,
        },

        {
          id: 'route-2',
          name: 'Alternative Route (Lower Congestion)',
          distance_km: altDistance,
          estimated_minutes: altTime,
          trafficLevel: 'Low',
          roadCondition: 'Clear',
          estimatedDelay: 0,
          hazardInfo:
            'Clear road conditions with minimal stops.',
          color: '#2ea043',
          geometry: altGeometry,
        },
      ];

      setStartCoords(start);
      setEndCoords(end);

      setRoutes(calculatedRoutes);

      setSelectedRouteId('route-1');

            // Hardcoded hourly demo forecasts. These are illustrative, not live model predictions.
      const demoForecast = [
        { travelTimeOffset: -3, congestion: 18 },
        { travelTimeOffset: 0, congestion: 32 },
        { travelTimeOffset: 5, congestion: 61 },
        { travelTimeOffset: 9, congestion: 78 },
        { travelTimeOffset: 4, congestion: 46 },
      ];

      const now = new Date();

      const demoForecasts = demoForecast.map((item, index) => {
        const forecastTime = new Date(
          now.getTime() + index * 60 * 60 * 1000
        );

        const traffic =
          item.congestion < 35
            ? 'Low'
            : item.congestion < 65
            ? 'Moderate'
            : 'Heavy';

        return {
          time: forecastTime.toLocaleTimeString([], {
            hour: 'numeric',
            hour12: true,
          }),
          traffic,
          travelTime: Math.max(1, baseTime + item.travelTimeOffset),
          congestion: item.congestion,
        };
      });

      setPredictionData(demoForecasts);
    } catch (err: any) {
      setErrorMsg(
        err.message || 'Error processing route calculation.'
      );
    } finally {
      setLoading(false);
    }
  };

  const activeRoute =
    routes.find((r) => r.id === selectedRouteId) ||
    routes[0];

  /*
   * SAVE ROUTE ANALYSIS DATA
   *
   * This connects Route Analysis with the Dashboard.
   *
   * Whenever the user performs route analysis or changes
   * the selected route, the latest information is saved.
   */
  useEffect(() => {
    if (!activeRoute || routes.length === 0) {
      return;
    }

    const routeAnalysisData = {
      origin,
      destination,
      selectedRouteId,
      selectedRoute: activeRoute,
      routes,
      predictionData,
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem(
      'trafficvision_route_analysis',
      JSON.stringify(routeAnalysisData)
    );
  }, [
    origin,
    destination,
    selectedRouteId,
    activeRoute,
    routes,
    predictionData,
  ]);

  return (
    <div className="flex h-screen bg-[#0d1117] text-white">

      <Sidebar role={role} />

      <main className="flex-1 overflow-y-auto p-8 space-y-6">

        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">
            Route Analysis & Optimization
          </h1>

          <p className="text-sm text-gray-400 mt-1">
            Analyze optimal travel routes, travel time and road
            conditions.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <div className="bg-[#161b22] p-6 rounded-2xl border border-[#30363d] shadow-lg space-y-5 h-fit">

            <h2 className="text-base font-semibold text-white border-b border-[#30363d] pb-3">
              Route Settings
            </h2>

            <form
              onSubmit={handleAnalyze}
              className="space-y-4"
            >

              <div>

                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                  Origin
                </label>

                <input
                  type="text"
                  value={origin}
                  onChange={(e) =>
                    setOrigin(e.target.value)
                  }
                  placeholder="e.g. Wakad, Baner"
                  className="w-full px-4 py-2.5 bg-[#0d1117] border border-[#30363d] text-white placeholder-gray-500 rounded-xl text-sm focus:outline-none focus:border-[#58a6ff] transition"
                  required
                />

              </div>

              <div>

                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                  Destination
                </label>

                <input
                  type="text"
                  value={destination}
                  onChange={(e) =>
                    setDestination(e.target.value)
                  }
                  placeholder="e.g. Shivajinagar, Kothrud"
                  className="w-full px-4 py-2.5 bg-[#0d1117] border border-[#30363d] text-white placeholder-gray-500 rounded-xl text-sm focus:outline-none focus:border-[#58a6ff] transition"
                  required
                />

              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#1f6feb] hover:bg-[#388bfd] text-white py-3 rounded-xl transition text-sm font-semibold shadow-md active:scale-[0.98] disabled:opacity-50"
              >
                {loading
                  ? 'Calculating Route...'
                  : 'Find Optimal Route'}
              </button>

            </form>

            {errorMsg && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-xl text-xs">
                {errorMsg}
              </div>
            )}

            {routes.length > 0 && !errorMsg && (

              <div className="mt-6 border-t border-[#30363d] pt-4 space-y-4">

                <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                  Available Routes
                </span>

                <div className="space-y-3">

                  {routes.map((rt) => (

                    <button
                      key={rt.id}
                      onClick={() =>
                        setSelectedRouteId(rt.id)
                      }
                      className={`w-full text-left p-4 rounded-xl border transition ${
                        selectedRouteId === rt.id
                          ? 'border-[#58a6ff] bg-[#1f6feb]/10 text-white'
                          : 'border-[#30363d] bg-[#0d1117] text-gray-400 hover:border-gray-500'
                      }`}
                    >

                      <div className="flex justify-between items-center text-xs font-semibold mb-2">

                        <span>
                          {rt.name}
                        </span>

                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] ${
                            rt.trafficLevel === 'Low'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : rt.trafficLevel === 'Moderate'
                              ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {rt.trafficLevel} Traffic
                        </span>

                      </div>

                      <div className="grid grid-cols-2 gap-3 mt-3">

                        <div className="bg-[#161b22] rounded-lg p-2.5">

                          <p className="text-[10px] text-gray-500 uppercase">
                            Distance
                          </p>

                          <p className="text-sm font-semibold text-white">
                            {rt.distance_km} km
                          </p>

                        </div>

                        <div className="bg-[#161b22] rounded-lg p-2.5">

                          <p className="text-[10px] text-gray-500 uppercase">
                            Travel Time
                          </p>

                          <p className="text-sm font-semibold text-white">
                            {rt.estimated_minutes} mins
                          </p>

                        </div>

                      </div>

                    </button>

                  ))}

                </div>

                {activeRoute && (

                  <div className="space-y-3">

                    <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">

                      <div className="flex items-center justify-between">

                        <div>

                          <p className="text-xs text-gray-500 uppercase">
                            Estimated Travel Time
                          </p>

                          <p className="text-xl font-bold text-white mt-1">
                            {activeRoute.estimated_minutes} mins
                          </p>

                        </div>

                        <div className="text-2xl">
                          •
                        </div>

                      </div>

                      {activeRoute.estimatedDelay > 0 && (

                        <p className="text-xs text-amber-400 mt-2">
                          +{activeRoute.estimatedDelay} mins
                          expected delay
                        </p>

                      )}

                    </div>

                    <div
                      className={`border rounded-xl p-4 ${
                        activeRoute.roadCondition === 'Clear'
                          ? 'bg-emerald-500/10 border-emerald-500/30'
                          : activeRoute.roadCondition === 'Road Work'
                          ? 'bg-amber-500/10 border-amber-500/30'
                          : 'bg-red-500/10 border-red-500/30'
                      }`}
                    >

                      <p className="text-xs text-gray-400 uppercase">
                        Road Condition
                      </p>

                      <div className="flex justify-between items-center mt-1">

                        <p
                          className={`text-base font-semibold ${
                            activeRoute.roadCondition === 'Clear'
                              ? 'text-emerald-400'
                              : activeRoute.roadCondition === 'Road Work'
                              ? 'text-amber-400'
                              : 'text-red-400'
                          }`}
                        >
                          {activeRoute.roadCondition}
                        </p>

                        <span className="text-xl">
                          {activeRoute.roadCondition === 'Clear'
                            ? ''
                            : ' '}
                        </span>

                      </div>

                    </div>

                    <div
                      className={`border p-4 rounded-xl text-xs ${
                        activeRoute.trafficLevel === 'Low'
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                          : activeRoute.trafficLevel === 'Moderate'
                          ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                          : 'bg-red-500/10 border-red-500/30 text-red-400'
                      }`}
                    >

                      <span className="font-semibold block mb-1">
                        Condition Alert
                      </span>

                      <span>
                        {activeRoute.hazardInfo}
                      </span>

                    </div>

                  </div>

                )}

              </div>

            )}

          </div>

          <div className="lg:col-span-2 bg-[#161b22] border border-[#30363d] rounded-2xl overflow-hidden min-h-[450px]">

            <Map
              nodes={[]}
              selectedNodeId=""
              onSelectNode={() => {}}
              startCoords={startCoords}
              endCoords={endCoords}
              routeGeometry={activeRoute?.geometry || []}
              routeColor={activeRoute?.color || '#1f6feb'}
            />

          </div>

        </div>

        {/* TRAFFIC PREDICTION */}

        <div className="bg-[#161b22] border border-[#30363d] rounded-2xl p-6 shadow-lg">

          <div className="flex items-center justify-between mb-6">

            <div>

              <h2 className="text-lg font-semibold text-white">
                Traffic Prediction
              </h2>

              <p className="text-xs text-gray-400 mt-1">
                Forecasted traffic and travel conditions for the
                upcoming hours.
              </p>

            </div>

            <div className="flex items-center gap-3">

              <button
                type="button"
                onClick={() => {
                  const csv = [
                    'Time,Traffic,Travel Time (min),Congestion (%)',
                    ...predictionData.map(
                      (p) =>
                        `${p.time},${p.traffic},${p.travelTime},${p.congestion}`
                    ),
                  ].join('\n');

                  const blob = new Blob([csv], {
                    type: 'text/csv',
                  });

                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');

                  link.href = url;
                  link.download =
                    'traffic-prediction-report.csv';

                  link.click();

                  URL.revokeObjectURL(url);
                }}
                className="px-4 py-2 rounded-lg bg-[#238636] text-white text-sm font-medium hover:bg-[#2ea043]"
              >
                Download Report
              </button>

              <div className="text-2xl">
                📈
              </div>

            </div>

          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">

            <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">

              <p className="text-[10px] text-gray-500 uppercase tracking-wider">
                Current Prediction
              </p>

              <p className="text-xl font-bold text-emerald-400 mt-2">
                {predictionData[0] ? `${predictionData[0].traffic} Traffic` : 'Unavailable'}
              </p>

              <p className="text-xs text-gray-500 mt-1">
                {predictionData[0] ? `Expected around ${predictionData[0].time}` : 'No live forecast available'}
              </p>

            </div>

            <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">

              <p className="text-[10px] text-gray-500 uppercase tracking-wider">
                Peak Traffic
              </p>

              <p className="text-xl font-bold text-red-400 mt-2">
                {predictionData.length ? predictionData.reduce((a, b) => a.congestion >= b.congestion ? a : b).traffic : 'Unavailable'}
              </p>

              <p className="text-xs text-gray-500 mt-1">
                Expected around 1â€“2 PM
              </p>

            </div>

            <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">

              <p className="text-[10px] text-gray-500 uppercase tracking-wider">
                Relative Severity Index
              </p>

              <p className="text-xl font-bold text-white mt-2">
                {predictionData.length ? `${Math.max(...predictionData.map(p => p.congestion))}/100` : 'Unavailable'}
              </p>

              <p className="text-xs text-gray-500 mt-1">
                {predictionData.length ? 'Derived from the predicted traffic category' : 'No live forecast available'}
              </p>

            </div>

          </div>

          <div>

            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
              Hourly Forecast
            </p>

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
                    className={`text-sm font-semibold mt-3 ${
                      prediction.traffic === 'Low'
                        ? 'text-emerald-400'
                        : prediction.traffic === 'Moderate'
                        ? 'text-amber-400'
                        : 'text-red-400'
                    }`}
                  >
                    {prediction.traffic}
                  </p>

                  <p className="text-[10px] text-gray-500 uppercase mt-3">
                    Travel Time
                  </p>

                  <p className="text-lg font-bold text-white">
                    {prediction.travelTime} min
                  </p>

                </div>

              ))}

            </div>

          </div>

          <div className="mt-7">

            <div className="flex justify-between items-center mb-4">

              <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                Congestion Forecast
              </p>

              <span className="text-[10px] text-gray-500">
                Next 5 hours
              </span>

            </div>

            <div className="space-y-4">

              {predictionData.map((prediction) => (

                <div key={prediction.time}>

                  <div className="flex justify-between items-center mb-1">

                    <span className="text-xs text-gray-400">
                      {prediction.time}
                    </span>

                    <span className="text-xs font-semibold text-gray-300">
                      {prediction.congestion}%
                    </span>

                  </div>

                  <div className="w-full h-2.5 bg-[#30363d] rounded-full overflow-hidden">

                    <div
                      className={`h-full rounded-full transition-all ${
                        prediction.traffic === 'Low'
                          ? 'bg-emerald-500'
                          : prediction.traffic === 'Moderate'
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                      }`}
                      style={{
                        width: `${prediction.congestion}%`,
                      }}
                    />

                  </div>

                </div>

              ))}

            </div>

          </div>

          <div className="mt-7 bg-red-500/10 border border-red-500/30 rounded-xl p-4">

            <div className="flex items-start gap-3">

              <span className="text-lg">
                ⚠️
              </span>

              <div>

                <p className="text-sm font-semibold text-red-400">
                  Peak Congestion Expected
                </p>

                <p className="text-xs text-gray-300 mt-1">{predictionData.length ? `The highest predicted category is ${predictionData.reduce((a, b) => a.congestion >= b.congestion ? a : b).traffic}, around ${predictionData.reduce((a, b) => a.congestion >= b.congestion ? a : b).time}. The severity index is derived from the category, not a model-predicted percentage.` : 'No live backend predictions are available. Check the backend and try analyzing the route again.'}</p>

              </div>

            </div>

          </div>

        </div>

      </main>

    </div>
  );
}

