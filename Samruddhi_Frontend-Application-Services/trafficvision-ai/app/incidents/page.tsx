'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';

interface Incident {
  id: string;
  code: string;
  roadName: string;
  type: string;
  severity: 'High' | 'Medium' | 'Low';
  reportedAgo: string;
}

const defaultIncidents: Incident[] = [
  {
    id: '1',
    code: 'INC-101',
    roadName: 'JM Road',
    type: 'Accident',
    severity: 'High',
    reportedAgo: '10 mins ago',
  },
  {
    id: '2',
    code: 'INC-102',
    roadName: 'Karve Road',
    type: 'Road Work',
    severity: 'Medium',
    reportedAgo: '25 mins ago',
  },
];

export default function IncidentsPage() {
  const [role, setRole] = useState('Traffic Operator');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [roadName, setRoadName] = useState('');
  const [type, setType] = useState('Accident');
  const [severity, setSeverity] = useState<'High' | 'Medium' | 'Low'>('Medium');

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Traffic Operator');
    const saved = localStorage.getItem('app_incidents');
    if (saved) {
      setIncidents(JSON.parse(saved));
    } else {
      setIncidents(defaultIncidents);
      localStorage.setItem('app_incidents', JSON.stringify(defaultIncidents));
    }
  }, []);

  const handleReportIncident = (e: React.FormEvent) => {
    e.preventDefault();
    if (!roadName.trim()) return;

    const newInc: Incident = {
      id: Date.now().toString(),
      code: `INC-${Math.floor(100 + Math.random() * 900)}`,
      roadName,
      type,
      severity,
      reportedAgo: 'Just now',
    };

    const updated = [newInc, ...incidents];
    setIncidents(updated);
    localStorage.setItem('app_incidents', JSON.stringify(updated));
    setRoadName('');
  };

  const handleResolve = (id: string) => {
    const updated = incidents.filter((item) => item.id !== id);
    setIncidents(updated);
    localStorage.setItem('app_incidents', JSON.stringify(updated));
  };

  return (
    <div className="flex min-h-screen bg-[#1c1d28] text-white">
      {/* Sidebar */}
      <Sidebar role={role} />

      {/* Main Content Area */}
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-6xl space-y-8">
          {/* Header Titles */}
          <div>
            <h1 className="text-2xl font-bold text-white tracking-wide">
              Incident & System Alerts Panel
            </h1>
            <p className="text-xs text-gray-400 mt-1 font-medium">
              Report active traffic events and manage control center alerts in real-time.
            </p>
          </div>

          {/* Two-Column Grid matching screenshot */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Left Card: Log New Incident */}
            <div className="lg:col-span-5 bg-[#25283c] rounded-2xl p-6 shadow-xl border border-white/5 space-y-6">
              <h2 className="text-lg font-bold text-white">Log New Incident</h2>

              <form onSubmit={handleReportIncident} className="space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-2">
                    Road / Node Name
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. FC Road"
                    value={roadName}
                    onChange={(e) => setRoadName(e.target.value)}
                    className="w-full bg-[#1b1e2e] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#00d2ff] placeholder-gray-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-2">
                    Incident Type
                  </label>
                  <select
                    value={type}
                    onChange={(e) => setType(e.target.value)}
                    className="w-full bg-[#1b1e2e] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#00d2ff]"
                  >
                    <option value="Accident">Accident</option>
                    <option value="Road Work">Road Work</option>
                    <option value="Heavy Congestion">Heavy Congestion</option>
                    <option value="Signal Failure">Signal Failure</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-2">
                    Severity Level
                  </label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value as 'High' | 'Medium' | 'Low')}
                    className="w-full bg-[#1b1e2e] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#00d2ff]"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <button
                  type="submit"
                  className="w-full bg-[#ffab00] hover:bg-[#e09600] text-black font-bold py-3.5 rounded-xl text-sm transition-colors shadow-md"
                >
                  Report Incident
                </button>
              </form>
            </div>

            {/* Right Card: Active System Incidents */}
            <div className="lg:col-span-7 bg-[#25283c] rounded-2xl p-6 shadow-xl border border-white/5 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Active System Incidents</h2>
                <span className="bg-[#5c2438] text-[#ff6b81] text-xs font-semibold px-3 py-1 rounded-full border border-[#ff6b81]/20">
                  {incidents.length} Active Alerts
                </span>
              </div>

              <div className="space-y-4">
                {incidents.map((inc) => (
                  <div
                    key={inc.id}
                    className="bg-[#1b1e2e] border border-white/5 p-4 rounded-xl flex items-center justify-between shadow-inner"
                  >
                    <div>
                      <h3 className="font-bold text-white text-sm">
                        {inc.roadName}{' '}
                        <span className="text-xs font-normal text-gray-400">({inc.code})</span>
                      </h3>
                      <p className="text-xs text-gray-400 mt-1">
                        Type: <span className="text-gray-200">{inc.type}</span> - Reported: {inc.reportedAgo}
                      </p>
                    </div>

                    <div className="flex items-center gap-3">
                      <span
                        className={`text-xs px-3 py-1 rounded-lg font-bold ${
                          inc.severity === 'High'
                            ? 'bg-[#8a1f2d] text-[#ff6b81] border border-[#ff6b81]/30'
                            : inc.severity === 'Medium'
                            ? 'bg-[#7a5814] text-[#ffc107] border border-[#ffc107]/30'
                            : 'bg-[#1b5e20] text-[#81c784] border border-[#81c784]/30'
                        }`}
                      >
                        {inc.severity}
                      </span>
                      <button
                        onClick={() => handleResolve(inc.id)}
                        className="bg-[#3b82f6] hover:bg-[#2563eb] text-white text-xs px-3.5 py-1.5 rounded-lg font-medium transition-colors"
                      >
                        Resolve
                      </button>
                    </div>
                  </div>
                ))}

                {incidents.length === 0 && (
                  <p className="text-center text-xs text-gray-400 py-8">
                    No active system incidents reported.
                  </p>
                )}
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
