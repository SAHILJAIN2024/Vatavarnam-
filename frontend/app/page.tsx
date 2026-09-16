"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import ClimatePanel from "@/components/ClimatePanel";
import ClimateChart from "@/components/ClimateChart";

import {
  getClimateGrid,
  getClimateMetrics,
  getClimateTimeSeries,
  type GridFeature,
  type MetricsResponse,
  type TimeSeriesResponse,
} from "@/lib/api";

const ClimateMap = dynamic(
  () => import("@/components/ClimateMap"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center bg-slate-950 text-slate-400">
        Loading climate map...
      </div>
    ),
  },
);

export default function Home() {
  const [grid, setGrid] = useState<GridFeature[]>(
    [],
  );

  const [metrics, setMetrics] =
    useState<MetricsResponse | null>(null);

  const [timeSeries, setTimeSeries] =
    useState<TimeSeriesResponse | null>(null);

  const [loadingGrid, setLoadingGrid] =
    useState(true);

  const [loadingLocation, setLoadingLocation] =
    useState(false);

  const [error, setError] = useState<
    string | null
  >(null);

  useEffect(() => {
    async function loadGrid() {
      try {
        setLoadingGrid(true);
        setError(null);

        const response =
          await getClimateGrid(
            "temperature_2m",
          );

        setGrid(response.features);
      } catch (err) {
        console.error(err);

        setError(
          "Unable to load climate grid. Make sure the FastAPI backend is running.",
        );
      } finally {
        setLoadingGrid(false);
      }
    }

    loadGrid();
  }, []);

  async function handleLocationSelect(
    latitude: number,
    longitude: number,
  ) {
    try {
      setLoadingLocation(true);
      setError(null);

      const [metricsData, timeSeriesData] =
        await Promise.all([
          getClimateMetrics(
            latitude,
            longitude,
          ),
          getClimateTimeSeries(
            latitude,
            longitude,
          ),
        ]);

      setMetrics(metricsData);
      setTimeSeries(timeSeriesData);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to retrieve climate information for this location.",
      );
    } finally {
      setLoadingLocation(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#050816] text-white">
      {/* Header */}

      <header className="border-b border-white/10 bg-black/30 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1800px] items-center justify-between px-6 py-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.8)]" />

              <h1 className="text-xl font-semibold tracking-tight">
                Vatavarnam
              </h1>
            </div>

            <p className="mt-1 text-xs text-slate-500">
              AI-Powered Digital Twin of India&apos;s
              Climate
            </p>
          </div>

          <div className="hidden rounded-full border border-cyan-400/20 bg-cyan-400/5 px-4 py-2 text-xs text-cyan-300 md:block">
            LIVE CLIMATE DATA
          </div>
        </div>
      </header>

      {/* Main */}

      <div className="mx-auto grid max-w-[1800px] gap-5 p-5 lg:grid-cols-[1fr_390px]">
        {/* Map */}

        <section className="relative min-h-[650px] overflow-hidden rounded-3xl border border-white/10 bg-slate-950 shadow-2xl">
          {loadingGrid && (
            <div className="absolute left-5 top-5 z-[1000] rounded-xl border border-white/10 bg-black/70 px-4 py-3 text-sm text-slate-300 backdrop-blur-xl">
              Loading climate grid...
            </div>
          )}

          {error && (
            <div className="absolute left-5 right-5 top-5 z-[1000] rounded-xl border border-red-400/20 bg-red-950/80 px-4 py-3 text-sm text-red-200 backdrop-blur-xl">
              {error}
            </div>
          )}

          <ClimateMap
            features={grid}
            onLocationSelect={
              handleLocationSelect
            }
          />
        </section>

        {/* Sidebar */}

        <aside className="space-y-5">
          <ClimatePanel
            data={metrics}
            loading={loadingLocation}
          />

          <ClimateChart
            data={timeSeries}
            loading={loadingLocation}
          />
        </aside>
      </div>
    </main>
  );
}