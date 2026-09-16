"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import type { TimeSeriesResponse } from "@/lib/api";

interface ClimateChartProps {
  data: TimeSeriesResponse | null;
  loading: boolean;
}

export default function ClimateChart({
  data,
  loading,
}: ClimateChartProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-white/10 bg-black/40 p-5">
        <div className="text-sm text-slate-400">
          Loading time series...
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const chartData = Object.entries(
    data.time_series,
  ).map(([timestamp, values]) => {
    const temperature =
      values.temperature_2m?.value;

    return {
      time: new Date(timestamp).toLocaleTimeString(
        [],
        {
          hour: "2-digit",
          minute: "2-digit",
        },
      ),
      temperature:
        temperature !== undefined
          ? temperature - 273.15
          : null,
    };
  });

  return (
    <div className="rounded-2xl border border-white/10 bg-black/40 p-5">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
          Historical Observation
        </p>

        <h2 className="mt-1 text-xl font-semibold text-white">
          Temperature Timeline
        </h2>
      </div>

      <div className="h-72">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              strokeOpacity={0.15}
            />

            <XAxis
              dataKey="time"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
            />

            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              unit="°C"
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="temperature"
              strokeWidth={2}
              dot
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}