'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { Card } from '@/components/Card';
import { Radio, PlusCircle, Users, Navigation } from 'lucide-react';

export default function DashboardPage() {
  const [role, setRole] = useState('Public');
  const [username, setUsername] = useState('USER');

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Public');
    setUsername(localStorage.getItem('username') || 'USER');
  }, []);

  return (
    <div className="flex min-h-screen bg-[#0d1117] text-white">
      <Sidebar role={role} />

      <main className="flex-1 p-8 overflow-y-auto">
        <Header username={username} role={role} />

        <div className="space-y-6">
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card title="Current Congestion Index" value="Moderate (42%)" valueColor="text-amber-400" />
            <Card title="Active Road Incidents" value="2 Reported" valueColor="text-rose-500" />
            <Card title="Est. Average Delay" value="+8 mins" valueColor="text-cyan-400" />
          </div>

          {/* ADMIN & OPERATOR ACTION PANEL */}
          {(role === 'Admin' || role === 'Operator' || role === 'Traffic Operator') && (
            <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-2xl flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <span className="text-sm font-semibold text-gray-200">
                  Control Panel Actions Available for {role === 'Admin' ? 'Admins' : 'Operators'}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/incidents"
                  className="bg-[#00d2ff] hover:bg-[#00b8e6] text-black font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-all"
                >
                  <PlusCircle size={15} /> + Log Incident
                </Link>

                {role === 'Admin' && (
                  <Link
                    href="/users"
                    className="bg-[#a855f7] hover:bg-[#9333ea] text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-all"
                  >
                    <Users size={15} /> Manage System Users
                  </Link>
                )}
              </div>
            </div>
          )}

          {/* AI CONGESTION FORECAST PANEL */}
          <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Radio size={18} className="text-[#1f6feb]" />
                <h2 className="text-lg font-bold text-white">AI Congestion Forecast & Route Insights</h2>
              </div>
              <span className="bg-[#1f6feb]/20 text-[#58a6ff] text-xs px-3 py-1 rounded-full border border-[#1f6feb]/40">
                Live AI Prediction
              </span>
            </div>
            <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">
              <p className="text-xs font-bold text-gray-300 uppercase mb-1">Peak Hour Delay Forecast</p>
              <p className="text-sm text-gray-400">
                JM Road Corridor expected to experience high congestion at <span className="text-amber-400 font-bold">17:30</span>. Status: <span className="text-emerald-400 font-semibold">Normal</span>
              </p>
            </div>
          </div>

          {/* PUBLIC ROLE: SUGGESTED TRAVEL ROUTES */}
          {role === 'Public' && (
            <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl space-y-4">
              <div className="flex items-center gap-2">
                <Navigation size={18} className="text-[#58a6ff]" />
                <h2 className="text-lg font-bold text-white">Recommended Travel Routes</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d] space-y-2">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Fastest Route
                  </span>
                  <h4 className="font-bold text-white text-sm">FC Road Bypass via Model Colony</h4>
                  <p className="text-xs text-gray-400">Est. Time: 12 mins (Saves ~10 mins vs. JM Road)</p>
                </div>
                <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d] space-y-2">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    Moderate Traffic
                  </span>
                  <h4 className="font-bold text-white text-sm">Karve Road to Deccan Gymkhana</h4>
                  <p className="text-xs text-gray-400">Est. Time: 18 mins (Standard flow)</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
