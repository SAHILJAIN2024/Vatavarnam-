"use client";

import type { MetricsResponse } from "@/lib/api";

interface ClimatePanelProps {
  data: MetricsResponse | null;
  loading: boolean;
}

export default function ClimatePanel({
  data,
  loading,
}: ClimatePanelProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/40 p-5 backdrop-blur-xl">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
          Location Intelligence
        </p>

        <h2 className="mt-1 text-xl font-semibold text-white">
          Climate Conditions
        </h2>
      </div>

      {loading && (
        <div className="text-sm text-slate-400">
          Loading climate data...
        </div>
      )}

      {!loading && !data && (
        <div className="rounded-xl border border-dashed border-white/10 p-5 text-center text-sm text-slate-500">
          Click a climate grid point on the map
          to inspect its conditions.
        </div>
      )}

      {data && !loading && (
        <div className="space-y-4">
          <div className="rounded-xl bg-white/5 p-4">
            <div className="text-xs text-slate-500">
              Grid Location
            </div>

            <div className="mt-1 font-mono text-sm text-white">
              {data.location.nearest_grid_point.latitude.toFixed(
                2,
              )}
              {" , "}
              {data.location.nearest_grid_point.longitude.toFixed(
                2,
              )}
            </div>

            <div className="mt-1 text-xs text-slate-500">
              Distance from selected point:{" "}
              {data.location.nearest_grid_point.distance_meters.toFixed(
                0,
              )}{" "}
              m
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              label="Temperature"
              value={
                data.derived_metrics
                  .temperature_2m?.value
              }
              unit="°C"
            />

            <MetricCard
              label="Pressure"
              value={
                data.derived_metrics
                  .surface_pressure?.value
              }
              unit="hPa"
            />

            <MetricCard
              label="Wind Speed"
              value={
                data.derived_metrics.wind_10m
                  ?.speed.value
              }
              unit="m/s"
            />

            <MetricCard
              label="Wind Direction"
              value={
                data.derived_metrics.wind_10m
                  ?.direction.value
              }
              unit="°"
            />

            <MetricCard
              label="Boundary Layer"
              value={
                data.derived_metrics
                  .boundary_layer_height?.value
              }
              unit="m"
            />
          </div>

          <div className="border-t border-white/10 pt-4">
            <div className="text-xs text-slate-500">
              Observation
            </div>

            <div className="mt-1 text-sm text-slate-300">
              {new Date(
                data.timestamp,
              ).toLocaleString()}
            </div>

            <div className="mt-1 text-xs text-slate-500">
              {data.source} · {data.dataset_id}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  unit,
}: {
  label: string;
  value?: number;
  unit: string;
}) {
  return (
    <div className="rounded-xl bg-white/5 p-4">
      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className="mt-1 text-xl font-semibold text-white">
        {value !== undefined
          ? value.toFixed(2)
          : "—"}
        <span className="ml-1 text-xs font-normal text-slate-500">
          {unit}
        </span>
      </div>
    </div>
  );
}