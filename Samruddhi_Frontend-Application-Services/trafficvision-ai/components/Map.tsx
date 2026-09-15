'use client';

import { useEffect, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface MapProps {
  nodes?: any[];
  selectedNodeId?: string;
  onSelectNode?: (node: any) => void;
  startCoords?: [number, number];
  endCoords?: [number, number];
  routeGeometry?: [number, number][];
  routeColor?: string;
}

function ResizeMap() {
  const map = useMap();

  useEffect(() => {
    const resizeMap = () => {
      map.invalidateSize();
    };

    resizeMap();

    const timer = setTimeout(resizeMap, 300);

    window.addEventListener('resize', resizeMap);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', resizeMap);
    };
  }, [map]);

  return null;
}

function FitRoute({
  startCoords,
  endCoords,
  routeGeometry,
}: {
  startCoords?: [number, number];
  endCoords?: [number, number];
  routeGeometry?: [number, number][];
}) {
  const map = useMap();

  useEffect(() => {
    if (routeGeometry && routeGeometry.length > 0) {
      const bounds = L.latLngBounds(routeGeometry);
      map.fitBounds(bounds, { padding: [40, 40] });
    } else if (startCoords && endCoords) {
      const bounds = L.latLngBounds([startCoords, endCoords]);
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [map, startCoords, endCoords, routeGeometry]);

  return null;
}

export default function Map({
  nodes = [],
  selectedNodeId = '',
  onSelectNode = () => {},
  startCoords,
  endCoords,
  routeGeometry = [],
  routeColor = '#1f6feb',
}: MapProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);

    delete (L.Icon.Default.prototype as any)._getIconUrl;

    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl:
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl:
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    });

    return () => {
      setIsMounted(false);
    };
  }, []);

  if (!isMounted) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-[#161b22] text-gray-400">
        Loading Map...
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <MapContainer
  key={`${startCoords?.join('-')}-${endCoords?.join('-')}`}
        center={[18.5204, 73.8567]}
        zoom={12}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <ResizeMap />

        <FitRoute
          startCoords={startCoords}
          endCoords={endCoords}
          routeGeometry={routeGeometry}
        />

        {routeGeometry.length > 0 && (
          <Polyline
            positions={routeGeometry}
            pathOptions={{
              color: routeColor,
              weight: 7,
              opacity: 0.9,
            }}
          />
        )}

        {startCoords && (
          <Marker position={startCoords}>
            <Popup>
              <strong>Origin</strong>
            </Popup>
          </Marker>
        )}

        {endCoords && (
          <Marker position={endCoords}>
            <Popup>
              <strong>Destination</strong>
            </Popup>
          </Marker>
        )}

        {nodes.map((node: any) => (
          <Marker
            key={node.id}
            position={node.coords}
            eventHandlers={{
              click: () => onSelectNode(node),
            }}
          >
            <Popup>
              <div className="text-xs text-gray-900">
                <p className="font-bold">{node.name}</p>

                {node.status && <p>Status: {node.status}</p>}

                {node.count !== undefined && (
                  <p>Vehicles: {node.count}</p>
                )}

                {node.density && <p>Density: {node.density}</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
