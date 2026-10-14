"use client";

import dynamic from "next/dynamic";
import React from "react";
import type { MapMarker, MapRoute } from "./LeafletMap";

interface LeafletMapWrapperProps {
  center?: [number, number];
  zoom?: number;
  markers?: MapMarker[];
  routes?: MapRoute[];
  selectedRouteId?: string;
  onRouteClick?: (routeId: string) => void;
  className?: string;
  height?: string;
}

const DynamicLeafletMap = dynamic(() => import("./LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 flex flex-col items-center justify-center p-8 text-center min-h-[450px]">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-600/20 border border-cyan-500/40 text-cyan-400 mb-3 animate-pulse">
        <span className="text-2xl">🗺️</span>
      </div>
      <h4 className="text-sm font-bold text-slate-200">Initializing OpenStreetMap Carrier Engine...</h4>
      <p className="text-xs text-slate-500 mt-1">Connecting to free geographic tile layer and rendering route vectors</p>
    </div>
  ),
});

export default function LeafletMapWrapper(props: LeafletMapWrapperProps) {
  return <DynamicLeafletMap {...props} />;
}
