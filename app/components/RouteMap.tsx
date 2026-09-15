"use client";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const markerIcon = new L.Icon({
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export default function RouteMap() {
  const kolkata: [number, number] = [22.5726, 88.3639];

  return (
    <div className="h-[500px] w-full">
      <MapContainer
        center={kolkata}
        zoom={12}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <Marker position={kolkata} icon={markerIcon}>
          <Popup>
            <strong>TrafficVision AI</strong>
            <br />
            Kolkata Traffic Monitoring
          </Popup>
        </Marker>

        <Circle
          center={kolkata}
          radius={1200}
          pathOptions={{
            color: "red",
            fillColor: "red",
            fillOpacity: 0.15,
          }}
        />
      </MapContainer>
    </div>
  );
}