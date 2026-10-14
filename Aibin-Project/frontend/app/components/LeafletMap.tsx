"use client";

import React, { useEffect, useRef } from "react";
import L from "leaflet";

export interface MapMarker {
  position: [number, number];
  title: string;
  type: "origin" | "destination" | "corridor" | "incident";
  popupHtml?: string;
}

export interface MapRoute {
  id: string;
  coordinates: [number, number][];
  color: string;
  weight?: number;
  opacity?: number;
  dashArray?: string;
  popupHtml?: string;
}

interface LeafletMapProps {
  center?: [number, number];
  zoom?: number;
  markers?: MapMarker[];
  routes?: MapRoute[];
  selectedRouteId?: string;
  onRouteClick?: (routeId: string) => void;
  className?: string;
  height?: string;
}

export default function LeafletMap({
  center = [12.9716, 77.5946],
  zoom = 12,
  markers = [],
  routes = [],
  selectedRouteId,
  onRouteClick,
  className = "",
  height = "450px",
}: LeafletMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Check if map already initialized
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const map = L.map(mapContainerRef.current, {
      center,
      zoom,
      zoomControl: false,
    });

    L.control.zoom({ position: "bottomright" }).addTo(map);

    // Free OpenStreetMap Tile Layer (no key required) with dark tile class
    const tileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | TrafficVision AI',
      maxZoom: 19,
      className: "dark-tiles",
    });

    tileLayer.addTo(map);

    const layerGroup = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;
    layerGroupRef.current = layerGroup;

    // Fix leaflet tile rendering issue on initial load
    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Layers (Markers, Routes)
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();

    // 1. Render Routes (Polylines)
    routes.forEach((route) => {
      const isSelected = selectedRouteId === route.id;
      const polyline = L.polyline(route.coordinates, {
        color: route.color,
        weight: isSelected ? (route.weight || 6) + 3 : route.weight || 5,
        opacity: isSelected ? 1.0 : route.opacity || 0.75,
        dashArray: route.dashArray,
        lineCap: "round",
        lineJoin: "round",
      });

      if (route.popupHtml) {
        polyline.bindPopup(route.popupHtml);
      }

      polyline.on("click", () => {
        if (onRouteClick) onRouteClick(route.id);
      });

      layerGroup.addLayer(polyline);

      // Glow underlay for recommended / selected route
      if (isSelected) {
        const glowLine = L.polyline(route.coordinates, {
          color: route.color,
          weight: (route.weight || 6) + 8,
          opacity: 0.25,
          lineCap: "round",
        });
        layerGroup.addLayer(glowLine);
      }
    });

    // 2. Render Custom Markers
    markers.forEach((marker) => {
      let iconHtml = "";
      if (marker.type === "origin") {
        iconHtml = `
          <div style="background: #10b981; border: 2px solid #ffffff; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(16, 185, 129, 0.8); color: white; font-size: 14px; font-weight: bold;">
            🟢
          </div>
        `;
      } else if (marker.type === "destination") {
        iconHtml = `
          <div style="background: #ef4444; border: 2px solid #ffffff; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(239, 68, 68, 0.8); color: white; font-size: 14px; font-weight: bold;">
            🏁
          </div>
        `;
      } else if (marker.type === "incident") {
        iconHtml = `
          <div style="background: #f59e0b; border: 2px solid #ffffff; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px rgba(245, 158, 11, 0.8); font-size: 12px;">
            ⚠️
          </div>
        `;
      } else {
        iconHtml = `
          <div style="background: #0f172a; border: 2px solid #06b6d4; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(6, 182, 212, 0.6); font-size: 11px; color: #06b6d4;">
            📍
          </div>
        `;
      }

      const customIcon = L.divIcon({
        html: iconHtml,
        className: "custom-leaflet-marker",
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
      });

      const leafletMarker = L.marker(marker.position, { icon: customIcon });

      if (marker.popupHtml) {
        leafletMarker.bindPopup(marker.popupHtml);
      } else {
        leafletMarker.bindPopup(`
          <div style="padding: 4px; font-family: sans-serif;">
            <div style="font-weight: bold; font-size: 12px; color: #f1f5f9;">${marker.title}</div>
            <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">${marker.type} node</div>
          </div>
        `);
      }

      layerGroup.addLayer(leafletMarker);
    });

    // Auto-fit bounds if we have coordinates
    const allCoords: [number, number][] = [];
    markers.forEach((m) => allCoords.push(m.position));
    routes.forEach((r) => r.coordinates.forEach((c) => allCoords.push(c)));

    if (allCoords.length > 1) {
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  }, [markers, routes, selectedRouteId, onRouteClick]);

  return (
    <div
      className={`relative w-full rounded-2xl overflow-hidden border border-slate-800 shadow-2xl ${className}`}
      style={{ height }}
    >
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
}
