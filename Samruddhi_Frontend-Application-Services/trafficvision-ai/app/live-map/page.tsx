'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { Radio, AlertCircle } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const API_BASE = 'http://127.0.0.1:8002/api/v1';

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

type TrafficStatus = 'Congested' | 'Moderate' | 'Flowing';

interface TrafficNode {
  id: string;
  name: string;
  coords: [number, number];
  status: TrafficStatus;
  vehicleCount: number;
  density: string;
}

interface BackendTrafficNode {
  id: string | number;
  name: string;
  lat: number;
  lng: number;
  status: string;
  count: number;
  density: string;
}

export default function LiveMapPage() {
  const [role, setRole] = useState('Admin');
  const [username, setUsername] = useState('USER');
  const [trafficNodes, setTrafficNodes] = useState<TrafficNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<TrafficNode | null>(null);
  const [leafletLoaded, setLeafletLoaded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Admin');
    setUsername(localStorage.getItem('username') || 'USER');

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

  useEffect(() => {
    let cancelled = false;

    const loadNodes = async () => {
      try {
        const response = await fetch(`${API_BASE}/traffic/nodes`, {
          cache: 'no-store',
        });

        if (!response.ok) {
          throw new Error(`Backend returned HTTP ${response.status}`);
        }

        const data: BackendTrafficNode[] = await response.json();

        const nodes: TrafficNode[] = data
          .filter(
            (item) =>
              Number.isFinite(Number(item.lat)) &&
              Number.isFinite(Number(item.lng))
          )
          .map((item) => ({
            id: String(item.id),
            name: item.name,
            coords: [Number(item.lat), Number(item.lng)],
            status: (() => {
              const status = String(item.status).toUpperCase();
              if (['HIGH', 'HEAVY', 'CONGESTED'].includes(status)) return 'Congested' as const;
              if (['MEDIUM', 'MODERATE'].includes(status)) return 'Moderate' as const;
              return 'Flowing' as const;
            })(),
            vehicleCount: Number(item.count) || 0,
            density: item.density || 'Unknown',
          }));

        if (!cancelled) {
          setTrafficNodes(nodes);
          setSelectedNode((previous) => {
            if (!nodes.length) return null;
            return nodes.find((node) => node.id === previous?.id) || nodes[0];
          });
          setError('');
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Could not load traffic data.'
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadNodes();
    const timer = window.setInterval(loadNodes, 30000);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const getStatusColor = (status: TrafficStatus) => {
    switch (status) {
      case 'Congested':
        return {
          line: '#ef4444',
          badge: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
          text: 'text-rose-400',
        };
      case 'Moderate':
        return {
          line: '#eab308',
          badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
          text: 'text-amber-400',
        };
      default:
        return {
          line: '#22c55e',
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
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold">Live Traffic Map</h1>
              <p className="text-sm text-gray-400 mt-1">
                Road status from the TrafficVision backend
              </p>
            </div>
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Auto-refresh: 30 seconds
            </span>
          </div>

          {error && (
            <div className="flex items-start gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
              <AlertCircle size={18} className="mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold">Unable to refresh live traffic</p>
                <p>{error}</p>
                <p className="mt-1 text-xs">
                  Check that the backend is running on port 8002.
                </p>
              </div>
            </div>
          )}

          {loading && (
            <p className="text-sm text-gray-400">Loading roads from backend...</p>
          )}

          {!loading && !error && trafficNodes.length === 0 && (
            <div className="rounded-xl border border-white/10 bg-[#25283c] p-5 text-sm text-gray-300">
              The backend returned no road nodes with traffic records. Record
              traffic data for a road, then refresh this page.
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-[#25283c] border border-white/5 rounded-2xl p-4 shadow-xl space-y-3">
              <div className="flex items-center justify-between px-2">
                <span className="text-sm font-bold text-white">
                  Chennai Road Network
                </span>
                <span className="text-xs text-gray-400">
                  {trafficNodes.length} road(s) from API
                </span>
              </div>

              <div className="h-[420px] w-full rounded-xl overflow-hidden border border-white/10 relative z-0">
                {leafletLoaded && (
                  <MapContainer
                    center={[13.0569, 80.2425]}
                    zoom={12}
                    scrollWheelZoom={true}
                    className="h-full w-full"
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {trafficNodes.map((node) => {
                      const colors = getStatusColor(node.status);
                      return (
                        <Marker
                          key={node.id}
                          position={node.coords}
                          eventHandlers={{
                            click: () => setSelectedNode(node),
                          }}
                        >
                          <Popup>
                            <div className="text-xs font-sans text-gray-900">
                              <p className="font-bold">{node.name}</p>
                              <p>Status: {node.status}</p>
                              <p>Vehicles: {node.vehicleCount}</p>
                              <p>Density: {node.density}</p>
                            </div>
                          </Popup>
                        </Marker>
                      );
                    })}
                  </MapContainer>
                )}
              </div>

              <div className="flex flex-wrap items-center justify-around gap-3 bg-[#1c1d28] p-3 rounded-xl border border-white/5 text-xs">
                {(['Congested', 'Moderate', 'Flowing'] as TrafficStatus[]).map(
                  (status) => (
                    <div key={status} className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getStatusColor(status).line }}
                      />
                      <span className="text-gray-300">
                        {status === 'Flowing' ? 'Clear / Flowing' : status}
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="bg-[#25283c] border border-white/5 rounded-2xl p-6 shadow-xl space-y-6 flex flex-col justify-between">
              {selectedNode ? (
                <>
                  <div>
                    <p className="text-[10px] font-bold tracking-wider text-purple-400 uppercase">
                      SELECTED ROAD NODE
                    </p>
                    <h2 className="text-xl font-bold text-white mt-1">
                      {selectedNode.name}
                    </h2>

                    <div className="mt-6 space-y-4">
                      <div>
                        <span className="text-xs text-gray-400 block mb-1">
                          Congestion Status
                        </span>
                        <span
                          className={`inline-block px-3 py-1 text-xs font-bold rounded-full border ${getStatusColor(selectedNode.status).badge}`}
                        >
                          {selectedNode.status}
                        </span>
                      </div>

                      <div>
                        <span className="text-xs text-gray-400 block">
                          Vehicle Count
                        </span>
                        <p className="text-2xl font-extrabold text-white mt-0.5">
                          {selectedNode.vehicleCount}
                          <span className="text-xs font-normal text-gray-400">
                            {' '}vehicles
                          </span>
                        </p>
                      </div>

                      <div>
                        <span className="text-xs text-gray-400 block mb-1">
                          Calculated Density
                        </span>
                        <p className={`text-lg font-bold ${getStatusColor(selectedNode.status).text}`}>
                          {selectedNode.density}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-[#1c1d28] border border-white/5 rounded-xl text-xs text-gray-400 space-y-2">
                    <p className="flex items-center gap-1.5 text-gray-300 font-medium">
                      <Radio size={14} className="text-emerald-400" />
                      Feed Status: API connected
                    </p>
                    <p className="text-[11px]">
                      Latitude / Longitude: {selectedNode.coords.join(', ')}
                    </p>
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-400">
                  Select a road marker to view its traffic details.
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {trafficNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
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
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <p className="text-sm font-bold text-white">{node.name}</p>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${colors.badge}`}
                    >
                      {node.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">
                    Vehicles: {node.vehicleCount} · Density: {node.density}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Coordinates: {node.coords.join(', ')}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
