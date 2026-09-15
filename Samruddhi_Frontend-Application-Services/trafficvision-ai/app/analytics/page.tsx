'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from '../../components/Sidebar';

type Timeframe = '24h' | '7d' | '1m';

export default function AnalyticsPage() {
  const [role, setRole] = useState<string>('User');
  const [timeframe, setTimeframe] = useState<Timeframe>('24h');

  useEffect(() => {
    const savedRole = localStorage.getItem('userRole');
    if (savedRole) setRole(savedRole);
  }, []);

  const metrics = [
    { label: 'Avg Network Speed', value: '42 km/h', change: '+5.2%', positive: true },
    { label: 'Total Analyzed Routes', value: '1,284', change: '+12.4%', positive: true },
    { label: 'Peak Congestion Index', value: '78%', change: '-3.1%', positive: true },
    { label: 'Active Incidents', value: '4 Alerts', change: '+1', positive: false },
  ];

  // Dynamic chart data mapping based on selected timeframe
  const chartDataMap: Record<Timeframe, { label: string; load: number }[]> = {
    '24h': [
      { label: '06:00', load: 20 },
      { label: '09:00', load: 85 },
      { label: '12:00', load: 45 },
      { label: '15:00', load: 60 },
      { label: '18:00', load: 92 },
      { label: '21:00', load: 30 },
    ],
    '7d': [
      { label: 'Mon', load: 70 },
      { label: 'Tue', load: 82 },
      { label: 'Wed', load: 88 },
      { label: 'Thu', load: 75 },
      { label: 'Fri', load: 95 },
      { label: 'Sat', load: 40 },
    ],
    '1m': [
      { label: 'Week 1', load: 65 },
      { label: 'Week 2', load: 78 },
      { label: 'Week 3', load: 85 },
      { label: 'Week 4', load: 72 },
    ],
  };

  const currentChartData = chartDataMap[timeframe];

  const hotspots = [
    { location: 'Hinjewadi Phase 1 Circle', status: 'High Congestion', delay: '+14 mins' },
    { location: 'University Circle / Ganeshkhind Road', status: 'Moderate Flow', delay: '+6 mins' },
    { location: 'Chhatrapati Shivaji Maharaj Flyover', status: 'Active Maintenance', delay: '+8 mins' },
  ];

  return (
    <div className="flex h-screen bg-[#0d1117] text-white">
      <Sidebar role={role} />

      <main className="flex-1 overflow-y-auto p-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Traffic Analytics & Insights</h1>
          <p className="text-sm text-gray-400 mt-1">Overview of overall system performance and congestion metrics.</p>
        </div>

        {/* Metrics Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((item, index) => (
            <div key={index} className="bg-[#161b22] border border-[#30363d] p-5 rounded-2xl space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{item.label}</span>
              <div className="flex justify-between items-baseline">
                <span className="text-2xl font-bold text-white">{item.value}</span>
                <span className={`text-xs font-semibold ${item.positive ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {item.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Traffic Density Breakdown Chart */}
        <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl space-y-6">
          <div className="flex justify-between items-center flex-wrap gap-3">
            <h2 className="text-base font-semibold text-white">Peak Traffic Congestion Trend</h2>
            
            {/* Interactive Timeframe Toggle Buttons */}
            <div className="flex bg-[#0d1117] p-1 rounded-xl border border-[#30363d] space-x-1">
              {(['24h', '7d', '1m'] as Timeframe[]).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1 text-xs font-medium rounded-lg transition ${
                    timeframe === tf
                      ? 'bg-[#1f6feb] text-white shadow-sm'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tf === '24h' ? 'Live 24h' : tf === '7d' ? 'Last 7 Days' : '1 Month'}
                </button>
              ))}
            </div>
          </div>

          <div className={`grid gap-3 items-end h-48 pt-6 border-b border-[#30363d] pb-2 ${
            timeframe === '1m' ? 'grid-cols-4' : 'grid-cols-6'
          }`}>
            {currentChartData.map((data, idx) => (
              <div key={idx} className="flex flex-col items-center gap-2 h-full justify-end">
                <div 
                  className={`w-full rounded-t-lg transition-all duration-300 ${
                    data.load > 75 ? 'bg-red-500/80' : data.load > 50 ? 'bg-amber-500/80' : 'bg-[#1f6feb]'
                  }`} 
                  style={{ height: `${data.load}%` }}
                />
                <span className="text-xs text-gray-400">{data.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Active Hotspots Section */}
        <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl space-y-4">
          <h2 className="text-base font-semibold text-white">High Priority Hotspots</h2>
          <div className="space-y-3">
            {hotspots.map((spot, i) => (
              <div key={i} className="flex justify-between items-center bg-[#0d1117] p-3.5 rounded-xl border border-[#30363d] text-xs">
                <span className="font-semibold text-gray-200">{spot.location}</span>
                <div className="flex items-center gap-4">
                  <span className="text-amber-400 font-medium">{spot.status}</span>
                  <span className="bg-red-500/10 text-red-400 border border-red-500/20 px-2.5 py-1 rounded-md font-bold">
                    {spot.delay}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
