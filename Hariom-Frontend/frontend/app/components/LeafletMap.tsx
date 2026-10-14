"use client";

import React, { useEffect, useRef } from "react";
import L from "leaflet";

export interface MapMarker {
  id?: string;
  position: [number, number];
  title: string;
  type: "origin" | "destination" | "corridor" | "incident" | "node" | "custom";
  category?: "transit" | "commercial" | "airport" | "arterial" | "tech_hub" | string;
  popupHtml?: string;
  onClick?: () => void;
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
  onMapClick?: (coords: [number, number]) => void;
  onSelectPoint?: (type: "origin" | "destination", coords: [number, number], label?: string) => void;
  selectionMode?: "none" | "origin" | "destination";
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
  onMapClick,
  onSelectPoint,
  selectionMode = "none",
  className = "",
  height = "450px",
}: LeafletMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);

  const onMapClickRef = useRef(onMapClick);
  onMapClickRef.current = onMapClick;

  const onSelectPointRef = useRef(onSelectPoint);
  onSelectPointRef.current = onSelectPoint;

  const selectionModeRef = useRef(selectionMode);
  selectionModeRef.current = selectionMode;

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

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

    // Free OpenStreetMap Tile Layer with dark tiles
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

    // Handle Map Click for Dynamic Point Selection
    map.on("click", (e: L.LeafletMouseEvent) => {
      const coords: [number, number] = [
        Math.round(e.latlng.lat * 10000) / 10000,
        Math.round(e.latlng.lng * 10000) / 10000,
      ];

      const currentMode = selectionModeRef.current;
      if (currentMode === "origin") {
        if (onSelectPointRef.current) {
          onSelectPointRef.current("origin", coords, `Map Point (${coords[0].toFixed(4)}, ${coords[1].toFixed(4)})`);
        }
        return;
      }

      if (currentMode === "destination") {
        if (onSelectPointRef.current) {
          onSelectPointRef.current("destination", coords, `Map Point (${coords[0].toFixed(4)}, ${coords[1].toFixed(4)})`);
        }
        return;
      }

      // Default Click: notify parent & open interactive quick-action popup
      if (onMapClickRef.current) {
        onMapClickRef.current(coords);
      }

      const popupHtml = `
        <div style="padding: 6px 4px; min-width: 195px; font-family: system-ui, -apple-system, sans-serif;">
          <div style="display: flex; items-center: center; gap: 6px; margin-bottom: 4px;">
            <span style="font-size: 14px;">📍</span>
            <strong style="color: #38bdf8; font-size: 12px;">Map Coordinates Selected</strong>
          </div>
          <div style="font-size: 11px; font-family: monospace; color: #94a3b8; background: #020617; padding: 4px 6px; border-radius: 6px; margin-bottom: 8px; border: 1px solid #1e293b;">
            ${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}
          </div>
          <div style="display: flex; gap: 6px;">
            <button class="leaflet-popup-set-origin" data-lat="${coords[0]}" data-lng="${coords[1]}" style="flex: 1; background: #059669; hover: background: #10b981; color: white; border: none; padding: 6px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; transition: 0.2s;">
              🟢 Set Origin
            </button>
            <button class="leaflet-popup-set-dest" data-lat="${coords[0]}" data-lng="${coords[1]}" style="flex: 1; background: #e11d48; hover: background: #f43f5e; color: white; border: none; padding: 6px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; transition: 0.2s;">
              🏁 Set Dest
            </button>
          </div>
        </div>
      `;

      L.popup({ offset: [0, -10] })
        .setLatLng(e.latlng)
        .setContent(popupHtml)
        .openOn(map);
    });

    // Delegate click events inside Leaflet Popups
    map.on("popupopen", (e) => {
      const popupNode = e.popup.getElement();
      if (!popupNode) return;

      const originBtn = popupNode.querySelector<HTMLButtonElement>(".leaflet-popup-set-origin");
      if (originBtn) {
        originBtn.onclick = (event) => {
          event.stopPropagation();
          const lat = parseFloat(originBtn.dataset.lat || "0");
          const lng = parseFloat(originBtn.dataset.lng || "0");
          const label = originBtn.dataset.label || `Map Point (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
          if (onSelectPointRef.current) {
            onSelectPointRef.current("origin", [lat, lng], label);
          }
          map.closePopup();
        };
      }

      const destBtn = popupNode.querySelector<HTMLButtonElement>(".leaflet-popup-set-dest");
      if (destBtn) {
        destBtn.onclick = (event) => {
          event.stopPropagation();
          const lat = parseFloat(destBtn.dataset.lat || "0");
          const lng = parseFloat(destBtn.dataset.lng || "0");
          const label = destBtn.dataset.label || `Map Point (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
          if (onSelectPointRef.current) {
            onSelectPointRef.current("destination", [lat, lng], label);
          }
          map.closePopup();
        };
      }
    });

    // Fix leaflet tile rendering issue on initial load
    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Cursor Mode Management
  useEffect(() => {
    if (mapContainerRef.current) {
      if (selectionMode === "origin" || selectionMode === "destination") {
        mapContainerRef.current.style.cursor = "crosshair";
      } else {
        mapContainerRef.current.style.cursor = "";
      }
    }
  }, [selectionMode]);

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
      let iconSize: [number, number] = [32, 32];
      let iconAnchor: [number, number] = [16, 16];

      if (marker.type === "origin") {
        iconHtml = `
          <div style="background: #10b981; border: 2.5px solid #ffffff; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 18px rgba(16, 185, 129, 0.9); color: white; font-size: 15px; font-weight: bold; animation: pulse-slow 2s infinite;">
            🟢
          </div>
        `;
        iconSize = [34, 34];
        iconAnchor = [17, 17];
      } else if (marker.type === "destination") {
        iconHtml = `
          <div style="background: #ef4444; border: 2.5px solid #ffffff; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 18px rgba(239, 68, 68, 0.9); color: white; font-size: 15px; font-weight: bold; animation: pulse-slow 2s infinite;">
            🏁
          </div>
        `;
        iconSize = [34, 34];
        iconAnchor = [17, 17];
      } else if (marker.type === "node") {
        // Predefined City Landmark Corridor Node
        const catIcons: Record<string, string> = {
          transit: "🚆",
          commercial: "🏢",
          airport: "✈️",
          tech_hub: "💻",
          arterial: "🛣️",
        };
        const nodeIcon = catIcons[marker.category || ""] || "📍";

        iconHtml = `
          <div style="background: rgba(15, 23, 42, 0.9); border: 2px solid #06b6d4; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px rgba(6, 182, 212, 0.6); font-size: 12px; cursor: pointer; transition: transform 0.2s;" title="${marker.title}">
            ${nodeIcon}
          </div>
        `;
        iconSize = [28, 28];
        iconAnchor = [14, 14];
      } else if (marker.type === "incident") {
        iconHtml = `
          <div style="background: #f59e0b; border: 2px solid #ffffff; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px rgba(245, 158, 11, 0.8); font-size: 12px;">
            ⚠️
          </div>
        `;
        iconSize = [28, 28];
        iconAnchor = [14, 14];
      } else {
        iconHtml = `
          <div style="background: #0f172a; border: 2px solid #06b6d4; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(6, 182, 212, 0.6); font-size: 11px; color: #06b6d4;">
            📍
          </div>
        `;
        iconSize = [26, 26];
        iconAnchor = [13, 13];
      }

      const customIcon = L.divIcon({
        html: iconHtml,
        className: "custom-leaflet-marker",
        iconSize,
        iconAnchor,
        popupAnchor: [0, -16],
      });

      const leafletMarker = L.marker(marker.position, { icon: customIcon });

      if (marker.popupHtml) {
        leafletMarker.bindPopup(marker.popupHtml);
      } else if (marker.type === "node") {
        const catIcons: Record<string, string> = {
          transit: "Transit Hub",
          commercial: "Business District",
          airport: "Airport Highway",
          tech_hub: "Tech Park",
          arterial: "Arterial Expressway",
        };
        const catLabel = catIcons[marker.category || ""] || "Network Node";

        leafletMarker.bindPopup(`
          <div style="padding: 4px; min-width: 200px; font-family: system-ui, sans-serif;">
            <div style="font-weight: bold; font-size: 12px; color: #f1f5f9; margin-bottom: 2px;">${marker.title}</div>
            <div style="font-size: 10px; color: #38bdf8; text-transform: uppercase; margin-bottom: 6px;">${catLabel}</div>
            <div style="font-size: 11px; font-family: monospace; color: #94a3b8; background: #020617; padding: 3px 6px; border-radius: 4px; margin-bottom: 8px; border: 1px solid #1e293b;">
              ${marker.position[0].toFixed(4)}, ${marker.position[1].toFixed(4)}
            </div>
            <div style="display: flex; gap: 6px;">
              <button class="leaflet-popup-set-origin" data-lat="${marker.position[0]}" data-lng="${marker.position[1]}" data-label="${marker.title}" style="flex: 1; background: #059669; color: white; border: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer;">
                🟢 Set Origin
              </button>
              <button class="leaflet-popup-set-dest" data-lat="${marker.position[0]}" data-lng="${marker.position[1]}" data-label="${marker.title}" style="flex: 1; background: #e11d48; color: white; border: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer;">
                🏁 Set Dest
              </button>
            </div>
          </div>
        `);
      } else {
        leafletMarker.bindPopup(`
          <div style="padding: 4px; font-family: sans-serif;">
            <div style="font-weight: bold; font-size: 12px; color: #f1f5f9;">${marker.title}</div>
            <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">${marker.type} node</div>
            <div style="font-size: 10px; font-family: monospace; color: #64748b; margin-top: 3px;">
              ${marker.position[0].toFixed(4)}, ${marker.position[1].toFixed(4)}
            </div>
          </div>
        `);
      }

      if (marker.onClick) {
        leafletMarker.on("click", marker.onClick);
      }

      layerGroup.addLayer(leafletMarker);
    });

    // Auto-fit bounds if we have multiple valid coordinates
    const allCoords: [number, number][] = [];
    markers.forEach((m) => {
      // Only fit bounds based on origin, destination and routes to prevent map zoom-out if all nodes are spread
      if (m.type === "origin" || m.type === "destination") {
        allCoords.push(m.position);
      }
    });
    routes.forEach((r) => r.coordinates.forEach((c) => allCoords.push(c)));

    if (allCoords.length > 1) {
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  }, [markers, routes, selectedRouteId, onRouteClick]);

  return (
    <div
      className={`relative w-full rounded-2xl overflow-hidden border border-slate-800 shadow-2xl transition-all ${className}`}
      style={{ height }}
    >
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
}
