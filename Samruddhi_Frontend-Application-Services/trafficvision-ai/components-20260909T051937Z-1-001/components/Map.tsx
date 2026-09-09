'use client';

import React from 'react';
import 'leaflet/dist/leaflet.css';
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css';
import 'leaflet-defaulticon-compatibility';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

export interface RoadNode {
  id: string;
  name: string;
  coords: string;
  lat: number;
  lng: number;
  status: 'Congested' | 'Moderate' | 'Flowing';
  count: string;
  density: string;
}

interface MapProps {
  nodes: RoadNode[];
  selectedNodeId?: string;
  onSelectNode: (node: RoadNode) => void;
}

export default function Map({ nodes, onSelectNode }: MapProps) {
  // Center default to Pune Center
  const defaultCenter: [number, number] = [18.5204, 73.8567];

  return (
    <div className="w-full h-64 rounded-xl overflow-hidden border border-[#30363d]">
      <MapContainer
        center={defaultCenter}
        zoom={12}
        scrollWheelZoom={true}
        className="w-full h-full z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {nodes.map((node) => (
          <Marker
            key={node.id}
            position={[node.lat, node.lng]}
            eventHandlers={{
              click: () => onSelectNode(node),
            }}
          >
            <Popup>
              <div className="text-black font-sans p-1">
                <h4 className="font-bold text-sm">{node.name}</h4>
                <p className="text-xs">Status: <b>{node.status}</b></p>
                <p className="text-xs">Density: {node.density}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
