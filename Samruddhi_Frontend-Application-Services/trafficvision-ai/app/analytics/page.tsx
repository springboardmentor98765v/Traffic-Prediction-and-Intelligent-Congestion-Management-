'use client';

import { useEffect, useMemo, useState } from 'react';

import {

  Search,

  Download,

  RefreshCw,

  TrendingUp,

  Sparkles,

} from 'lucide-react';

import { Sidebar } from '../../components/Sidebar';

const roads = [

  'R001 - Anna Salai',

  'R002 - Mount Road',

  'R003 - GST Road',

];

const baseRecommendations = [

  ['HIGH', 'Dynamic Green-Wave Signal Offset', 'R001 - Anna Salai', '94%', '+12% throughput', '8 min saved'],

  ['MED', 'Heavy Freight Transit Lane Balancing', 'R002 - Mount Road', '88%', '+7% throughput', '5 min saved'],

  ['LOW', 'Dynamic Variable Speed Harmonics', 'R003 - GST Road', '82%', '+4% throughput', '3 min saved'],

];

const metrics = ['Density', 'Level'];

const trendData = {

  '24 Hours': {

    values: [28, 32, 25, 22, 30, 38, 48, 58, 65, 72, 68, 75, 82, 88, 76, 70, 62, 68, 80, 92, 85, 70, 55, 40],

    labels: ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM'],

  },

  '7 Days': {

    values: [45, 62, 78, 54, 88, 70, 58],

    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],

  },

  '1 Month': {

    values: [42, 55, 48, 65, 72, 60, 78, 82, 58, 64, 70, 76, 68, 85, 74, 62, 80, 88, 71, 66, 79, 83, 91, 75, 69, 84, 77, 89, 73, 81],

    labels: Array.from({ length: 30 }, (_, i) => String(i + 1)),

  },

};

type RangeType = keyof typeof trendData;

type MetricType = 'Density' | 'Speed' | 'Score' | 'Level';

type Recommendation = [string, string, string, string, string, string, string, string];

type BackendRecommendation = {

  priority: string;

  title: string;

  reason: string;

  suggested_action: string;

  road_id: number;

  road_name: string;

  basis: string;

};

type RecommendationResponse = {

  road_id: number;

  road_name: string;

  observed_level: string;

  observed_density: number | null;

  predicted_level: string | null;

  model_version: string | null;

  record_count: number;

  recommendations: BackendRecommendation[];

  generated_by: string;

  disclaimer: string;

};

type ModelEvaluationResponse = {

  road_id: number;

  status: string;

  message?: string;

  sample_count?: number;

  metrics?: {

    accuracy?: number;

    weighted_precision?: number;

    weighted_recall?: number;

    weighted_f1?: number;

  };

};

type TrafficRecord = {

  road_id?: number;

  timestamp: string;

  vehicle_count: number;

  density: number;

  average_speed_kmh?: number | null;

  congestion_level: string;

};

const API_BASE = 'http://127.0.0.1:8002/api/v1';

const densityPercent = (density: number) =>

  Math.max(0, Math.min(100, density <= 1 ? density * 100 : density));

export default function AnalyticsPage() {

  const [road, setRoad] = useState('');

  const [selectedRoad, setSelectedRoad] = useState(roads[0]);

  const [range, setRange] = useState<RangeType>('24 Hours');

  const [useCustomDates, setUseCustomDates] = useState(false);

  const [bucket, setBucket] = useState<'Hourly' | 'Daily'>('Hourly');

  const [metric, setMetric] = useState<MetricType>('Density');

  const [priority, setPriority] = useState('ALL');

  const [fromDate, setFromDate] = useState('2026-10-12');

  const [toDate, setToDate] = useState('2026-10-13');

  const [scanVersion, setScanVersion] = useState(0);

  const [isRescanning, setIsRescanning] = useState(false);

  const [selectedInsight, setSelectedInsight] = useState<Recommendation | null>(null);

  const [recommendationData, setRecommendationData] = useState<RecommendationResponse | null>(null);

  const [modelEvaluation, setModelEvaluation] = useState<ModelEvaluationResponse | null>(null);

  const [intelligenceError, setIntelligenceError] = useState("");

  const [trendRecords, setTrendRecords] = useState<TrafficRecord[]>([]);

  const [heatmapRecords, setHeatmapRecords] = useState<TrafficRecord[]>([]);

  const [congestionPrediction, setCongestionPrediction] = useState<{

    predicted_level: string;

    confidence: number | null;

    model_version: string;

  } | null>(null);

  const [peakWindows, setPeakWindows] = useState<{ start: string; end: string }[]>([]);

  const [delayPrediction, setDelayPrediction] = useState<{

    estimated_delay_minutes: number;

    confidence: number;

  } | null>(null);

  const [vehicleCountPrediction, setVehicleCountPrediction] = useState<{

    junction: number;

    prediction_time: string;

    predicted_vehicle_count: number;

    traffic_condition: string;

    model_version: string;

  } | null>(null);

  const [predictionError, setPredictionError] = useState('');

  const [analyticsError, setAnalyticsError] = useState('');

  const [isAnalyticsLoading, setIsAnalyticsLoading] = useState(false);

  const [refreshVersion, setRefreshVersion] = useState(0);

  const [sidebarRole, setSidebarRole] = useState('User');

  useEffect(() => {

    const savedRole = window.localStorage.getItem('userRole');

    if (savedRole) setSidebarRole(savedRole);

  }, []);

  useEffect(() => {

    let cancelled = false;

    const loadAnalytics = async () => {

      setIsAnalyticsLoading(true);

      setAnalyticsError('');

      try {

        const roadId = Math.max(1, roads.indexOf(selectedRoad) + 1);

        const apiRange = range === '7 Days' ? 'week' : range === '1 Month' ? 'month' : 'day';

        const [trendResponse, heatmapResponse] = await Promise.all([

          fetch(`${API_BASE}/analytics/trends?road_id=${roadId}&range=${apiRange}`),

          fetch(`${API_BASE}/analytics/heatmap?range=${apiRange}`),

        ]);

        if (!trendResponse.ok || !heatmapResponse.ok) {

          throw new Error(

            `Analytics API request failed (trends: ${trendResponse.status}, heatmap: ${heatmapResponse.status}).`

          );

        }

        const trendJson = await trendResponse.json();

        const heatmapJson = await heatmapResponse.json();

        if (!cancelled) {

          setTrendRecords(Array.isArray(trendJson.data) ? trendJson.data : []);

          setHeatmapRecords(

            Array.isArray(heatmapJson.data) ? heatmapJson.data : []

          );

        }

      } catch (error) {

        if (!cancelled) {

          setTrendRecords([]);

          setHeatmapRecords([]);

          setAnalyticsError(

            error instanceof Error ? error.message : 'Could not load analytics.'

          );

        }

      } finally {

        if (!cancelled) {

          setIsAnalyticsLoading(false);

          setIsRescanning(false);

        }

      }

    };

    void loadAnalytics();

    return () => {

      cancelled = true;

    };

  }, [selectedRoad, range, refreshVersion]);

  useEffect(() => {

    let cancelled = false;

    async function loadPredictions() {

      setPredictionError('');

      setCongestionPrediction(null);

      setPeakWindows([]);

      setDelayPrediction(null);

      const roadId = Math.max(1, roads.indexOf(selectedRoad) + 1);

      const predictionTime = new Date().toISOString().slice(0, 19);

      const requests = await Promise.allSettled([

        fetch(`${API_BASE}/predict/congestion?road_id=${roadId}&time=${encodeURIComponent(predictionTime)}`)

          .then(async (response) => {

            if (!response.ok) throw new Error(`Congestion prediction: HTTP ${response.status}`);

            return response.json();

          }),

        fetch(`${API_BASE}/predict/peak-hours?road_id=${roadId}`)

          .then(async (response) => {

            if (!response.ok) throw new Error(`Peak hours: HTTP ${response.status}`);

            return response.json();

          }),

        fetch(`${API_BASE}/predict/delay?road_id=${roadId}`)

          .then(async (response) => {

            if (!response.ok) throw new Error(`Delay estimate: HTTP ${response.status}`);

            return response.json();

          }),

        fetch(`${API_BASE}/predict/vehicle-count?junction=${roadId}&time=${encodeURIComponent(predictionTime)}`)

          .then(async (response) => {

            if (!response.ok) throw new Error(`Vehicle-count prediction: HTTP ${response.status}`);

            return response.json();

          }),

      ]);

      if (cancelled) return;

      const errors: string[] = [];

      if (requests[0].status === 'fulfilled') {

        setCongestionPrediction(requests[0].value);

      } else {

        errors.push('Congestion prediction unavailable');

      }

      if (requests[1].status === 'fulfilled') {

        setPeakWindows(Array.isArray(requests[1].value.peak_windows) ? requests[1].value.peak_windows : []);

      } else {

        errors.push('Peak-hour prediction unavailable');

      }

      if (requests[2].status === 'fulfilled') {

        setDelayPrediction(requests[2].value);

      } else {

        errors.push('Delay estimate unavailable');

      }

      if (requests[3].status === 'fulfilled') {

        setVehicleCountPrediction(requests[3].value);

      } else {

        errors.push('Dataset-based vehicle-count estimate unavailable');

      }

      if (errors.length) setPredictionError(errors.join('. ') + '.');

    }

    void loadPredictions();

    return () => {

      cancelled = true;

    };

  }, [selectedRoad, refreshVersion]);

  useEffect(() => {

    let cancelled = false;

    async function loadIntelligence() {

      const roadId = Math.max(1, roads.indexOf(selectedRoad) + 1);

      setIntelligenceError("");

      const token = localStorage.getItem("access_token");

if (!token) {

  setIntelligenceError("Please log in again.");

  return;

}

const headers = {

  Authorization: `Bearer ${token}`,

};

      const results = await Promise.allSettled([

        fetch(`${API_BASE}/analytics/recommendations?road_id=${roadId}`, { headers }).then(async (response) => {

          if (!response.ok) throw new Error(`Recommendations API returned ${response.status}`);

          return response.json() as Promise<RecommendationResponse>;

        }),

        fetch(`${API_BASE}/analytics/model-evaluation?road_id=${roadId}`, { headers }).then(async (response) => {

          if (!response.ok) throw new Error(`Model evaluation API returned ${response.status}`);

          return response.json() as Promise<ModelEvaluationResponse>;

        }),

      ]);

      if (cancelled) return;

      const errors: string[] = [];

      if (results[0].status === 'fulfilled') {

        setRecommendationData(results[0].value);

      } else {

        setRecommendationData(null);

        errors.push('Backend recommendations are unavailable');

      }

      if (results[1].status === 'fulfilled') {

        setModelEvaluation(results[1].value);

      } else {

        setModelEvaluation(null);

        errors.push('Model evaluation is unavailable');

      }

      if (errors.length) setIntelligenceError(errors.join('. ') + '.');

    }

    void loadIntelligence();

    return () => {

      cancelled = true;

    };

  }, [selectedRoad, refreshVersion]);

const aiRecommendations = useMemo<Recommendation[]>(() => {

    const items = recommendationData?.recommendations ?? [];

    return items.map((item) => {

      const level = item.priority.toUpperCase();

      const displayPriority = level === 'MEDIUM' ? 'MED' : level;

      const roadLabel = `R${String(item.road_id).padStart(3, '0')} - ${item.road_name}`;

      const density = recommendationData?.observed_density;

      return [

        displayPriority,

        item.title,

        roadLabel,

        'Rule-based engine',

        `Observed level: ${recommendationData?.observed_level ?? 'Unavailable'}`,

        density == null ? 'Density unavailable' : `Observed density: ${Math.round((density <= 1 ? density * 100 : density))}%`,

        item.reason,

        item.suggested_action,

      ] as Recommendation;

    });

  }, [recommendationData]);

  const filtered = useMemo(

    () => priority === 'ALL'

      ? aiRecommendations

      : aiRecommendations.filter((item) => item[0] === priority),

    [priority, aiRecommendations],

  );

  const matchingRoads = useMemo(() => {

    const query = road.trim().toLowerCase();

    if (!query) return [];

    return roads.filter((item) => item.toLowerCase().includes(query));

  }, [road]);

  const selectRoad = (roadName: string) => {

    setSelectedRoad(roadName);

    setRoad(roadName.replace(/^R\d+\s*-\s*/, ''));

  };

  const searchRoad = () => {

    if (matchingRoads.length > 0) selectRoad(matchingRoads[0]);

  };

  const rangeDays = useMemo(() => {

    const from = new Date(`${fromDate}T00:00:00`);

    const to = new Date(`${toDate}T00:00:00`);

    return Math.max(1, Math.floor((to.getTime() - from.getTime()) / 86400000) + 1);

  }, [fromDate, toDate]);

  const filteredTrendRecords = useMemo(() => {

    const validRecords = trendRecords.filter((record) =>

      Number.isFinite(new Date(record.timestamp).getTime()),

    );

    if (validRecords.length === 0) return [];

    if (useCustomDates) {

      return validRecords.filter((record) => {

        const date = record.timestamp.slice(0, 10);

        return date >= fromDate && date <= toDate;

      });

    }

    const latest = Math.max(...validRecords.map((record) =>

      new Date(record.timestamp).getTime(),

    ));

    const windowDays = range === '24 Hours' ? 1 : range === '7 Days' ? 7 : 30;

    const startTime = latest - windowDays * 24 * 60 * 60 * 1000;

    return validRecords.filter((record) => {

      const time = new Date(record.timestamp).getTime();

      return time >= startTime && time <= latest;

    });

  }, [trendRecords, fromDate, toDate, range, useCustomDates]);

  const filteredHeatmapRecords = useMemo(() => {

    const validRecords = heatmapRecords.filter((record) =>

      Number.isFinite(new Date(record.timestamp).getTime()),

    );

    if (validRecords.length === 0) return [];

    if (useCustomDates) {

      const startTime = new Date(`${fromDate}T00:00:00`).getTime();

      const endTime = new Date(`${toDate}T23:59:59.999`).getTime();

      return validRecords.filter((record) => {

        const time = new Date(record.timestamp).getTime();

        return time >= startTime && time <= endTime;

      });

    }

    const latest = Math.max(...validRecords.map((record) =>

      new Date(record.timestamp).getTime(),

    ));

    const windowDays = range === '24 Hours' ? 1 : range === '7 Days' ? 7 : 30;

    const startTime = latest - windowDays * 24 * 60 * 60 * 1000;

    return validRecords.filter((record) => {

      const time = new Date(record.timestamp).getTime();

      return time >= startTime && time <= latest;

    });

  }, [heatmapRecords, fromDate, toDate, range, useCustomDates]);

  const rangeSeed = useMemo(

    () => [...`${fromDate}${toDate}`].reduce((sum, char) => sum + char.charCodeAt(0), 0),

    [fromDate, toDate],

  );

  const heatmapSlots = useMemo(

    () =>

      [...new Set(filteredHeatmapRecords.map((record) => record.timestamp))]

        .sort()

        .slice(-12),

    [filteredHeatmapRecords],

  );

  const heatmapLabels = useMemo(

    () =>

      heatmapSlots.map((timestamp) => {

        const date = new Date(timestamp);

        return bucket === 'Hourly'

          ? date.toLocaleTimeString('en-IN', {

              hour: '2-digit',

              minute: '2-digit',

            })

          : date.toLocaleDateString('en-IN', {

              day: '2-digit',

              month: 'short',

            });

      }),

    [bucket, heatmapSlots],

  );

  const heat = (row: number, col: number) => {

    const timestamp = heatmapSlots[col];

    if (!timestamp) return 0;

    const record = filteredHeatmapRecords.find(

      (item) => item.road_id === row + 1 && item.timestamp === timestamp,

    );

    if (!record) return 0;

    if (metric === 'Density') return densityPercent(Number(record.density));

    if (metric === 'Level') {

      const level = String(record.congestion_level).toUpperCase();

      if (level.includes('HIGH') || level.includes('HEAVY')) return 85;

      if (level.includes('MEDIUM') || level.includes('MODERATE')) return 55;

      if (level.includes('LOW')) return 25;

      return 0;

    }

    // The current backend record does not provide speed or a separate score.

    return 0;

  };

  const getLevel = (value: number) => {

    if (value >= 70) return 'Heavy';

    if (value >= 45) return 'Moderate';

    return 'Low';

  };

  const getHeatColor = (value: number) => {

    if (value <= 0) return 'bg-gray-700';

    if (metric === 'Speed') {

      if (value < 40) return 'bg-red-500';

      if (value < 55) return 'bg-yellow-500';

      return 'bg-green-500';

    }

    if (value >= 70) return 'bg-red-500';

    if (value >= 45) return 'bg-yellow-500';

    return 'bg-green-500';

  };

  const roadAnalysis = useMemo(() => {

    const records = [...filteredTrendRecords].sort(

      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),

    );

    const densities = records.map((record) => densityPercent(Number(record.density)));

    const vehicleCounts = records.map((record) => Number(record.vehicle_count) || 0);

    const averageDensity = densities.length

      ? densities.reduce((sum, value) => sum + value, 0) / densities.length

      : 0;

    const maxDensity = densities.length ? Math.max(...densities) : 0;

    const vehicleCount = vehicleCounts.length

      ? vehicleCounts.reduce((sum, value) => sum + value, 0) / vehicleCounts.length

      : 0;

    const peakIndex = densities.indexOf(maxDensity);

    const peakRecord = peakIndex >= 0 ? records[peakIndex] : undefined;

    const peakCongestion = peakRecord

      ? new Date(peakRecord.timestamp).toLocaleTimeString('en-IN', {

          hour: '2-digit',

          minute: '2-digit',

        })

      : 'No data';

    return {

      vehicleCount,

      averageSpeed: 0,

      averageDensity,

      maxDensity,

      totalReadings: records.length,

      peakCongestion,

      congestionScore: Math.round(averageDensity),

    };

  }, [filteredTrendRecords]);

  const congestionLevel = getLevel(roadAnalysis.congestionScore);

  const congestionDistribution = useMemo(() => {

    const counts = { Low: 0, Moderate: 0, Heavy: 0 };

    for (const record of filteredTrendRecords) {

      const level = getLevel(densityPercent(Number(record.density)));

      counts[level] += 1;

    }

    const total = counts.Low + counts.Moderate + counts.Heavy;

    return {

      counts,

      total,

      lowPercent: total ? (counts.Low / total) * 100 : 0,

      moderatePercent: total ? (counts.Moderate / total) * 100 : 0,

      heavyPercent: total ? (counts.Heavy / total) * 100 : 0,

    };

  }, [filteredTrendRecords]);

  const handleFromDateChange = (value: string) => {

    setFromDate(value);

    setUseCustomDates(true);

    if (value > toDate) setToDate(value);

  };

  const handleToDateChange = (value: string) => {

    setToDate(value);

    setUseCustomDates(true);

    if (value < fromDate) setFromDate(value);

  };

  const downloadReport = async () => {

    try {

      const apiRange = range === '7 Days' ? 'week' : range === '1 Month' ? 'month' : 'day';

      const response = await fetch(

        `${API_BASE}/analytics/reports?range=${apiRange}&format=csv`,

      );

      if (!response.ok) {

        throw new Error(`Report request failed (${response.status}).`);

      }

      const blob = await response.blob();

      const url = URL.createObjectURL(blob);

      const anchor = document.createElement('a');

      anchor.href = url;

      anchor.download = `trafficvision-report-${apiRange}.csv`;

      document.body.appendChild(anchor);

      anchor.click();

      anchor.remove();

      URL.revokeObjectURL(url);

    } catch (error) {

      setAnalyticsError(

        error instanceof Error ? error.message : 'Could not download report.'

      );

    }

  };

  const rescanNetwork = () => {

    if (isRescanning || isAnalyticsLoading) return;

    setIsRescanning(true);

    setRefreshVersion((previous) => previous + 1);

  };

const speedReadings = filteredTrendRecords

  .filter(

    (record) =>

      record.average_speed_kmh != null &&

      Number.isFinite(Number(record.average_speed_kmh)) &&

      Number(record.average_speed_kmh) >= 0,

  )

  .map((record) => Number(record.average_speed_kmh));

const averageSpeedLabel =

  speedReadings.length > 0

    ? `${(

        speedReadings.reduce((sum, speed) => sum + speed, 0) /

        speedReadings.length

      ).toFixed(1)} km/h`

    : "Not available";

const currentTrend = useMemo(() => {

  const records = [...filteredTrendRecords].sort(

    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),

  );

  return {

    labels: records.map((record) => {

      const timestamp = new Date(record.timestamp);

      const timeLabel = timestamp.toLocaleTimeString('en-IN', {

        hour: '2-digit',

        minute: '2-digit',

      });

      if (range !== '24 Hours' && fromDate === toDate) return timeLabel;

      const dateLabel = timestamp.toLocaleDateString('en-IN', {

        day: '2-digit',

        month: 'short',

      });

      return `${dateLabel} ${timeLabel}`;

    }),

    values: records.map((record) =>

      Math.max(0, Number(record.vehicle_count) || 0),

    ),

    details: records.map((record) => ({

      density: densityPercent(Number(record.density)),

      congestion: record.congestion_level,

    })),

  };

}, [filteredTrendRecords, fromDate, toDate, range]);

const peakValue = currentTrend.values.length

    ? Math.max(...currentTrend.values)

    : 0;

  const peakLabel = currentTrend.values.length

    ? currentTrend.labels[currentTrend.values.indexOf(peakValue)]

    : 'No data';

  return (

    <div className="min-h-screen w-full overflow-x-hidden bg-[#060b16] text-white">

      <aside className="fixed left-0 top-0 z-50 hidden h-screen w-64 shrink-0 overflow-hidden border-r border-gray-800 bg-[#060b16] md:block">

        <div className="h-full w-64">

          <Sidebar role={sidebarRole} />

        </div>

      </aside>

      <main

        data-scroll-container

        className="h-screen min-h-0 w-full overflow-x-hidden overflow-y-auto bg-[#060b16] p-4 md:ml-64 md:w-[calc(100%-16rem)] md:p-6"

      >

        <div className="flex w-full flex-wrap items-start justify-between gap-4">

          <div>

            <h1 className="text-2xl font-bold">

              Traffic Intelligence &amp; Spatial Analytics

            </h1>

            <p className="mt-1 text-sm text-gray-500">

              Backend traffic trends, congestion metrics and illustrative road recommendations.

            </p>

          </div>

          <button

            type="button"

            onClick={downloadReport}

            className="flex items-center gap-2 rounded-lg bg-cyan-600 px-4 py-2 text-sm hover:bg-cyan-500"

          >

            <Download size={16} />

            Download Historical Report

          </button>

        </div>

        <div className="mt-5 flex flex-wrap gap-2">

          <div className="relative">

            <div className="flex rounded-lg border border-gray-700 bg-[#0c1424]">

              <input

                value={road}

                onChange={(event) => setRoad(event.target.value)}

                onKeyDown={(event) => {

                  if (event.key === 'Enter') searchRoad();

                }}

                placeholder="Search road..."

                className="w-52 bg-transparent px-3 py-2 text-sm outline-none"

              />

              <button

                type="button"

                onClick={searchRoad}

                aria-label="Search road"

                className="px-3 text-cyan-400 hover:text-cyan-300"

              >

                <Search size={17} />

              </button>

            </div>

            {road.trim() !== '' && (

              <div className="absolute left-0 top-full z-50 mt-1 w-full overflow-hidden rounded-lg border border-gray-700 bg-[#0c1424] shadow-xl">

                {matchingRoads.length > 0 ? (

                  matchingRoads.map((item) => (

                    <button

                      type="button"

                      key={item}

                      onClick={() => selectRoad(item)}

                      className={`block w-full px-3 py-2 text-left text-xs hover:bg-cyan-500/10 ${

                        item === selectedRoad ? 'bg-cyan-500/10 text-cyan-400' : 'text-gray-300'

                      }`}

                    >

                      {item}

                    </button>

                  ))

                ) : (

                  <div className="px-3 py-2 text-xs text-gray-500">No matching road</div>

                )}

              </div>

            )}

          </div>

          <select

            aria-label="Trend range"

            value={range}

            onChange={(event) => {
                setRange(event.target.value as RangeType);
                setUseCustomDates(false);
              }}

            className="rounded-lg border border-gray-700 bg-[#0c1424] px-3 text-sm"

          >

            <option>24 Hours</option>

            <option>7 Days</option>

            <option>1 Month</option>

          </select>

          <select

            aria-label="Select road"

            value={selectedRoad}

            onChange={(event) => selectRoad(event.target.value)}

            className="rounded-lg border border-gray-700 bg-[#0c1424] px-3 py-2 text-sm outline-none"

          >

            {roads.map((item) => (

              <option key={item} value={item}>{item}</option>

            ))}

          </select>

        </div>

        <div className="mt-3 text-xs text-cyan-400">

          Selected road: <span className="font-semibold">{selectedRoad}</span>

        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

          {[

            ['AVG MEAN VELOCITY', averageSpeedLabel, speedReadings.length ? 'Average of measured traffic speeds' : 'No speed measurements available'],

            ['CONGESTION INDEX', `${roadAnalysis.congestionScore} /100`, congestionPrediction ? `Observed: ${congestionLevel} | Model: ${congestionPrediction.predicted_level}` : `Observed: ${congestionLevel} | Model unavailable`],

            ['PEAK DELAY DELTA', delayPrediction ? `${delayPrediction.estimated_delay_minutes.toFixed(1)} min` : 'Unavailable', delayPrediction ? `Estimated delay | ${Math.round(delayPrediction.confidence * 100)}% confidence` : 'Prediction API unavailable'],

            [

              'PREDICTION ACCURACY',

              modelEvaluation?.metrics?.accuracy != null

                ? `${(modelEvaluation.metrics.accuracy * 100).toFixed(1)}%`

                : 'Not available',

              modelEvaluation

              ? `${modelEvaluation.status === 'preliminary_chronological_holdout' ? 'Preliminary evaluation' : modelEvaluation.status} | ${modelEvaluation.sample_count ?? 0} samples`

              : 'Evaluation API unavailable',

            ],

          ].map(([title, value, sub]) => (

            <div key={title} className="rounded-xl border border-gray-800 bg-[#0c1424] p-4">

              <p className="text-[10px] font-bold text-gray-500">{title}</p>

              <p className="mt-2 text-2xl font-bold">{value}</p>

              <p className="mt-1 text-xs text-cyan-400">{sub}</p>

            </div>

          ))}

        </div>

        <section className="mt-5 rounded-xl border border-gray-800 bg-[#0c1424] p-5">

          <div className="flex flex-wrap items-center justify-between gap-2">

            <h2 className="font-semibold">Backend Prediction Results</h2>

            <span className="text-xs text-cyan-400">

              {congestionPrediction ? `Model: ${congestionPrediction.model_version}` : 'Model prediction unavailable'}

            </span>

          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

            <div className="rounded-lg border border-gray-800 p-4">

              <p className="text-xs text-gray-500">Predicted congestion level</p>

              <p className="mt-2 text-lg font-semibold text-white">

                {congestionPrediction ? congestionPrediction.predicted_level : 'Unavailable'}

              </p>

              <p className="mt-1 text-xs text-gray-400">

                {congestionPrediction && congestionPrediction.confidence !== null

                  ? `Model confidence: ${Math.round(congestionPrediction.confidence * 100)}%`

                  : 'No prediction confidence returned'}

              </p>

            </div>

            <div className="rounded-lg border border-gray-800 p-4">

              <p className="text-xs text-gray-500">Predicted peak-hour windows</p>

              {peakWindows.length ? (

                <ul className="mt-2 space-y-1 text-sm text-white">

                  {peakWindows.map((window, index) => (

                    <li key={`${window.start}-${window.end}-${index}`}>

                      {window.start} – {window.end}

                    </li>

                  ))}

                </ul>

              ) : (

                <p className="mt-2 text-sm text-gray-400">No peak windows returned</p>

              )}

            </div>

            <div className="rounded-lg border border-cyan-900/60 bg-cyan-950/20 p-4">

              <p className="text-xs text-gray-400">Dataset-based predicted vehicle count</p>

              <p className="mt-2 text-2xl font-semibold text-white">

                {vehicleCountPrediction

                  ? vehicleCountPrediction.predicted_vehicle_count.toFixed(1)

                  : 'Unavailable'}

              </p>

              <p className="mt-1 text-sm text-cyan-300">

                {vehicleCountPrediction

                  ? vehicleCountPrediction.traffic_condition

                  : 'No estimate available'}

              </p>

              <p className="mt-2 text-xs text-gray-400">

                Provisional mapping: selected road number to dataset junction number.

                This is a model estimate, not a live sensor count.

              </p>

              <p className="mt-1 break-words text-xs text-gray-500">

                {vehicleCountPrediction

                  ? `Junction ${vehicleCountPrediction.junction} | Model: ${vehicleCountPrediction.model_version}`

                  : 'Vehicle-count model unavailable'}

              </p>

            </div>

          </div>

          {delayPrediction && (

            <p className="mt-3 text-xs text-gray-400">

              Estimated delay: {delayPrediction.estimated_delay_minutes.toFixed(1)} minutes.

              Confidence: {Math.round(delayPrediction.confidence * 100)}%.

              This is a backend estimate, not a measured travel delay.

            </p>

          )}

          {predictionError && (

            <p role="status" className="mt-3 text-xs text-amber-400">{predictionError}</p>

          )}

        </section>

        <div className="mt-5 grid gap-5 lg:grid-cols-3">

          <section className="rounded-xl border border-gray-800 bg-[#0c1424] p-5 lg:col-span-2">

            <div className="flex items-start justify-between gap-3">

              <div>

                <h2 className="font-semibold">{range} Traffic Volume</h2>

                <p className="text-xs text-gray-500">Observed vehicle counts from backend records</p>

              </div>

              <TrendingUp className="shrink-0 text-cyan-400" />

            </div>

            <div className="mt-6 overflow-x-auto">

  {currentTrend.values.length > 0 ? (

    <div className="flex h-52 w-full items-end gap-3">

      {currentTrend.values.map((value, index) => (

        <div key={`${currentTrend.labels[index]}-${index}`} className="flex h-full min-w-0 flex-1 flex-col justify-end">

          <div className="flex h-full items-end">

            <div

              className="w-full rounded-t bg-cyan-500/80 transition-all hover:bg-cyan-400"

              style={{

                height: `${value > 0 ? Math.max(3, value / Math.max(1, ...currentTrend.values) * 100) : 0}%`,

              }}

              title={`${currentTrend.labels[index]} | Vehicles: ${value} | Density: ${currentTrend.details[index].density.toFixed(0)}% | Congestion: ${currentTrend.details[index].congestion}`}

            />

          </div>

          <p className="mt-1 text-center text-[10px] font-medium text-gray-300">

            {currentTrend.labels[index]}

          </p>

        </div>

      ))}

    </div>

  ) : (

    <p className="py-12 text-center text-sm text-gray-400">

      No traffic records available for this period.

    </p>

  )}

</div>

<div className="mt-3 flex flex-wrap gap-5 text-[10px] font-medium text-gray-300">

  <span className="text-cyan-300">Observed Vehicles</span>

  <span>Hover over a bar for density and congestion details</span>

</div>

<div className="mt-3 flex flex-wrap gap-5 text-[10px] font-medium text-gray-300">

            </div>

          </section>

          <section className="rounded-xl border border-gray-800 bg-[#0c1424] p-5">

            <h2 className="font-semibold">Peak Congestion Surge</h2>

            <p className="text-xs text-gray-500">Congestion distribution</p>

            <div className="mx-auto mt-8 h-36 w-36 rounded-full p-8"

              style={{

                background: congestionDistribution.total

                  ? `conic-gradient(#22c55e 0% ${congestionDistribution.lowPercent}%, #f59e0b ${congestionDistribution.lowPercent}% ${congestionDistribution.lowPercent + congestionDistribution.moderatePercent}%, #ef4444 ${congestionDistribution.lowPercent + congestionDistribution.moderatePercent}% 100%)`

                  : "#374151",

              }}>

              <div className="flex h-full items-center justify-center rounded-full bg-[#0c1424] text-center text-xs">

                <span>Peak<br />{roadAnalysis.peakCongestion}</span>

              </div>

            </div>

            <div className="mt-5 space-y-2 text-xs text-gray-400">

              <p className="flex justify-between">

                <span>Low</span>

                <span>{congestionDistribution.counts.Low} ({congestionDistribution.total ? congestionDistribution.lowPercent.toFixed(1) : '0.0'}%)</span>

              </p>

              <p className="flex justify-between">

                <span>Moderate</span>

                <span>{congestionDistribution.counts.Moderate} ({congestionDistribution.total ? congestionDistribution.moderatePercent.toFixed(1) : '0.0'}%)</span>

              </p>

              <p className="flex justify-between">

                <span>Heavy</span>

                <span>{congestionDistribution.counts.Heavy} ({congestionDistribution.total ? congestionDistribution.heavyPercent.toFixed(1) : '0.0'}%)</span>

              </p>

              {!congestionDistribution.total && <p>No records available for this selection.</p>}

            </div>

          </section>

        </div>

        <section className="mt-5 rounded-xl border border-gray-800 bg-[#0c1424] p-5">

          <div className="flex flex-wrap justify-between gap-3">

            <div>

              <div className="flex flex-wrap items-center gap-2">

                <h2 className="font-semibold">Traffic Trend Analysis</h2>

                <span className="rounded bg-green-500/10 px-2 py-1 text-[9px] text-green-400">{isAnalyticsLoading ? "LOADING" : analyticsError ? "API ERROR" : "BACKEND DATA"}</span>

              </div>

              <p className="mt-1 text-xs text-gray-500">{analyticsError || (isAnalyticsLoading ? "Loading backend traffic records..." : `${currentTrend.values.length} backend records | ${range === "7 Days" ? "week" : range === "1 Month" ? "month" : "day"} API window`)}</p>

            </div>

            <div className="relative flex gap-2">

              <input

                value={road}

                onChange={(event) => setRoad(event.target.value)}

                onKeyDown={(event) => {

                  if (event.key === 'Enter') searchRoad();

                }}

                placeholder="Road name..."

                className="w-40 rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs"

              />

              <button type="button" onClick={searchRoad} aria-label="Search trend road" className="rounded border border-gray-700 px-2 text-cyan-400">

                <Search size={14} />

              </button>

              <button type="button" onClick={() => { setRange('24 Hours'); setUseCustomDates(false); }} aria-label="Reset trend" className="rounded border border-gray-700 px-2">

                <RefreshCw size={14} />

              </button>

              {road.trim() !== '' && (

                <div className="absolute right-0 top-full z-50 mt-1 w-48 overflow-hidden rounded-lg border border-gray-700 bg-[#0c1424] shadow-xl">

                  {matchingRoads.length > 0 ? matchingRoads.map((item) => (

                    <button type="button" key={item} onClick={() => selectRoad(item)} className="block w-full px-3 py-2 text-left text-xs text-gray-300 hover:bg-cyan-500/10 hover:text-cyan-400">

                      {item}

                    </button>

                  )) : <div className="px-3 py-2 text-xs text-gray-500">No matching road</div>}

                </div>

              )}

            </div>

          </div>

          <p className="mt-4 text-xs text-cyan-400">{selectedRoad}</p>

          <div className="mt-4 overflow-x-auto">

            <div className={`flex h-40 items-end ${

              range === '1 Month' ? 'min-w-[900px] gap-1' : range === '24 Hours' ? 'min-w-[750px] gap-1' : 'w-full gap-3'

            }`}>

              {currentTrend.values.map((value, index) => (

                <div key={index} className="flex h-full flex-1 flex-col justify-end">

                  <div className="flex h-full items-end">

                    <div className="w-full rounded-t bg-cyan-500/70 transition-all duration-300 hover:bg-cyan-400" style={{ height: `${value}%` }} title={`${currentTrend.labels[index]}: ${value}`} />

                  </div>

                  <p className="mt-1 text-center text-[10px] font-medium text-gray-300">{currentTrend.labels[index]}</p>

                </div>

              ))}

            </div>

          </div>

          <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">

            {[

              ['Peak Value', `${peakValue}`],

              ['Avg Speed', averageSpeedLabel],

              ['Peak Period', peakLabel],

              ['Total Trend Readings', `${currentTrend.values.length}`],

            ].map(([title, value]) => (

              <div key={title} className="rounded bg-[#101a2c] p-3">

                <p className="text-[10px] font-medium text-gray-300">{title}</p>

                <p className="mt-1 font-semibold">{value}</p>

              </div>

            ))}

          </div>

        </section>

        <section className="mt-5 rounded-xl border border-gray-800 bg-[#0c1424] p-5">

          <div className="flex flex-wrap justify-between gap-3">

            <div>

              <h2 className="font-semibold">Congestion Heatmap</h2>

              <p className="text-xs text-gray-500">Backend traffic records; grey cells indicate missing data. Speed and separate score values are not supplied by this API.</p>

            </div>

            <div className="flex flex-wrap items-center gap-2">

              <label className="flex items-center gap-1">

                <span className="text-[10px] font-medium text-gray-300">From</span>

                <input

                  type="date"

                  value={fromDate}

                  max={toDate}

                  onChange={(event) => handleFromDateChange(event.target.value)}

                  style={{ colorScheme: 'dark' }}

                  className="rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs text-white"

                />

              </label>

              <span className="text-xs text-gray-600">to</span>

              <label className="flex items-center gap-1">

                <span className="text-[10px] font-medium text-gray-300">To</span>

                <input

                  type="date"

                  value={toDate}

                  min={fromDate}

                  onChange={(event) => handleToDateChange(event.target.value)}

                  style={{ colorScheme: 'dark' }}

                  className="rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs text-white"

                />

              </label>

              <select

                aria-label="Heatmap bucket"

                value={bucket}

                onChange={(event) => setBucket(event.target.value as 'Hourly' | 'Daily')}

                className="rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs"

              >

                <option>Hourly</option>

                <option>Daily</option>

              </select>

              {metrics.map((item) => (

                <button

                  type="button"

                  key={item}

                  onClick={() => setMetric(item as MetricType)}

                  className={`rounded px-3 py-1 text-xs transition ${

                    metric === item ? 'bg-cyan-600 !text-white' : 'bg-[#101a2c] !text-gray-300 hover:bg-gray-800'

                  }`}

                >

                  {item}

                </button>

              ))}

            </div>

          </div>

          <div className="mt-4 rounded border border-cyan-500/20 bg-cyan-500/5 px-3 py-2 text-xs">

            <span className="text-gray-400">Selected date range:</span>

            <span className="ml-2 font-semibold text-cyan-400">{fromDate}</span>

            <span className="mx-2 text-gray-400">to</span>

            <span className="font-semibold text-cyan-400">{toDate}</span>

            <span className="ml-3 text-gray-500">({rangeDays} {rangeDays === 1 ? 'day' : 'days'})</span>

          </div>

          <div className="mt-2 rounded border border-gray-800 bg-[#101a2c] px-3 py-2 text-xs">

            <span className="text-gray-400">Metric:</span>

            <span className="ml-1 font-semibold text-cyan-400">{metric}</span>

            {metric === 'Level' && <span className="ml-2 text-gray-500">Low / Moderate / Heavy</span>}

          </div>

          <div className="mt-5 overflow-x-auto">

            <div className={bucket === 'Daily' ? 'min-w-[1100px]' : 'min-w-[850px]'}>

              <div

                className="ml-36 grid gap-1 text-[9px] text-gray-600"

                style={{ gridTemplateColumns: `repeat(${heatmapLabels.length}, minmax(0, 1fr))` }}

              >

                {heatmapLabels.map((label, index) => <span key={index} className="truncate">{label}</span>)}

              </div>

              {roads.map((item, row) => {

                const isSelected = item === selectedRoad;

                return (

                  <div key={item} className={`mt-1 flex gap-1 rounded ${isSelected ? 'bg-cyan-500/10 ring-1 ring-cyan-500/40' : ''}`}>

                    <button

                      type="button"

                      onClick={() => selectRoad(item)}

                      className={`w-36 shrink-0 truncate py-2 pl-1 text-left text-xs ${

                        isSelected ? 'font-semibold text-cyan-400' : 'text-gray-400 hover:text-white'

                      }`}

                    >

                      {item}

                    </button>

                    <div

                      className="grid flex-1 gap-1"

                      style={{ gridTemplateColumns: `repeat(${heatmapLabels.length}, minmax(0, 1fr))` }}

                    >

                      {heatmapLabels.map((_, col) => {

                        const value = heat(row, col);

                        return (

                          <div

                            key={col}

                            title={`${item} ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â ${metric}: ${metric === 'Level' ? getLevel(value) : value}`}

                            className={`h-7 rounded ${getHeatColor(value)}`}

                            style={{ opacity: 0.2 + value / 125 }}

                          />

                        );

                      })}

                    </div>

                  </div>

                );

              })}

            </div>

          </div>

          <div className="mt-5 rounded-lg border border-gray-800 bg-[#101a2c] p-4">

            <div className="flex flex-wrap items-start justify-between gap-4">

              <div>

                <p className="text-xs text-cyan-400">SELECTED ROAD</p>

                <h3 className="mt-1 font-semibold">{selectedRoad}</h3>

                <p className="mt-1 text-xs text-gray-500">Current metric: {metric}</p>

              </div>

              <div className="min-w-[180px] rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-5 py-3 text-right">

                <p className="text-[9px] font-bold tracking-wide text-gray-500">CONGESTION SCORE</p>

                <div className="mt-1 flex items-baseline justify-end gap-1">

                  <span className="text-3xl font-bold text-cyan-400">{roadAnalysis.congestionScore}</span>

                  <span className="text-xs text-gray-500">/100</span>

                </div>

                <p className="mt-1 text-[10px] font-medium text-gray-300">{congestionLevel}</p>

              </div>

            </div>

            <div className="mt-4 grid grid-cols-2 gap-4 border-t border-gray-800 pt-4 md:grid-cols-3 lg:grid-cols-6">

              {[

                ['Avg Vehicle Count', roadAnalysis.totalReadings ? roadAnalysis.vehicleCount.toFixed(1) : 'No data'],

                ['Avg Speed', averageSpeedLabel],

                ['Avg Density', roadAnalysis.totalReadings ? roadAnalysis.averageDensity.toFixed(1) : 'No data'],

                ['Max Density', roadAnalysis.totalReadings ? roadAnalysis.maxDensity.toFixed(1) : 'No data'],

                ['Total Readings', roadAnalysis.totalReadings.toLocaleString()],

                ['Peak Congestion', roadAnalysis.peakCongestion],

              ].map(([title, value]) => (

                <div key={title}>

                  <p className="text-[9px] text-gray-500">{title}</p>

                  <p className="mt-1 text-sm font-semibold">{value}</p>

                </div>

              ))}

            </div>

            {metric === 'Level' && (

              <div className="mt-4 rounded-lg border border-cyan-500/20 bg-cyan-500/5 p-4">

                <div className="flex items-center justify-between gap-3">

                  <div>

                    <p className="text-xs font-semibold text-cyan-400">ROAD LEVEL ANALYSIS</p>

                    <p className="mt-1 text-[10px] font-medium text-gray-300">Details for the selected road</p>

                  </div>

                  <span className={`rounded px-3 py-1 text-[10px] font-semibold ${

                    congestionLevel === 'Heavy'

                      ? 'bg-red-500/10 text-red-400'

                      : congestionLevel === 'Moderate'

                        ? 'bg-yellow-500/10 text-yellow-400'

                        : 'bg-green-500/10 text-green-400'

                  }`}>

                    {congestionLevel}

                  </span>

                </div>

                <p className="mt-3 text-xs leading-6 text-gray-400">

                  <span className="font-semibold text-white">{selectedRoad}</span> has a{' '}

                  <span className="font-semibold text-cyan-400">{congestionLevel}</span> congestion

                  level, with a score of{' '}

                  <span className="font-semibold text-white">{roadAnalysis.congestionScore}/100</span>.

                  Average vehicle count is{' '}

                  <span className="font-semibold text-white">{roadAnalysis.vehicleCount.toLocaleString()}</span>,

                  average speed is{' '}

                  <span className="font-semibold text-white">{averageSpeedLabel}</span>,

                  average density is{' '}

                  <span className="font-semibold text-white">{roadAnalysis.averageDensity.toFixed(1)}</span>,

                  and maximum density is{' '}

                  <span className="font-semibold text-white">{roadAnalysis.maxDensity.toFixed(1)}</span>.

                  The selected range contains{' '}

                  <span className="font-semibold text-white">{roadAnalysis.totalReadings.toLocaleString()}</span>{' '}

                  illustrative readings. Peak congestion: {roadAnalysis.peakCongestion}.

                </p>

              </div>

            )}

          </div>

        </section>

        <section className="mt-5 rounded-xl border border-purple-500/20 bg-[#0c1424] p-5">

          <div className="flex flex-wrap items-center justify-between gap-4">

            <div>

              <div className="flex flex-wrap items-center gap-2">

                <Sparkles size={17} className="text-purple-400" />

                <h2 className="font-semibold">AI Tactical Recommendations Copilot</h2>

                <span className="rounded bg-purple-500/10 px-2 py-1 text-[9px] font-semibold text-purple-400">

                  {recommendationData?.generated_by === 'rule_based' ? 'BACKEND RULE-BASED' : 'BACKEND'}

                </span>

              </div>

              <p className="mt-1 text-xs text-gray-500">

                Recommendations are generated from stored traffic observations and the available congestion prediction. They are decision support, not validated traffic-control interventions.

              </p>

            </div>

            <button

              type="button"

              onClick={rescanNetwork}

              disabled={isRescanning}

              className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-xs transition ${

                isRescanning

                  ? 'cursor-not-allowed border-purple-500/30 bg-purple-500/10 text-purple-300'

                  : 'border-gray-700 bg-[#101a2c] text-gray-300 hover:border-purple-500/50 hover:bg-purple-500/10 hover:text-purple-300'

              }`}

            >

              <RefreshCw size={14} className={isRescanning ? 'animate-spin' : ''} />

              {isRescanning ? 'Scanning Network...' : 'Rescan Network'}

            </button>

          </div>

          <div className="mt-4 flex flex-wrap items-center gap-3 rounded-lg border border-purple-500/10 bg-purple-500/5 px-4 py-3">

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 animate-pulse rounded-full bg-green-400" />

              <span className="text-xs font-medium text-green-400">Backend recommendations loaded</span>

            </div>

            <span className="text-gray-700">|</span>

            <span className="text-[10px] font-medium text-gray-300">Scan #{scanVersion + 1}</span>

            <span className="text-[10px] font-medium text-gray-300">|</span>

           <span className="text-[10px] font-medium text-gray-300">Road: {recommendationData?.road_name ?? 'Loading'} | Recent records considered: {recommendationData?.record_count ?? 0}</span>

          </div>

          <div className="my-4 flex flex-wrap gap-2">

            {['ALL', 'HIGH', 'MED', 'LOW'].map((item) => (

              <button

                type="button"

                key={item}

                onClick={() => setPriority(item)}

                className={`rounded px-4 py-1 text-xs transition ${

                  priority === item ? 'bg-purple-600 text-white' : 'bg-[#101a2c] text-gray-400 hover:bg-gray-800'

                }`}

              >

                {item}

              </button>

            ))}

          </div>

          <div className="grid gap-4 md:grid-cols-3">

            {filtered.map((item) => (

              <div

                key={`${item[1]}-${scanVersion}`}

                className="rounded-xl border border-gray-800 bg-[#101a2c] p-4 transition hover:border-purple-500/40"

              >

                <div className="flex justify-between gap-2">

                  <span className={`text-[10px] font-bold ${

                    item[0] === 'HIGH' ? 'text-red-400' : item[0] === 'MED' ? 'text-yellow-400' : 'text-green-400'

                  }`}>

                    {item[0]} PRIORITY

                  </span>

                  <span className="text-[10px] text-purple-400">{item[3]}</span>

                </div>

                <h3 className="mt-3 font-semibold">{item[1]}</h3>

                <p className="mt-2 text-xs text-gray-500">

                  Target corridor: <span className="text-gray-300">{item[2]}</span>

                </p>

                <div className="mt-4 flex justify-between gap-2 text-xs">

                  <span className="text-gray-400">{item[4]}</span>

                  <span className="text-gray-400">Evidence: {item[5]}</span>

                </div>

                <button

                  type="button"

                  onClick={() => {

                    selectRoad(item[2]);

                    setSelectedInsight(item);

                  }}

                  className="mt-4 flex w-full items-center justify-center gap-2 rounded border border-gray-700 py-2 text-xs transition hover:border-purple-500/50 hover:bg-purple-500/10"

                >

                  <Sparkles size={12} />

                  View Road Insight

                </button>

              </div>

            ))}

          </div>

          {selectedInsight && (

            <div className="mt-5 rounded-xl border border-purple-500/30 bg-purple-500/5 p-5">

              <div className="flex flex-wrap items-start justify-between gap-3">

                <div>

                  <p className="text-xs font-semibold uppercase tracking-wider text-purple-400">

                    Selected Road Insight

                  </p>

                  <h3 className="mt-2 text-lg font-bold text-white">

                    {selectedInsight[2]}

                  </h3>

                  <p className="mt-1 text-sm text-gray-400">

                    {selectedInsight[1]}

                  </p>

                </div>

                <button

                  type="button"

                  onClick={() => setSelectedInsight(null)}

                  className="rounded border border-gray-700 px-3 py-1 text-xs text-gray-300 hover:bg-gray-800"

                >

                  Close

                </button>

              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-3">

                <div className="rounded-lg border border-gray-800 bg-[#101a2c] p-3">

                  <p className="text-xs text-gray-500">Priority</p>

                  <p className="mt-1 font-semibold text-white">{selectedInsight[0]}</p>

                </div>

                <div className="rounded-lg border border-gray-800 bg-[#101a2c] p-3">

                  <p className="text-xs text-gray-500">Generation method</p>

                  <p className="mt-1 font-semibold text-purple-400">{selectedInsight[3]}</p>

                </div>

                <div className="rounded-lg border border-gray-800 bg-[#101a2c] p-3">

                  <p className="text-xs text-gray-500">Observed traffic evidence</p>

                  <p className="mt-1 font-semibold text-green-400">{selectedInsight[5]}</p>

                </div>

              </div>

              <div className="mt-4 rounded-lg bg-[#101a2c] p-4">

                <p className="text-xs font-medium text-gray-500">Reason</p>

                <p className="mt-1 text-sm leading-6 text-gray-400">

                  {selectedInsight[6]}

                </p>

                <p className="mt-3 text-sm font-semibold text-white">Suggested action</p>

                <p className="mt-1 text-sm leading-6 text-gray-400">

                  {selectedInsight[7]}

                </p>

                <p className="mt-3 text-xs text-yellow-400">

                  {recommendationData?.disclaimer ?? 'Backend-generated decision support; verify local conditions before acting.'}

                </p>

              </div>

            </div>

          )}

        </section>

        <footer className="mt-5 border-t border-gray-800 py-4 text-xs text-gray-500">

          TrafficVision AI | Analytics | Backend traffic records

        </footer>

      </main>

    </div>

  );

}
