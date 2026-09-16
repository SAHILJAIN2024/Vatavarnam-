"use client";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import type { GridFeature } from "@/lib/api";

interface ClimateMapProps {
  features: GridFeature[];
  onLocationSelect: (
    latitude: number,
    longitude: number,
  ) => void;
}

function MapViewUpdater({
  latitude,
  longitude,
}: {
  latitude: number;
  longitude: number;
}) {
  const map = useMap();

  map.setView(
    [latitude, longitude],
    map.getZoom(),
  );

  return null;
}

function getTemperatureColor(value: number): string {
  if (value < 273.15) return "#2563eb";
  if (value < 278.15) return "#06b6d4";
  if (value < 283.15) return "#22c55e";
  if (value < 288.15) return "#eab308";
  if (value < 293.15) return "#f97316";

  return "#ef4444";
}

export default function ClimateMap({
  features,
  onLocationSelect,
}: ClimateMapProps) {
  const center: [number, number] = [
    22.5,
    79.0,
  ];

  return (
    <MapContainer
      center={center}
      zoom={5}
      scrollWheelZoom
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {features.map((feature) => {
        const [longitude, latitude] =
          feature.geometry.coordinates;

        return (
          <CircleMarker
            key={feature.properties.id}
            center={[latitude, longitude]}
            radius={5}
            pathOptions={{
              color: getTemperatureColor(
                feature.properties.value,
              ),
              fillColor: getTemperatureColor(
                feature.properties.value,
              ),
              fillOpacity: 0.75,
              weight: 1,
            }}
            eventHandlers={{
              click: () => {
                onLocationSelect(
                  latitude,
                  longitude,
                );
              },
            }}
          >
            <Popup>
              <div className="text-sm">
                <strong>
                  Climate Grid Point
                </strong>

                <div>
                  Latitude:{" "}
                  {latitude.toFixed(2)}
                </div>

                <div>
                  Longitude:{" "}
                  {longitude.toFixed(2)}
                </div>

                <div>
                  Value:{" "}
                  {feature.properties.value.toFixed(
                    2,
                  )}{" "}
                  {feature.properties.unit}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}