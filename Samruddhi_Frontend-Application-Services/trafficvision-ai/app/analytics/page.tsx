'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { 
  BarChart3, 
  TrendingUp, 
  Car, 
  AlertTriangle, 
  Clock, 
  Download,
  Calendar
} from 'lucide-react';

export default function AnalyticsPage() {
  const [role, setRole] = useState('Admin');
  const [username, setUsername] = useState('USER');
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Admin');
    setUsername(localStorage.getItem('username') || 'USER');
  }, []);

  return (
    <div className="flex min-h-screen bg-[#1c1d28] text-white">
      <Sidebar role={role} />

      <main className="flex-1 p-8 overflow-y-auto">
        <Header username={username} role={role} />

        <div className="space-y-6 max-w-6xl">
          {/* Page Title & Filter Bar */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Traffic Analytics & Insights</h1>
              <p className="text-xs text-gray-400 mt-1">
                Real-time traffic flow metrics, violation trends, and congestion analytics.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center bg-[#25283c] border border-white/10 rounded-xl px-3 py-1.5 text-xs text-gray-300">
                <Calendar size={14} className="mr-2 text-purple-400" />
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="bg-transparent focus:outline-none cursor-pointer"
                >
                  <option value="24h" className="bg-[#25283c]">Last 24 Hours</option>
                  <option value="7d" className="bg-[#25283c]">Last 7 Days</option>
                  <option value="30d" className="bg-[#25283c]">Last 30 Days</option>
                </select>
              </div>

              <button className="bg-[#a855f7] hover:bg-[#9333ea] text-white text-xs font-bold px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all shadow-lg hover:shadow-purple-500/20">
                <Download size={14} /> Export Report
              </button>
            </div>
          </div>

          {/* Key Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[#25283c] border border-white/5 p-5 rounded-2xl shadow-xl space-y-2">
              <div className="flex justify-between items-center text-gray-400">
                <span className="text-xs font-medium">Total Vehicles</span>
                <Car size={18} className="text-[#00d2ff]" />
              </div>
              <p className="text-2xl font-bold">142,890</p>
              <p className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
                <TrendingUp size={12} /> +12.4% vs last week
              </p>
            </div>

            <div className="bg-[#25283c] border border-white/5 p-5 rounded-2xl shadow-xl space-y-2">
              <div className="flex justify-between items-center text-gray-400">
                <span className="text-xs font-medium">Avg. Flow Speed</span>
                <Clock size={18} className="text-emerald-400" />
              </div>
              <p className="text-2xl font-bold">42 km/h</p>
              <p className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
                <TrendingUp size={12} /> +4.1% vs last week
              </p>
            </div>

            <div className="bg-[#25283c] border border-white/5 p-5 rounded-2xl shadow-xl space-y-2">
              <div className="flex justify-between items-center text-gray-400">
                <span className="text-xs font-medium">Detected Violations</span>
                <AlertTriangle size={18} className="text-amber-400" />
              </div>
              <p className="text-2xl font-bold">1,284</p>
              <p className="text-xs text-rose-400 flex items-center gap-1 font-medium">
                <TrendingUp size={12} /> +8.2% vs last week
              </p>
            </div>

            <div className="bg-[#25283c] border border-white/5 p-5 rounded-2xl shadow-xl space-y-2">
              <div className="flex justify-between items-center text-gray-400">
                <span className="text-xs font-medium">Congestion Index</span>
                <BarChart3 size={18} className="text-[#a855f7]" />
              </div>
              <p className="text-2xl font-bold">Low (28%)</p>
              <p className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
                -3.5% vs last week
              </p>
            </div>
          </div>

          {/* Visual Data Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Traffic Volume Chart Card */}
            <div className="lg:col-span-2 bg-[#25283c] border border-white/5 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-base font-bold text-white">Hourly Vehicle Volume</h2>
                  <p className="text-xs text-gray-400">Peak hour comparison across main corridors</p>
                </div>
              </div>

              {/* CSS Bar Chart Simulation */}
              <div className="h-64 flex items-end justify-between gap-2 pt-8 pb-2 px-2 border-b border-white/10">
                {[
                  { time: '06:00', val: '40%' },
                  { time: '08:00', val: '85%' },
                  { time: '10:00', val: '65%' },
                  { time: '12:00', val: '50%' },
                  { time: '14:00', val: '55%' },
                  { time: '16:00', val: '75%' },
                  { time: '18:00', val: '95%' },
                  { time: '20:00', val: '60%' },
                  { time: '22:00', val: '35%' },
                ].map((item, idx) => (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                    <div
                      style={{ height: item.val }}
                      className="w-full max-w-[32px] bg-gradient-to-t from-[#a855f7] to-[#00d2ff] rounded-t-lg transition-all group-hover:brightness-125"
                    />
                    <span className="text-[10px] text-gray-400">{item.time}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Violation Breakdown Card */}
            <div className="bg-[#25283c] border border-white/5 rounded-2xl p-6 shadow-xl space-y-4">
              <h2 className="text-base font-bold text-white">Violation Distribution</h2>
              
              <div className="space-y-4 pt-2">
                {[
                  { type: 'Speed Limit Violations', percentage: 48, count: 616, color: 'bg-amber-400' },
                  { type: 'Red Light Jump', percentage: 26, count: 334, color: 'bg-rose-500' },
                  { type: 'No Helmet / Seatbelt', percentage: 16, count: 205, color: 'bg-purple-500' },
                  { type: 'Wrong Side Driving', percentage: 10, count: 129, color: 'bg-sky-400' },
                ].map((item, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-300 font-medium">{item.type}</span>
                      <span className="text-gray-400">{item.count} ({item.percentage}%)</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${item.color} rounded-full`}
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
