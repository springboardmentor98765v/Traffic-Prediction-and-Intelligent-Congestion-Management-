'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { Radio, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Dynamic import for Leaflet map components to avoid SSR issues in Next.js
const MapContainer = dynamic(
  () => import('react-leaflet').then((m) => m.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((m) => m.TileLayer),
  { ssr: false }
);
const Marker = dynamic(
  () => import('react-leaflet').then((m) => m.Marker),
  { ssr: false }
);
const Popup = dynamic(
  () => import('react-leaflet').then((m) => m.Popup),
  { ssr: false }
);
const Polyline = dynamic(
  () => import('react-leaflet').then((m) => m.Polyline),
  { ssr: false }
);

interface TrafficNode {
  id: string;
  name: string;
  coords: [number, number];
  status: 'Congested' | 'Moderate' | 'Flowing';
  vehicleCount: number;
  density: number;
  // Polylines defining the road segment path
  routeCoords: [number, number][];
}

const trafficNodes: TrafficNode[] = [
  {
    id: 'jm-road',
    name: 'JM Road Node',
    coords: [18.5204, 73.8567],
    status: 'Congested',
    vehicleCount: 450,
    density: 85,
    routeCoords: [
      [18.5280, 73.8475],
      [18.5204, 73.8567],
      [18.5150, 73.8590],
    ],
  },
  {
    id: 'fc-road',
    name: 'FC Road Node',
    coords: [18.5284, 73.8417],
    status: 'Flowing',
    vehicleCount: 120,
    density: 25,
    routeCoords: [
      [18.5320, 73.8380],
      [18.5284, 73.8417],
      [18.5220, 73.8450],
    ],
  },
  {
    id: 'karve-road',
    name: 'Karve Road Node',
    coords: [18.5074, 73.8277],
    status: 'Moderate',
    vehicleCount: 280,
    density: 58,
    routeCoords: [
      [18.5120, 73.8350],
      [18.5074, 73.8277],
      [18.5020, 73.8200],
    ],
  },
  {
    id: 'baner-road',
    name: 'Baner Main Node',
    coords: [18.5590, 73.7868],
    status: 'Flowing',
    vehicleCount: 95,
    density: 18,
    routeCoords: [
      [18.5650, 73.7800],
      [18.5590, 73.7868],
      [18.5520, 73.7930],
    ],
  },
];

export default function LiveMapPage() {
  const [role, setRole] = useState('Admin');
  const [username, setUsername] = useState('USER');
  const [selectedNode, setSelectedNode] = useState<TrafficNode>(trafficNodes[0]);
  const [leafletLoaded, setLeafletLoaded] = useState(false);

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Admin');
    setUsername(localStorage.getItem('username') || 'USER');

    // Fix default Leaflet icon issues in React
    import('leaflet').then((L) => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      });
      setLeafletLoaded(true);
    });
  }, []);

  const getStatusColor = (status: TrafficNode['status']) => {
    switch (status) {
      case 'Congested':
        return {
          line: '#ef4444', // Vivid Red
          badge: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
          text: 'text-rose-400',
        };
      case 'Moderate':
        return {
          line: '#eab308', // Vivid Yellow / Amber
          badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
          text: 'text-amber-400',
        };
      case 'Flowing':
        return {
          line: '#22c55e', // Vivid Green
          badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
          text: 'text-emerald-400',
        };
    }
  };

  return (
    <div className="flex min-h-screen bg-[#1c1d28] text-white">
      <Sidebar role={role} />

      <main className="flex-1 p-8 overflow-y-auto">
        <Header username={username} role={role} />

        <div className="space-y-6 max-w-6xl">
          {/* Title */}
          <div>
            <h1 className="text-2xl font-bold text-white">Live Traffic Map</h1>
            <p className="text-xs text-gray-400 mt-1">
              Real-time monitoring of camera locations and active traffic nodes across the city network.
            </p>
          </div>

          {/* Main Map + Node Details Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Interactive Leaflet Map Container */}
            <div className="lg:col-span-2 bg-[#25283c] border border-white/5 rounded-2xl p-4 shadow-xl space-y-3">
              <div className="flex items-center justify-between px-2">
                <span className="text-sm font-bold text-white">City Network Overlay (Pune Center)</span>
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Live Stream Active
                </span>
              </div>

              <div className="h-[420px] w-full rounded-xl overflow-hidden border border-white/10 relative z-0">
                {leafletLoaded && (
                  <MapContainer
                    center={[18.5204, 73.8567]}
                    zoom={12}
                    scrollWheelZoom={true}
                    className="h-full w-full"
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {/* Color Coded Road Routes */}
                    {trafficNodes.map((node) => {
                      const colors = getStatusColor(node.status);
                      return (
                        <React.Fragment key={node.id}>
                          <Polyline
                            positions={node.routeCoords}
                            pathOptions={{
                              color: colors.line,
                              weight: selectedNode.id === node.id ? 8 : 5,
                              opacity: 0.85,
                            }}
                          />
                          <Marker
                            position={node.coords}
                            eventHandlers={{
                              click: () => setSelectedNode(node),
                            }}
                          >
                            <Popup>
                              <div className="text-xs font-sans text-gray-900">
                                <p className="font-bold">{node.name}</p>
                                <p>Status: <span className="font-semibold">{node.status}</span></p>
                                <p>Vehicles: {node.vehicleCount}/min</p>
                              </div>
                            </Popup>
                          </Marker>
                        </React.Fragment>
                      );
                    })}
                  </MapContainer>
                )}
              </div>

              {/* Map Legend */}
              <div className="flex items-center justify-around bg-[#1c1d28] p-3 rounded-xl border border-white/5 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-1.5 rounded-full bg-rose-500" />
                  <span className="text-gray-300">Congested Road</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-1.5 rounded-full bg-amber-400" />
                  <span className="text-gray-300">Moderate Road</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-1.5 rounded-full bg-emerald-500" />
                  <span className="text-gray-300">Flowing Road</span>
                </div>
              </div>
            </div>

            {/* Selected Camera Node Panel */}
            <div className="bg-[#25283c] border border-white/5 rounded-2xl p-6 shadow-xl space-y-6 flex flex-col justify-between">
              <div>
                <p className="text-[10px] font-bold tracking-wider text-purple-400 uppercase">
                  SELECTED CAMERA NODE
                </p>
                <h2 className="text-xl font-bold text-white mt-1">{selectedNode.name}</h2>

                <div className="mt-6 space-y-4">
                  <div>
                    <span className="text-xs text-gray-400 block mb-1">Congestion Status</span>
                    <span
                      className={`inline-block px-3 py-1 text-xs font-bold rounded-full border ${
                        getStatusColor(selectedNode.status).badge
                      }`}
                    >
                      {selectedNode.status}
                    </span>
                  </div>

                  <div>
                    <span className="text-xs text-gray-400 block">Current Vehicle Count</span>
                    <p className="text-2xl font-extrabold text-white mt-0.5">
                      {selectedNode.vehicleCount} <span className="text-xs font-normal text-gray-400">vehicles/min</span>
                    </p>
                  </div>

                  <div>
                    <span className="text-xs text-gray-400 block mb-1">Calculated Density</span>
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-bold">
                        <span className={getStatusColor(selectedNode.status).text}>{selectedNode.density}%</span>
                      </div>
                      <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full transition-all duration-500"
                          style={{
                            width: `${selectedNode.density}%`,
                            backgroundColor: getStatusColor(selectedNode.status).line,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-[#1c1d28] border border-white/5 rounded-xl text-xs text-gray-400 space-y-1">
                <p className="flex items-center gap-1.5 text-gray-300 font-medium">
                  <Radio size={14} className="text-emerald-400" /> Feed Status: Normal
                </p>
                <p className="text-[11px]">Latitude / Longitude: {selectedNode.coords.join(', ')}</p>
              </div>
            </div>
          </div>

          {/* Nodes List Bar */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {trafficNodes.map((node) => {
              const isSelected = selectedNode.id === node.id;
              const colors = getStatusColor(node.status);
              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    isSelected
                      ? 'bg-[#2a2d45] border-purple-500 shadow-lg shadow-purple-500/10'
                      : 'bg-[#25283c] border-white/5 hover:border-white/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-bold text-white">{node.name}</p>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${colors.badge}`}
                    >
                      {node.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">Coords: {node.coords.join(', ')}</p>
                </button>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
