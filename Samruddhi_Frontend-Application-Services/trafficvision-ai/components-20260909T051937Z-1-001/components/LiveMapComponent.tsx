'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { RoadNode } from './Map';

const DynamicMap = dynamic(() => import('./Map'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-64 bg-[#0d1117] border border-[#30363d] rounded-xl flex items-center justify-center text-gray-400 text-sm">
      Loading Dynamic Map Tiles...
    </div>
  ),
});

const defaultNodes: RoadNode[] = [
  { id: '1', name: 'JM Road Node', coords: '18.5204, 73.8567', lat: 18.5204, lng: 73.8567, status: 'Congested', count: '450 vehicles/min', density: '85%' },
  { id: '2', name: 'FC Road Node', coords: '18.5284, 73.8417', lat: 18.5284, lng: 73.8417, status: 'Flowing', count: '120 vehicles/min', density: '30%' },
  { id: '3', name: 'Karve Road Node', coords: '18.5074, 73.8277', lat: 18.5074, lng: 73.8277, status: 'Moderate', count: '280 vehicles/min', density: '55%' },
  { id: '4', name: 'Baner Main Node', coords: '18.559, 73.7868', lat: 18.559, lng: 73.7868, status: 'Flowing', count: '100 vehicles/min', density: '20%' },
];

export const LiveMapComponent: React.FC = () => {
  const [nodes, setNodes] = useState<RoadNode[]>(defaultNodes);
  const [selectedNode, setSelectedNode] = useState<RoadNode>(defaultNodes[0]);

  // Backend connection hook
  useEffect(() => {
    async function fetchBackendNodes() {
      try {
        const res = await fetch('http://localhost:5000/api/nodes'); // Change port to match your backend API URL
        if (res.ok) {
          const data: RoadNode[] = await res.json();
          setNodes(data);
          if (data.length > 0) setSelectedNode(data[0]);
        }
      } catch (err) {
        console.warn('Backend server disconnected. Fallback to mock data.', err);
      }
    }
    fetchBackendNodes();
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Column: Map + 4 Card Nodes */}
      <div className="lg:col-span-2 bg-[#161b22] border border-[#30363d] rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-gray-300">City Network Overlay (Pune Center)</h3>
          <span className="text-xs text-emerald-400 flex items-center gap-1.5 font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Live Stream Active
          </span>
        </div>

        {/* Dynamic Leaflet Map Area */}
        <DynamicMap nodes={nodes} selectedNodeId={selectedNode.id} onSelectNode={setSelectedNode} />

        {/* 2x2 Grid of Nodes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {nodes.map((node) => {
            const isSelected = selectedNode.id === node.id;
            return (
              <button
                key={node.id}
                onClick={() => setSelectedNode(node)}
                className={`p-4 rounded-xl border text-left transition-all flex items-center justify-between ${
                  isSelected
                    ? 'bg-[#1f6feb]/20 border-[#1f6feb] ring-1 ring-[#1f6feb]'
                    : 'bg-[#0d1117] border-[#30363d] hover:border-gray-500'
                }`}
              >
                <div>
                  <h4 className="font-bold text-sm text-white">{node.name}</h4>
                  <p className="text-xs text-gray-400 mt-1">Coords: {node.coords}</p>
                </div>
                <span
                  className={`text-xs px-2.5 py-1 rounded-md font-semibold ${
                    node.status === 'Congested'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : node.status === 'Moderate'
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  }`}
                >
                  {node.status}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right Column: Selected Node Stats */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-2xl p-6 space-y-4 h-fit">
        <div>
          <p className="text-xs font-bold text-[#58a6ff] uppercase tracking-wider">Selected Camera Node</p>
          <h3 className="text-xl font-bold mt-1 text-white">{selectedNode.name}</h3>
        </div>

        <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">
          <p className="text-xs text-gray-400 font-semibold mb-1">Congestion Status</p>
          <p
            className={`text-lg font-bold ${
              selectedNode.status === 'Congested'
                ? 'text-rose-400'
                : selectedNode.status === 'Moderate'
                ? 'text-amber-400'
                : 'text-emerald-400'
            }`}
          >
            {selectedNode.status}
          </p>
        </div>

        <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">
          <p className="text-xs text-gray-400 font-semibold mb-1">Current Vehicle Count</p>
          <p className="text-lg font-bold text-white">{selectedNode.count}</p>
        </div>

        <div className="bg-[#0d1117] p-4 rounded-xl border border-[#30363d]">
          <p className="text-xs text-gray-400 font-semibold mb-1">Calculated Density</p>
          <p className="text-lg font-bold text-white">{selectedNode.density}</p>
        </div>
      </div>
    </div>
  );
};
