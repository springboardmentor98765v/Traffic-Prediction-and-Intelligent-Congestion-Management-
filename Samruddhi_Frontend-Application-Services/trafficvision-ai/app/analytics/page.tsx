'use client';

import {
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
} from 'react';

import {
  Search,
  Download,
  RefreshCw,
  TrendingUp,
  Sparkles,
} from 'lucide-react';

import { usePathname } from 'next/navigation';

import { Sidebar } from '../../components/Sidebar';

const roads = [
  'R001 - Shivajinagar',
  'R002 - Koregaon Park',
  'R003 - Wakad',
  'R004 - Baner',
  'R005 - Hinjawadi',
  'R006 - Kothrud',
  'R007 - Viman Nagar',
];

const baseRecommendations = [
  [
    'HIGH',
    'Dynamic Green-Wave Signal Offset',
    'R001 - Shivajinagar',
    '94%',
    '+12% throughput',
    '8 min saved',
  ],
  [
    'MED',
    'Heavy Freight Transit Lane Balancing',
    'R005 - Hinjawadi',
    '88%',
    '+7% throughput',
    '5 min saved',
  ],
  [
    'LOW',
    'Dynamic Variable Speed Harmonics',
    'R007 - Viman Nagar',
    '82%',
    '+4% throughput',
    '3 min saved',
  ],
];

const metrics = [
  'Density',
  'Speed',
  'Score',
  'Level',
];

const trendData = {
  '24 Hours': {
    values: [
      28, 32, 25, 22, 30, 38,
      48, 58, 65, 72, 68, 75,
      82, 88, 76, 70, 62, 68,
      80, 92, 85, 70, 55, 40,
    ],
    labels: [
      '12 AM',
      '1 AM',
      '2 AM',
      '3 AM',
      '4 AM',
      '5 AM',
      '6 AM',
      '7 AM',
      '8 AM',
      '9 AM',
      '10 AM',
      '11 AM',
      '12 PM',
      '1 PM',
      '2 PM',
      '3 PM',
      '4 PM',
      '5 PM',
      '6 PM',
      '7 PM',
      '8 PM',
      '9 PM',
      '10 PM',
      '11 PM',
    ],
  },

  '7 Days': {
    values: [
      45, 62, 78, 54, 88, 70, 58,
    ],
    labels: [
      'Mon',
      'Tue',
      'Wed',
      'Thu',
      'Fri',
      'Sat',
      'Sun',
    ],
  },

  '1 Month': {
    values: [
      42, 55, 48, 65, 72,
      60, 78, 82, 58, 64,
      70, 76, 68, 85, 74,
      62, 80, 88, 71, 66,
      79, 83, 91, 75, 69,
      84, 77, 89, 73, 81,
    ],
    labels: [
      '1',
      '2',
      '3',
      '4',
      '5',
      '6',
      '7',
      '8',
      '9',
      '10',
      '11',
      '12',
      '13',
      '14',
      '15',
      '16',
      '17',
      '18',
      '19',
      '20',
      '21',
      '22',
      '23',
      '24',
      '25',
      '26',
      '27',
      '28',
      '29',
      '30',
    ],
  },
};

type RangeType = keyof typeof trendData;
type MetricType =
  | 'Density'
  | 'Speed'
  | 'Score'
  | 'Level';

export default function AnalyticsPage() {
  const [role, setRole] = useState('Public');

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Public');
  }, []);

  const pathname = usePathname();

  const [road, setRoad] = useState('');

  const [selectedRoad, setSelectedRoad] =
    useState(roads[0]);

  const [range, setRange] =
    useState<RangeType>('24 Hours');

  const [bucket, setBucket] =
    useState<'Hourly' | 'Daily'>('Hourly');

  const [metric, setMetric] =
    useState<MetricType>('Density');

  const [priority, setPriority] =
    useState('ALL');

  const [fromDate, setFromDate] =
    useState('2026-09-01');

  const [toDate, setToDate] =
    useState('2026-09-30');

  /* =========================================================
     AI RESCAN STATE
  ========================================================= */

  const [scanVersion, setScanVersion] =
    useState(0);

  const [isRescanning, setIsRescanning] =
    useState(false);

  /* =========================================================
     FORCE ANALYTICS PAGE TO TOP
  ========================================================= */

  useLayoutEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const previousScrollRestoration =
      window.history.scrollRestoration;

    window.history.scrollRestoration = 'manual';

    const forceScrollToTop = () => {
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'auto',
      });

      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;

      const main =
        document.querySelector(
          'main'
        ) as HTMLElement | null;

      if (main) {
        main.scrollTop = 0;
        main.scrollLeft = 0;
      }

      const scrollContainers =
        document.querySelectorAll<HTMLElement>(
          '[data-scroll-container]'
        );

      scrollContainers.forEach(
        (element) => {
          element.scrollTop = 0;
          element.scrollLeft = 0;
        }
      );
    };

    forceScrollToTop();

    const frame =
      window.requestAnimationFrame(() => {
        forceScrollToTop();
      });

    const timer1 =
      window.setTimeout(
        forceScrollToTop,
        0
      );

    const timer2 =
      window.setTimeout(
        forceScrollToTop,
        100
      );

    const timer3 =
      window.setTimeout(
        forceScrollToTop,
        300
      );

    return () => {
      window.cancelAnimationFrame(
        frame
      );

      window.clearTimeout(timer1);
      window.clearTimeout(timer2);
      window.clearTimeout(timer3);

      window.history.scrollRestoration =
        previousScrollRestoration;
    };
  }, [pathname]);

  /* =========================================================
     AI TACTICAL RECOMMENDATIONS
  ========================================================= */

  const aiRecommendations =
    useMemo(() => {
      return baseRecommendations.map(
        (recommendation, index) => {
          const confidenceBase =
            Number(
              recommendation[3].replace(
                '%',
                ''
              )
            );

          const confidenceVariation =
            (scanVersion * 3 +
              index * 2) %
            5;

          const confidence =
            Math.min(
              99,
              confidenceBase +
                confidenceVariation
            );

          const throughputBase =
            4 +
            index * 4 +
            (scanVersion % 3);

          const savedMinutes =
            3 +
            index * 2 +
            (scanVersion % 2);

          return [
            recommendation[0],
            recommendation[1],
            index === 0
              ? selectedRoad
              : recommendation[2],
            `${confidence}%`,
            `+${throughputBase}% throughput`,
            `${savedMinutes} min saved`,
          ];
        }
      );
    }, [
      scanVersion,
      selectedRoad,
    ]);

  /* =========================================================
     FILTERED AI RECOMMENDATIONS
  ========================================================= */

  const filtered =
    useMemo(
      () =>
        priority === 'ALL'
          ? aiRecommendations
          : aiRecommendations.filter(
              (r) =>
                r[0] === priority
            ),
      [
        priority,
        aiRecommendations,
      ]
    );

  /* =========================================================
     AI RESCAN FUNCTION
  ========================================================= */

  const rescanNetwork = () => {
    if (isRescanning) {
      return;
    }

    setIsRescanning(true);

    window.setTimeout(() => {
      setScanVersion(
        (previous) =>
          previous + 1
      );

      setIsRescanning(false);
    }, 900);
  };

  /* =========================================================
     ROAD SEARCH
  ========================================================= */

  const matchingRoads =
    useMemo(() => {
      const query =
        road.trim().toLowerCase();

      if (!query) {
        return [];
      }

      return roads.filter(
        (r) =>
          r
            .toLowerCase()
            .includes(query)
      );
    }, [road]);

  const selectRoad = (
    roadName: string
  ) => {
    setSelectedRoad(
      roadName
    );

    setRoad(
      roadName.replace(
        /^R\d+\s*-\s*/,
        ''
      )
    );
  };

  const searchRoad = () => {
    if (
      matchingRoads.length > 0
    ) {
      selectRoad(
        matchingRoads[0]
      );
    }
  };

  /* =========================================================
     DATE RANGE
  ========================================================= */

  const rangeDays =
    useMemo(() => {
      const from =
        new Date(
          `${fromDate}T00:00:00`
        );

      const to =
        new Date(
          `${toDate}T00:00:00`
        );

      const difference =
        to.getTime() -
        from.getTime();

      return Math.max(
        1,
        Math.floor(
          difference /
            (1000 *
              60 *
              60 *
              24)
        ) + 1
      );
    }, [
      fromDate,
      toDate,
    ]);

  /* =========================================================
     DATE SEED
  ========================================================= */

  const rangeSeed =
    useMemo(() => {
      return [
        ...`${fromDate}${toDate}`,
      ].reduce(
        (sum, char) =>
          sum +
          char.charCodeAt(0),
        0
      );
    }, [
      fromDate,
      toDate,
    ]);

  /* =========================================================
     HEATMAP LABELS
  ========================================================= */

  const heatmapLabels =
    useMemo(() => {
      if (
        bucket === 'Hourly'
      ) {
        return Array.from(
          {
            length: 12,
          },
          (_, i) =>
            `${String(
              i * 2
            ).padStart(
              2,
              '0'
            )}:00`
        );
      }

      const columnCount =
        Math.min(
          rangeDays,
          31
        );

      return Array.from(
        {
          length:
            columnCount,
        },
        (_, index) => {
          const offset =
            rangeDays <= 31
              ? index
              : Math.round(
                  (index *
                    (rangeDays -
                      1)) /
                    Math.max(
                      1,
                      columnCount -
                        1
                    )
                );

          const date =
            new Date(
              `${fromDate}T00:00:00`
            );

          date.setDate(
            date.getDate() +
              offset
          );

          return date.toLocaleDateString(
            'en-IN',
            {
              day: '2-digit',
              month: 'short',
            }
          );
        }
      );
    }, [
      bucket,
      rangeDays,
      fromDate,
    ]);

  /* =========================================================
     HEATMAP VALUES
  ========================================================= */

  const heat = (
    row: number,
    col: number
  ) => {
    const base =
      25 +
      (
        row * 17 +
        col * 11 +
        rangeSeed * 5
      ) % 70;

    if (
      metric === 'Density'
    ) {
      return base;
    }

    if (
      metric === 'Speed'
    ) {
      return (
        30 +
        (
          row * 9 +
          col * 7 +
          rangeSeed * 3
        ) % 40
      );
    }

    if (
      metric === 'Score'
    ) {
      return (
        20 +
        (
          row * 13 +
          col * 8 +
          rangeSeed * 4
        ) % 80
      );
    }

    return base;
  };

  const getLevel = (
    value: number
  ) => {
    if (value >= 70) {
      return 'Heavy';
    }

    if (value >= 45) {
      return 'Moderate';
    }

    return 'Low';
  };

  const getHeatColor = (
    value: number
  ) => {
    if (
      metric === 'Speed'
    ) {
      if (value < 40) {
        return 'bg-red-500';
      }

      if (value < 55) {
        return 'bg-yellow-500';
      }

      return 'bg-green-500';
    }

    if (value >= 70) {
      return 'bg-red-500';
    }

    if (value >= 45) {
      return 'bg-yellow-500';
    }

    return 'bg-green-500';
  };

  /* =========================================================
     SELECTED ROAD ANALYSIS
  ========================================================= */

  const roadAnalysis =
    useMemo(() => {
      const roadIndex =
        Math.max(
          0,
          roads.indexOf(
            selectedRoad
          )
        );

      const vehicleCount =
        1050 +
        roadIndex * 86 +
        rangeDays * 3;

      const averageSpeed =
        Math.max(
          28,
          52 -
            roadIndex * 2
        );

      const averageDensity =
        30.5 +
        roadIndex * 1.7 +
        (rangeDays % 7);

      const maxDensity =
        Math.min(
          99,
          74 +
            roadIndex * 2 +
            (rangeDays % 5)
        );

      const totalReadings =
        1420 +
        roadIndex * 120 +
        rangeDays * 20;

      const peakCongestion =
        roadIndex % 3 === 0
          ? '1–2 PM'
          : roadIndex % 3 === 1
            ? '6–8 PM'
            : '8–9 AM';

      const congestionScore =
        Math.min(
          100,
          Math.round(
            averageDensity +
              25
          )
        );

      return {
        vehicleCount,
        averageSpeed,
        averageDensity,
        maxDensity,
        totalReadings,
        peakCongestion,
        congestionScore,
      };
    }, [
      selectedRoad,
      rangeDays,
    ]);

  const congestionLevel =
    getLevel(
      roadAnalysis.congestionScore
    );

  /* =========================================================
     DATE HANDLERS
  ========================================================= */

  const handleFromDateChange = (
    value: string
  ) => {
    setFromDate(value);

    if (
      value > toDate
    ) {
      setToDate(value);
    }
  };

  const handleToDateChange = (
    value: string
  ) => {
    setToDate(value);

    if (
      value < fromDate
    ) {
      setFromDate(value);
    }
  };

  /* =========================================================
     DOWNLOAD REPORT
  ========================================================= */

  const downloadReport = () => {
    const csv =
      'Road,Average Speed,Average Vehicle Count,Average Density,Max Density,Total Readings,Peak Congestion,Congestion Score\n' +
      `"${selectedRoad}",${roadAnalysis.averageSpeed} km/h,${roadAnalysis.vehicleCount},${roadAnalysis.averageDensity.toFixed(
        1
      )},${roadAnalysis.maxDensity.toFixed(
        1
      )},${roadAnalysis.totalReadings},"${roadAnalysis.peakCongestion}",${roadAnalysis.congestionScore}`;

    const blob =
      new Blob(
        [csv],
        {
          type: 'text/csv',
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const a =
      document.createElement(
        'a'
      );

    a.href = url;

    a.download =
      'trafficvision-historical-report.csv';

    document.body.appendChild(a);

    a.click();

    a.remove();

    URL.revokeObjectURL(
      url
    );
  };

  /* =========================================================
     CURRENT TREND
  ========================================================= */

  const currentTrend =
    trendData[range];

  const peakValue =
    Math.max(
      ...currentTrend.values
    );

  const peakIndex =
    currentTrend.values.indexOf(
      peakValue
    );

  const peakLabel =
    currentTrend.labels[
      peakIndex
    ];

  /* =========================================================
     PAGE
  ========================================================= */

  return (
    <div className="min-h-screen w-full overflow-x-hidden bg-[#060b16] text-white">

      {/* =====================================================
          SIDEBAR
          EXACT 256px / 16rem WIDTH
      ====================================================== */}

      <aside
        className="
          fixed
          left-0
          top-0
          z-50
          hidden
          h-screen
          w-64
          shrink-0
          overflow-hidden
          border-r
          border-gray-800
          bg-[#060b16]
          md:block
        "
      >
        <div className="h-full w-64">
          <Sidebar role={role} />
        </div>
      </aside>

      {/* =====================================================
          MAIN CONTENT
          SAME 256px OFFSET AS SIDEBAR
      ====================================================== */}

      <main
        data-scroll-container
        className="
          min-h-screen
          w-full
          overflow-x-hidden
          bg-[#060b16]
          p-4
          md:ml-64
          md:w-[calc(100%-16rem)]
          md:p-6
        "
      >

        {/* ===================================================
            PAGE HEADER
        ==================================================== */}

        <div className="flex w-full flex-wrap items-start justify-between gap-4">

          <div>

            <h1 className="text-2xl font-bold">
              Traffic Intelligence &
              Spatial Analytics
            </h1>

            <p className="mt-1 text-sm text-gray-500">
              Temporal congestion trajectories,
              machine-learning forecasts
              and autonomous grid
              recommendations.
            </p>

          </div>

          <button
            onClick={
              downloadReport
            }
            className="flex items-center gap-2 rounded-lg bg-cyan-600 px-4 py-2 text-sm hover:bg-cyan-500"
          >
            <Download size={16} />

            Download Historical Report
          </button>

        </div>

        {/* ===================================================
            TOP CONTROLS
        ==================================================== */}

        <div className="mt-5 flex flex-wrap gap-2">

          {/* ROAD SEARCH */}

          <div className="relative">

            <div className="flex rounded-lg border border-gray-700 bg-[#0c1424]">

              <input
                value={road}
                onChange={(e) =>
                  setRoad(
                    e.target.value
                  )
                }
                onKeyDown={(e) => {
                  if (
                    e.key === 'Enter'
                  ) {
                    searchRoad();
                  }
                }}
                placeholder="Search road..."
                className="w-52 bg-transparent px-3 py-2 text-sm outline-none"
              />

              <button
                onClick={
                  searchRoad
                }
                className="px-3 text-cyan-400 hover:text-cyan-300"
              >
                <Search size={17} />
              </button>

            </div>

            {road.trim() !== '' && (

              <div className="absolute left-0 top-full z-50 mt-1 w-full overflow-hidden rounded-lg border border-gray-700 bg-[#0c1424] shadow-xl">

                {matchingRoads.length >
                0 ? (
                  matchingRoads.map(
                    (r) => (
                      <button
                        key={r}
                        onClick={() =>
                          selectRoad(r)
                        }
                        className={`block w-full px-3 py-2 text-left text-xs hover:bg-cyan-500/10 ${
                          r ===
                          selectedRoad
                            ? 'bg-cyan-500/10 text-cyan-400'
                            : 'text-gray-300'
                        }`}
                      >
                        {r}
                      </button>
                    )
                  )
                ) : (
                  <div className="px-3 py-2 text-xs text-gray-500">
                    No matching road
                  </div>
                )}

              </div>

            )}

          </div>

          {/* RANGE */}

          <select
            value={range}
            onChange={(e) =>
              setRange(
                e.target.value as RangeType
              )
            }
            className="rounded-lg border border-gray-700 bg-[#0c1424] px-3 text-sm"
          >
            <option>
              24 Hours
            </option>

            <option>
              7 Days
            </option>

            <option>
              1 Month
            </option>
          </select>

          {/* ROAD SELECT */}

          <select
            value={selectedRoad}
            onChange={(e) =>
              selectRoad(
                e.target.value
              )
            }
            className="rounded-lg border border-gray-700 bg-[#0c1424] px-3 py-2 text-sm outline-none"
          >
            {roads.map(
              (roadName) => (
                <option
                  key={roadName}
                  value={roadName}
                >
                  {roadName}
                </option>
              )
            )}
          </select>

        </div>

        {/* SELECTED ROAD */}

        <div className="mt-3 text-xs text-cyan-400">
          Selected road:{' '}
          <span className="font-semibold">
            {selectedRoad}
          </span>
        </div>

        {/* ===================================================
            SUMMARY
        ==================================================== */}

        <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

          {[
            [
              'AVG MEAN VELOCITY',
              '50.0 km/h',
              'Network average',
            ],
            [
              'CONGESTION INDEX',
              '36.3 /100',
              'Moderate',
            ],
            [
              'PEAK DELAY DELTA',
              '+18.4 min',
              'Peak period',
            ],
            [
              'PREDICTION ACCURACY',
              '94.2%',
              'ML forecast',
            ],
          ].map(
            ([
              title,
              value,
              sub,
            ]) => (
              <div
                key={title}
                className="rounded-xl border border-gray-800 bg-[#0c1424] p-4"
              >
                <p className="text-[10px] font-bold text-gray-500">
                  {title}
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {value}
                </p>

                <p className="mt-1 text-xs text-cyan-400">
                  {sub}
                </p>
              </div>
            )
          )}

        </div>

        {/* ===================================================
            CHARTS
        ==================================================== */}

        <div className="mt-5 grid gap-5 lg:grid-cols-3">

          <section className="rounded-xl border border-gray-800 bg-[#0c1424] p-5 lg:col-span-2">

            <div className="flex justify-between">

              <div>

                <h2 className="font-semibold">
                  {range} Volume &
                  Velocity Trajectory
                </h2>

                <p className="text-xs text-gray-500">
                  Observed volume •
                  ML forecast • speed
                </p>

              </div>

              <TrendingUp className="text-cyan-400" />

            </div>

            <div className="mt-6 overflow-x-auto">

              <div
                className={`flex h-52 items-end ${
                  range === '1 Month'
                    ? 'min-w-[900px] gap-1'
                    : range === '24 Hours'
                      ? 'min-w-[750px] gap-1'
                      : 'w-full gap-3'
                }`}
              >

                {currentTrend.values.map(
                  (
                    value,
                    i
                  ) => (
                    <div
                      key={i}
                      className="flex h-full flex-1 flex-col justify-end"
                    >

                      <div className="flex h-full items-end">

                        <div
                          className="w-full rounded-t bg-cyan-500/70 transition-all duration-300 hover:bg-cyan-400"
                          style={{
                            height: `${value}%`,
                          }}
                          title={`${currentTrend.labels[i]}: ${value}`}
                        />

                      </div>

                      <p className="mt-1 text-center text-[9px] text-gray-500">
                        {
                          currentTrend
                            .labels[i]
                        }
                      </p>

                    </div>
                  )
                )}

              </div>

            </div>

            <div className="mt-3 flex gap-5 text-[10px] text-gray-500">
              <span>
                ● Observed Volume
              </span>

              <span>
                ● ML Forecast
              </span>

              <span>
                ● Speed km/h
              </span>
            </div>

          </section>

          <section className="rounded-xl border border-gray-800 bg-[#0c1424] p-5">

            <h2 className="font-semibold">
              Peak Congestion Surge
            </h2>

            <p className="text-xs text-gray-500">
              Congestion distribution
            </p>

            <div className="mx-auto mt-8 h-36 w-36 rounded-full bg-[conic-gradient(#ef4444_0_35%,#f59e0b_35%_70%,#22c55e_70%_100%)] p-8">

              <div className="flex h-full items-center justify-center rounded-full bg-[#0c1424] text-center text-xs">
                Peak
                <br />
                {
                  roadAnalysis.peakCongestion
                }
              </div>

            </div>

            <div className="mt-5 space-y-2 text-xs text-gray-400">

              <p>
                🔴 Heavy — 35%
              </p>

              <p>
                🟡 Moderate — 35%
              </p>

              <p>
                🟢 Low — 30%
              </p>

            </div>

          </section>

        </div>

        {/* ===================================================
            TRAFFIC TREND ANALYSIS
        ==================================================== */}

        <section className="mt-5 rounded-xl border border-gray-800 bg-[#0c1424] p-5">

          <div className="flex flex-wrap justify-between gap-3">

            <div>

              <div className="flex items-center gap-2">

                <h2 className="font-semibold">
                  Traffic Trend Analysis
                </h2>

                <span className="rounded bg-green-500/10 px-2 py-1 text-[9px] text-green-400">
                  REAL DATA
                </span>

              </div>

              <p className="mt-1 text-xs text-gray-500">
                Historical trend for{' '}
                {range}
              </p>

            </div>

            <div className="relative">

              <div className="flex gap-2">

                <input
                  value={road}
                  onChange={(e) =>
                    setRoad(
                      e.target.value
                    )
                  }
                  onKeyDown={(e) => {
                    if (
                      e.key === 'Enter'
                    ) {
                      searchRoad();
                    }
                  }}
                  placeholder="Road name..."
                  className="w-40 rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs"
                />

                <button
                  onClick={
                    searchRoad
                  }
                  className="rounded border border-gray-700 px-2 text-cyan-400"
                >
                  <Search size={14} />
                </button>

                <button
                  onClick={() =>
                    setRange(
                      '24 Hours'
                    )
                  }
                  className="rounded border border-gray-700 px-2"
                  title="Reset trend"
                >
                  <RefreshCw size={14} />
                </button>

              </div>

              {road.trim() !== '' && (

                <div className="absolute right-0 top-full z-50 mt-1 w-48 overflow-hidden rounded-lg border border-gray-700 bg-[#0c1424] shadow-xl">

                  {matchingRoads.length >
                  0 ? (
                    matchingRoads.map(
                      (r) => (
                        <button
                          key={r}
                          onClick={() =>
                            selectRoad(r)
                          }
                          className="block w-full px-3 py-2 text-left text-xs text-gray-300 hover:bg-cyan-500/10 hover:text-cyan-400"
                        >
                          {r}
                        </button>
                      )
                    )
                  ) : (
                    <div className="px-3 py-2 text-xs text-gray-500">
                      No matching road
                    </div>
                  )}

                </div>

              )}

            </div>

          </div>

          <p className="mt-4 text-xs text-cyan-400">
            {selectedRoad}
          </p>

          <div className="mt-4 overflow-x-auto">

            <div
              className={`flex h-40 items-end ${
                range === '1 Month'
                  ? 'min-w-[900px] gap-1'
                  : range === '24 Hours'
                    ? 'min-w-[750px] gap-1'
                    : 'w-full gap-3'
              }`}
            >

              {currentTrend.values.map(
                (
                  value,
                  i
                ) => (
                  <div
                    key={i}
                    className="flex h-full flex-1 flex-col justify-end"
                  >

                    <div className="flex h-full items-end">

                      <div
                        className="w-full rounded-t bg-cyan-500/70 transition-all duration-300 hover:bg-cyan-400"
                        style={{
                          height: `${value}%`,
                        }}
                        title={`${currentTrend.labels[i]}: ${value}`}
                      />

                    </div>

                    <p className="mt-1 text-center text-[9px] text-gray-500">
                      {
                        currentTrend
                          .labels[i]
                      }
                    </p>

                  </div>
                )
              )}

            </div>

          </div>

          <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">

            {[
              [
                'Peak Value',
                `${peakValue}`,
              ],
              [
                'Avg Speed',
                '50 km/h',
              ],
              [
                'Peak Period',
                peakLabel,
              ],
              [
                'Total Trend Readings',
                `${currentTrend.values.length}`,
              ],
            ].map(
              ([a, b]) => (
                <div
                  key={a}
                  className="rounded bg-[#101a2c] p-3"
                >
                  <p className="text-[10px] text-gray-500">
                    {a}
                  </p>

                  <p className="mt-1 font-semibold">
                    {b}
                  </p>
                </div>
              )
            )}

          </div>

        </section>

        {/* ===================================================
            CONGESTION HEATMAP
        ==================================================== */}

        <section className="mt-5 rounded-xl border border-gray-800 bg-[#0c1424] p-5">

          <div className="flex flex-wrap justify-between gap-3">

            <div>

              <h2 className="font-semibold">
                Congestion Heatmap
              </h2>

              <p className="text-xs text-gray-500">
                Road-level spatial analytics
              </p>

            </div>

            <div className="flex flex-wrap items-center gap-2">

              <div className="flex items-center gap-1">

                <span className="text-[10px] text-gray-500">
                  From
                </span>

                <input
                  type="date"
                  value={fromDate}
                  max={toDate}
                  onChange={(e) =>
                    handleFromDateChange(
                      e.target.value
                    )
                  }
                  style={{
                    colorScheme: 'dark',
                  }}
                  className="rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs text-white"
                />

              </div>

              <span className="text-xs text-gray-600">
                →
              </span>

              <div className="flex items-center gap-1">

                <span className="text-[10px] text-gray-500">
                  To
                </span>

                <input
                  type="date"
                  value={toDate}
                  min={fromDate}
                  onChange={(e) =>
                    handleToDateChange(
                      e.target.value
                    )
                  }
                  style={{
                    colorScheme: 'dark',
                  }}
                  className="rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs text-white"
                />

              </div>

              <select
                value={bucket}
                onChange={(e) =>
                  setBucket(
                    e.target.value as
                      | 'Hourly'
                      | 'Daily'
                  )
                }
                className="rounded border border-gray-700 bg-[#101a2c] px-2 py-1 text-xs"
              >
                <option>
                  Hourly
                </option>

                <option>
                  Daily
                </option>
              </select>

              {metrics.map(
                (m) => (
                  <button
                    key={m}
                    onClick={() =>
                      setMetric(
                        m as MetricType
                      )
                    }
                    className={`rounded px-3 py-1 text-xs transition ${
                      metric === m
                        ? 'bg-cyan-600 text-white'
                        : 'bg-[#101a2c] text-gray-400 hover:bg-gray-800'
                    }`}
                  >
                    {m}
                  </button>
                )
              )}

            </div>

          </div>

          <div className="mt-4 rounded border border-cyan-500/20 bg-cyan-500/5 px-3 py-2 text-xs">

            <span className="text-gray-400">
              Showing heatmap data from
            </span>

            <span className="mx-1 font-semibold text-cyan-400">
              {fromDate}
            </span>

            <span className="text-gray-400">
              to
            </span>

            <span className="ml-1 font-semibold text-cyan-400">
              {toDate}
            </span>

            <span className="ml-2 text-gray-500">
              ({rangeDays}{' '}
              {rangeDays === 1
                ? 'day'
                : 'days'}
              )
            </span>

          </div>

          <div className="mt-2 rounded border border-gray-800 bg-[#101a2c] px-3 py-2 text-xs">

            <span className="text-gray-400">
              Showing:
            </span>

            <span className="ml-1 font-semibold text-cyan-400">
              {metric}
            </span>

            {metric === 'Level' && (
              <span className="ml-2 text-gray-500">
                Low / Moderate / Heavy
              </span>
            )}

          </div>

          <div className="mt-5 overflow-x-auto">

            <div
              className={
                bucket === 'Daily'
                  ? 'min-w-[1100px]'
                  : 'min-w-[850px]'
              }
            >

              <div
                className="ml-36 grid gap-1 text-[9px] text-gray-600"
                style={{
                  gridTemplateColumns:
                    `repeat(${heatmapLabels.length}, minmax(0, 1fr))`,
                }}
              >

                {heatmapLabels.map(
                  (
                    label,
                    index
                  ) => (
                    <span
                      key={index}
                      className="truncate"
                    >
                      {label}
                    </span>
                  )
                )}

              </div>

              {roads.map(
                (
                  r,
                  row
                ) => {

                  const isSelected =
                    r ===
                    selectedRoad;

                  return (
                    <div
                      key={r}
                      className={`mt-1 flex gap-1 rounded ${
                        isSelected
                          ? 'bg-cyan-500/10 ring-1 ring-cyan-500/40'
                          : ''
                      }`}
                    >

                      <button
                        onClick={() =>
                          selectRoad(r)
                        }
                        className={`w-36 truncate py-2 pl-1 text-left text-xs ${
                          isSelected
                            ? 'font-semibold text-cyan-400'
                            : 'text-gray-400 hover:text-white'
                        }`}
                      >
                        {r}
                      </button>

                      <div
                        className="grid flex-1 gap-1"
                        style={{
                          gridTemplateColumns:
                            `repeat(${heatmapLabels.length}, minmax(0, 1fr))`,
                        }}
                      >

                        {heatmapLabels.map(
                          (
                            _,
                            col
                          ) => {

                            const value =
                              heat(
                                row,
                                col
                              );

                            return (
                              <div
                                key={col}
                                title={
                                  metric ===
                                  'Level'
                                    ? `${r} — ${metric}: ${getLevel(value)}`
                                    : `${r} — ${metric}: ${value}`
                                }
                                className={`h-7 rounded ${getHeatColor(
                                  value
                                )}`}
                                style={{
                                  opacity:
                                    0.2 +
                                    value /
                                      125,
                                }}
                              />
                            );
                          }
                        )}

                      </div>

                    </div>
                  );
                }
              )}

            </div>

          </div>

          {/* =================================================
              SELECTED ROAD DETAILS
          ================================================== */}

          <div className="mt-5 rounded-lg border border-gray-800 bg-[#101a2c] p-4">

            <div className="flex flex-wrap items-start justify-between gap-4">

              <div>

                <p className="text-xs text-cyan-400">
                  SELECTED ROAD
                </p>

                <h3 className="mt-1 font-semibold">
                  {selectedRoad}
                </h3>

                <p className="mt-1 text-xs text-gray-500">
                  Current metric:{' '}
                  {metric}
                </p>

              </div>

              {/* RIGHT SIDE CONGESTION SCORE */}

              <div className="min-w-[180px] rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-5 py-3 text-right">

                <p className="text-[9px] font-bold tracking-wide text-gray-500">
                  CONGESTION SCORE
                </p>

                <div className="mt-1 flex items-baseline justify-end gap-1">

                  <span className="text-3xl font-bold text-cyan-400">
                    {
                      roadAnalysis.congestionScore
                    }
                  </span>

                  <span className="text-xs text-gray-500">
                    /100
                  </span>

                </div>

                <p className="mt-1 text-[10px] text-gray-500">
                  {congestionLevel}
                </p>

              </div>

            </div>

            {/* ROAD ANALYSIS */}

            <div className="mt-4 grid grid-cols-2 gap-4 border-t border-gray-800 pt-4 md:grid-cols-3 lg:grid-cols-6">

              {[
                [
                  'Avg Vehicle Count',
                  roadAnalysis.vehicleCount.toLocaleString(),
                ],
                [
                  'Avg Speed',
                  `${roadAnalysis.averageSpeed} km/h`,
                ],
                [
                  'Avg Density',
                  roadAnalysis.averageDensity.toFixed(
                    1
                  ),
                ],
                [
                  'Max Density',
                  roadAnalysis.maxDensity.toFixed(
                    1
                  ),
                ],
                [
                  'Total Readings',
                  roadAnalysis.totalReadings.toLocaleString(),
                ],
                [
                  'Peak Congestion',
                  roadAnalysis.peakCongestion,
                ],
              ].map(
                ([title, value]) => (
                  <div key={title}>

                    <p className="text-[9px] text-gray-500">
                      {title}
                    </p>

                    <p className="mt-1 text-sm font-semibold">
                      {value}
                    </p>

                  </div>
                )
              )}

            </div>

            {/* LEVEL ANALYSIS */}

            {metric === 'Level' && (

              <div className="mt-4 rounded-lg border border-cyan-500/20 bg-cyan-500/5 p-4">

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-xs font-semibold text-cyan-400">
                      ROAD LEVEL ANALYSIS
                    </p>

                    <p className="mt-1 text-[10px] text-gray-500">
                      Detailed analysis for the selected road
                    </p>

                  </div>

                  <span
                    className={`rounded px-3 py-1 text-[10px] font-semibold ${
                      congestionLevel ===
                      'Heavy'
                        ? 'bg-red-500/10 text-red-400'
                        : congestionLevel ===
                            'Moderate'
                          ? 'bg-yellow-500/10 text-yellow-400'
                          : 'bg-green-500/10 text-green-400'
                    }`}
                  >
                    {congestionLevel}
                  </span>

                </div>

                <p className="mt-3 text-xs leading-6 text-gray-400">

                  <span className="font-semibold text-white">
                    {selectedRoad}
                  </span>{' '}

                  currently has a{' '}

                  <span className="font-semibold text-cyan-400">
                    {congestionLevel}
                  </span>{' '}

                  congestion level with a congestion
                  score of{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.congestionScore
                    }
                    /100
                  </span>
                  .

                  The road records an average vehicle
                  count of{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.vehicleCount.toLocaleString()
                    }
                  </span>{' '}

                  vehicles and an average speed of{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.averageSpeed
                    }{' '}
                    km/h
                  </span>
                  .

                  Average density is{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.averageDensity.toFixed(
                        1
                      )
                    }
                  </span>{' '}

                  with a maximum density of{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.maxDensity.toFixed(
                        1
                      )
                    }
                  </span>
                  .

                  A total of{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.totalReadings.toLocaleString()
                    }
                  </span>{' '}

                  readings are included in the selected
                  date range.

                  Peak congestion is observed around{' '}

                  <span className="font-semibold text-white">
                    {
                      roadAnalysis.peakCongestion
                    }
                  </span>
                  .

                </p>

              </div>

            )}

          </div>

        </section>

        {/* ===================================================
            AI TACTICAL RECOMMENDATIONS COPILOT
        ==================================================== */}

        <section className="mt-5 rounded-xl border border-purple-500/20 bg-[#0c1424] p-5">

          {/* HEADER */}

          <div className="flex flex-wrap items-center justify-between gap-4">

            <div>

              <div className="flex flex-wrap items-center gap-2">

                <div className="flex items-center gap-2">

                  <Sparkles
                    size={17}
                    className="text-purple-400"
                  />

                  <h2 className="font-semibold">
                    AI Tactical Recommendations
                    Copilot
                  </h2>

                </div>

                <span className="rounded bg-purple-500/10 px-2 py-1 text-[9px] font-semibold text-purple-400">
                  AI ENGINE
                </span>

              </div>

              <p className="mt-1 text-xs text-gray-500">
                AI-powered tactical recommendations
                generated from current network conditions.
              </p>

            </div>

            {/* RESCAN BUTTON */}

            <button
              onClick={
                rescanNetwork
              }
              disabled={
                isRescanning
              }
              className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-xs transition ${
                isRescanning
                  ? 'cursor-not-allowed border-purple-500/30 bg-purple-500/10 text-purple-300'
                  : 'border-gray-700 bg-[#101a2c] text-gray-300 hover:border-purple-500/50 hover:bg-purple-500/10 hover:text-purple-300'
              }`}
            >

              <RefreshCw
                size={14}
                className={
                  isRescanning
                    ? 'animate-spin'
                    : ''
                }
              />

              {isRescanning
                ? 'Scanning Network...'
                : 'Rescan Network'}

            </button>

          </div>

          {/* AI ENGINE STATUS */}

          <div className="mt-4 flex flex-wrap items-center gap-3 rounded-lg border border-purple-500/10 bg-purple-500/5 px-4 py-3">

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 animate-pulse rounded-full bg-green-400" />

              <span className="text-xs font-medium text-green-400">
                AI Engine Online
              </span>

            </div>

            <span className="text-gray-700">
              |
            </span>

            <span className="text-[10px] text-gray-500">
              Network scan #{scanVersion + 1}
            </span>

            <span className="text-[10px] text-gray-500">
              •
            </span>

            <span className="text-[10px] text-gray-500">
              Monitoring {roads.length} corridors
            </span>

          </div>

          {/* PRIORITY FILTER */}

          <div className="my-4 flex flex-wrap gap-2">

            {[
              'ALL',
              'HIGH',
              'MED',
              'LOW',
            ].map(
              (p) => (

                <button
                  key={p}
                  onClick={() =>
                    setPriority(
                      p
                    )
                  }
                  className={`rounded px-4 py-1 text-xs transition ${
                    priority === p
                      ? 'bg-purple-600 text-white'
                      : 'bg-[#101a2c] text-gray-400 hover:bg-gray-800'
                  }`}
                >
                  {p}
                </button>

              )
            )}

          </div>

          {/* RECOMMENDATION CARDS */}

          <div className="grid gap-4 md:grid-cols-3">

            {filtered.map(
              (r) => (

                <div
                  key={`${r[1]}-${scanVersion}`}
                  className="rounded-xl border border-gray-800 bg-[#101a2c] p-4 transition hover:border-purple-500/40"
                >

                  <div className="flex justify-between">

                    <span
                      className={`text-[10px] font-bold ${
                        r[0] ===
                        'HIGH'
                          ? 'text-red-400'
                          : r[0] ===
                              'MED'
                            ? 'text-yellow-400'
                            : 'text-green-400'
                      }`}
                    >
                      {r[0]} PRIORITY
                    </span>

                    <span className="text-[10px] text-purple-400">
                      {r[3]} confidence
                    </span>

                  </div>

                  <h3 className="mt-3 font-semibold">
                    {r[1]}
                  </h3>

                  <p className="mt-2 text-xs text-gray-500">
                    Target corridor:{' '}
                    <span className="text-gray-300">
                      {r[2]}
                    </span>
                  </p>

                  <div className="mt-4 flex justify-between text-xs">

                    <span className="text-green-400">
                      {r[4]}
                    </span>

                    <span className="text-cyan-400">
                      {r[5]}
                    </span>

                  </div>

                  <button
                    onClick={() =>
                      selectRoad(
                        r[2]
                      )
                    }
                    className="mt-4 flex w-full items-center justify-center gap-2 rounded border border-gray-700 py-2 text-xs transition hover:border-purple-500/50 hover:bg-purple-500/10"
                  >

                    <Sparkles size={12} />

                    View AI Road Insight

                  </button>

                </div>

              )
            )}

          </div>

        </section>

      </main>

    </div>
  );
}
