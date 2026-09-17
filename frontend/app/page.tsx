"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import ClimatePanel from "@/components/ClimatePanel";
import ClimateChart from "@/components/ClimateChart";

import {
  getClimateGrid,
  getClimateMetrics,
  getClimateTimeSeries,
  type ClimateVariable,
  type GridResponse,
  type MetricsResponse,
  type TimeSeriesResponse,
} from "@/lib/api";

const ClimateMap = dynamic(
  () => import("@/components/ClimateMap"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full min-h-[650px] items-center justify-center bg-slate-950 text-slate-400">
        Loading climate map...
      </div>
    ),
  },
);

export default function Home() {
  /* ====================================================
     Climate Grid
  ==================================================== */

  const [grid, setGrid] =
    useState<GridResponse | null>(null);

  const [
    selectedVariable,
    setSelectedVariable,
  ] = useState<ClimateVariable>(
    "temperature_2m",
  );

  /* ====================================================
     Location Intelligence
  ==================================================== */

  const [metrics, setMetrics] =
    useState<MetricsResponse | null>(null);

  const [timeSeries, setTimeSeries] =
    useState<TimeSeriesResponse | null>(null);

  /* ====================================================
     Loading / Error States
  ==================================================== */

  const [loadingGrid, setLoadingGrid] =
    useState(true);

  const [loadingLocation, setLoadingLocation] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  /* ====================================================
     Load Selected Climate Variable
  ==================================================== */

  useEffect(() => {
    let cancelled = false;

    async function loadGrid() {
      try {
        setLoadingGrid(true);
        setError(null);

        const result =
          await getClimateGrid(
            selectedVariable,
          );

        if (!cancelled) {
          setGrid(result);
        }
      } catch (err) {
        console.error(
          "Failed to load climate grid:",
          err,
        );

        if (!cancelled) {
          setError(
            "Unable to load the selected climate layer.",
          );
          setGrid(null);
        }
      } finally {
        if (!cancelled) {
          setLoadingGrid(false);
        }
      }
    }

    loadGrid();

    return () => {
      cancelled = true;
    };
  }, [selectedVariable]);

  /* ====================================================
     Map Location Selection
  ==================================================== */

  async function handleLocationSelect(
    latitude: number,
    longitude: number,
  ) {
    try {
      setLoadingLocation(true);
      setError(null);

      const [
        metricsData,
        timeSeriesData,
      ] = await Promise.all([
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
      console.error(
        "Failed to retrieve climate information:",
        err,
      );

      setError(
        "Unable to retrieve climate information for this location.",
      );
    } finally {
      setLoadingLocation(false);
    }
  }

  /* ====================================================
     Render
  ==================================================== */

  return (
    <main className="min-h-screen bg-[#050816] text-white">
      {/* ==================================================
         Header
      ================================================== */}

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

      {/* ==================================================
         Main Layout
      ================================================== */}

      <div className="mx-auto grid max-w-[1800px] gap-5 p-5 lg:grid-cols-[1fr_390px]">
        {/* =================================================
           Map
        ================================================= */}

        <section className="relative min-h-[650px] overflow-hidden rounded-3xl border border-white/10 bg-slate-950 shadow-2xl">
          {/* Variable Selector */}

          <div className="absolute left-5 top-5 z-[1001]">
            <div className="rounded-2xl border border-white/10 bg-black/80 p-3 shadow-2xl backdrop-blur-xl">
              <label
                htmlFor="climate-variable"
                className="mb-2 block text-[10px] uppercase tracking-[0.2em] text-cyan-400"
              >
                Climate Variable
              </label>

              <select
                id="climate-variable"
                value={selectedVariable}
                onChange={(event) =>
                  setSelectedVariable(
                    event.target
                      .value as ClimateVariable,
                  )
                }
                className="min-w-[250px] cursor-pointer rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan-400/50"
              >
                <option value="temperature_2m">
                  Temperature at 2m
                </option>

                <option value="surface_pressure">
                  Surface Pressure
                </option>

                <option value="wind_speed">
                  Wind Speed at 10m
                </option>

                <option value="wind_u_10m">
                  Wind U Component
                </option>

                <option value="wind_v_10m">
                  Wind V Component
                </option>

                <option value="boundary_layer_height">
                  Boundary Layer Height
                </option>
              </select>
            </div>
          </div>

          {/* Loading Indicator */}

          {loadingGrid && (
            <div className="absolute left-5 right-5 top-24 z-[1000] rounded-xl border border-cyan-400/20 bg-black/75 px-4 py-3 text-sm text-cyan-200 backdrop-blur-xl">
              Loading{" "}
              {selectedVariable.replaceAll(
                "_",
                " ",
              )}
              ...
            </div>
          )}

          {/* Error */}

          {error && (
            <div className="absolute left-5 right-5 top-5 z-[1000] rounded-xl border border-red-400/20 bg-red-950/85 px-4 py-3 text-sm text-red-200 backdrop-blur-xl">
              {error}
            </div>
          )}

          {/* Climate Map */}

          <ClimateMap
            data={grid}
            variable={selectedVariable}
            onLocationSelect={
              handleLocationSelect
            }
          />
        </section>

        {/* =================================================
           Sidebar
        ================================================= */}

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