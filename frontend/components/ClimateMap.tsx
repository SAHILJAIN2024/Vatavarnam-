"use client";

import { useEffect, useMemo, useRef } from "react";

import {
  MapContainer,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

import type {
  ClimateVariable,
  GridResponse,
} from "@/lib/api";

/* =========================================================
   Types
========================================================= */

type ClimateMapProps = {
  data: GridResponse | null;

  variable: ClimateVariable;

  onLocationSelect: (
    latitude: number,
    longitude: number,
  ) => void;
};

type GridPoint = {
  latitude: number;
  longitude: number;
  value: number;
};

type BuiltGrid = {
  latitudes: number[];
  longitudes: number[];
  values: Float32Array;
};

/* =========================================================
   Variable Configuration
========================================================= */

type VariableConfig = {
  label: string;
  unit: string;
  min: number;
  max: number;

  stops: {
    value: number;
    color: [number, number, number];
  }[];
};

const VARIABLE_CONFIG: Record<
  ClimateVariable,
  VariableConfig
> = {
  temperature_2m: {
    label: "Temperature at 2m",
    unit: "°C",
    min: 0,
    max: 45,

    stops: [
      {
        value: 0,
        color: [49, 54, 149],
      },
      {
        value: 8,
        color: [69, 117, 180],
      },
      {
        value: 15,
        color: [171, 217, 233],
      },
      {
        value: 22,
        color: [255, 255, 191],
      },
      {
        value: 30,
        color: [253, 174, 97],
      },
      {
        value: 37,
        color: [244, 109, 67],
      },
      {
        value: 45,
        color: [215, 48, 39],
      },
    ],
  },

  surface_pressure: {
    label: "Surface Pressure",
    unit: "hPa",
    min: 900,
    max: 1050,

    stops: [
      {
        value: 900,
        color: [49, 54, 149],
      },
      {
        value: 940,
        color: [69, 117, 180],
      },
      {
        value: 980,
        color: [171, 217, 233],
      },
      {
        value: 1010,
        color: [255, 255, 191],
      },
      {
        value: 1030,
        color: [253, 174, 97],
      },
      {
        value: 1050,
        color: [215, 48, 39],
      },
    ],
  },

  wind_speed: {
    label: "10m Wind Speed",
    unit: "m/s",
    min: 0,
    max: 20,

    stops: [
      {
        value: 0,
        color: [49, 54, 149],
      },
      {
        value: 4,
        color: [69, 117, 180],
      },
      {
        value: 8,
        color: [171, 217, 233],
      },
      {
        value: 12,
        color: [255, 255, 191],
      },
      {
        value: 16,
        color: [253, 174, 97],
      },
      {
        value: 20,
        color: [215, 48, 39],
      },
    ],
  },

  wind_u_10m: {
    label: "10m Wind U Component",
    unit: "m/s",
    min: -15,
    max: 15,

    stops: [
      {
        value: -15,
        color: [49, 54, 149],
      },
      {
        value: -7,
        color: [69, 117, 180],
      },
      {
        value: 0,
        color: [255, 255, 191],
      },
      {
        value: 7,
        color: [244, 109, 67],
      },
      {
        value: 15,
        color: [215, 48, 39],
      },
    ],
  },

  wind_v_10m: {
    label: "10m Wind V Component",
    unit: "m/s",
    min: -15,
    max: 15,

    stops: [
      {
        value: -15,
        color: [49, 54, 149],
      },
      {
        value: -7,
        color: [69, 117, 180],
      },
      {
        value: 0,
        color: [255, 255, 191],
      },
      {
        value: 7,
        color: [244, 109, 67],
      },
      {
        value: 15,
        color: [215, 48, 39],
      },
    ],
  },

  boundary_layer_height: {
    label: "Boundary Layer Height",
    unit: "m",
    min: 0,
    max: 3000,

    stops: [
      {
        value: 0,
        color: [49, 54, 149],
      },
      {
        value: 500,
        color: [69, 117, 180],
      },
      {
        value: 1000,
        color: [171, 217, 233],
      },
      {
        value: 1500,
        color: [255, 255, 191],
      },
      {
        value: 2200,
        color: [253, 174, 97],
      },
      {
        value: 3000,
        color: [215, 48, 39],
      },
    ],
  },
};

/* =========================================================
   Convert Raw API Value
========================================================= */

function convertValue(
  value: number,
  variable: ClimateVariable,
): number {
  switch (variable) {
    case "temperature_2m":
      // Kelvin → Celsius
      return value - 273.15;

    case "surface_pressure":
      // Pascal → hectopascal
      return value / 100;

    case "wind_speed":
      return value;

    case "wind_u_10m":
      return value;

    case "wind_v_10m":
      return value;

    case "boundary_layer_height":
      return value;

    default:
      return value;
  }
}

/* =========================================================
   Color Interpolation
========================================================= */

function interpolateColor(
  value: number,
  config: VariableConfig,
): [number, number, number] {
  const stops = config.stops;

  if (value <= stops[0].value) {
    return stops[0].color;
  }

  if (
    value >=
    stops[stops.length - 1].value
  ) {
    return stops[stops.length - 1].color;
  }

  for (
    let i = 0;
    i < stops.length - 1;
    i++
  ) {
    const lower = stops[i];
    const upper = stops[i + 1];

    if (
      value >= lower.value &&
      value <= upper.value
    ) {
      const ratio =
        (value - lower.value) /
        (upper.value - lower.value);

      return [
        Math.round(
          lower.color[0] +
            (upper.color[0] -
              lower.color[0]) *
              ratio,
        ),

        Math.round(
          lower.color[1] +
            (upper.color[1] -
              lower.color[1]) *
              ratio,
        ),

        Math.round(
          lower.color[2] +
            (upper.color[2] -
              lower.color[2]) *
              ratio,
        ),
      ];
    }
  }

  return stops[0].color;
}

/* =========================================================
   Build Regular Climate Grid
========================================================= */

function buildGrid(
  data: GridResponse,
  variable: ClimateVariable,
): BuiltGrid | null {
  const points: GridPoint[] = data.features
    .map((feature) => {
      const [
        longitude,
        latitude,
      ] = feature.geometry.coordinates;

      return {
        latitude,
        longitude,
        value: convertValue(
          feature.properties.value,
          variable,
        ),
      };
    })
    .filter(
      (point) =>
        Number.isFinite(point.latitude) &&
        Number.isFinite(point.longitude) &&
        Number.isFinite(point.value),
    );

  if (!points.length) {
    return null;
  }

  /* -------------------------------------------------------
     Extract unique latitude / longitude coordinates
  ------------------------------------------------------- */

  const latitudes = [
    ...new Set(
      points.map(
        (point) => point.latitude,
      ),
    ),
  ].sort((a, b) => b - a);

  const longitudes = [
    ...new Set(
      points.map(
        (point) => point.longitude,
      ),
    ),
  ].sort((a, b) => a - b);

  /* -------------------------------------------------------
     Flat Float32Array for fast lookup
  ------------------------------------------------------- */

  const values = new Float32Array(
    latitudes.length *
      longitudes.length,
  );

  values.fill(NaN);

  const latIndex =
    new Map<number, number>();

  const lonIndex =
    new Map<number, number>();

  latitudes.forEach(
    (latitude, index) => {
      latIndex.set(
        latitude,
        index,
      );
    },
  );

  longitudes.forEach(
    (longitude, index) => {
      lonIndex.set(
        longitude,
        index,
      );
    },
  );

  /* -------------------------------------------------------
     Populate grid
  ------------------------------------------------------- */

  for (const point of points) {
    const row =
      latIndex.get(
        point.latitude,
      );

    const column =
      lonIndex.get(
        point.longitude,
      );

    if (
      row === undefined ||
      column === undefined
    ) {
      continue;
    }

    values[
      row * longitudes.length +
        column
    ] = point.value;
  }

  return {
    latitudes,
    longitudes,
    values,
  };
}

/* =========================================================
   Bilinear Interpolation
========================================================= */

function interpolateGrid(
  grid: BuiltGrid | null,
  latitude: number,
  longitude: number,
): number | null {
  if (!grid) {
    return null;
  }

  const {
    latitudes,
    longitudes,
    values,
  } = grid;

  /* -------------------------------------------------------
     Make sure point is inside data bounds
  ------------------------------------------------------- */

  if (
    latitude <
      latitudes[
        latitudes.length - 1
      ] ||
    latitude > latitudes[0] ||
    longitude < longitudes[0] ||
    longitude >
      longitudes[
        longitudes.length - 1
      ]
  ) {
    return null;
  }

  /* -------------------------------------------------------
     Latitude indices
  ------------------------------------------------------- */

  let latUpper = 0;

  while (
    latUpper <
      latitudes.length - 1 &&
    latitudes[latUpper] >
      latitude
  ) {
    latUpper++;
  }

  const latLower = Math.min(
    latUpper + 1,
    latitudes.length - 1,
  );

  /* -------------------------------------------------------
     Longitude indices
  ------------------------------------------------------- */

  let lonLower = 0;

  while (
    lonLower <
      longitudes.length - 1 &&
    longitudes[lonLower + 1] <
      longitude
  ) {
    lonLower++;
  }

  const lonUpper = Math.min(
    lonLower + 1,
    longitudes.length - 1,
  );

  /* -------------------------------------------------------
     Coordinates
  ------------------------------------------------------- */

  const lat1 =
    latitudes[latUpper];

  const lat2 =
    latitudes[latLower];

  const lon1 =
    longitudes[lonLower];

  const lon2 =
    longitudes[lonUpper];

  /* -------------------------------------------------------
     Four surrounding values
  ------------------------------------------------------- */

  const q11 =
    values[
      latUpper *
        longitudes.length +
        lonLower
    ];

  const q12 =
    values[
      latUpper *
        longitudes.length +
        lonUpper
    ];

  const q21 =
    values[
      latLower *
        longitudes.length +
        lonLower
    ];

  const q22 =
    values[
      latLower *
        longitudes.length +
        lonUpper
    ];

  if (
    !Number.isFinite(q11) ||
    !Number.isFinite(q12) ||
    !Number.isFinite(q21) ||
    !Number.isFinite(q22)
  ) {
    return null;
  }

  /* -------------------------------------------------------
     Interpolation fractions
  ------------------------------------------------------- */

  const latFraction =
    lat1 === lat2
      ? 0
      : (lat1 - latitude) /
        (lat1 - lat2);

  const lonFraction =
    lon1 === lon2
      ? 0
      : (longitude - lon1) /
        (lon2 - lon1);

  /* -------------------------------------------------------
     Bilinear interpolation
  ------------------------------------------------------- */

  const top =
    q11 +
    (q12 - q11) *
      lonFraction;

  const bottom =
    q21 +
    (q22 - q21) *
      lonFraction;

  return (
    top +
    (bottom - top) *
      latFraction
  );
}

/* =========================================================
   Canvas Climate Layer
========================================================= */

function ClimateCanvasLayer({
  data,
  variable,
}: {
  data: GridResponse | null;
  variable: ClimateVariable;
}) {
  const map = useMap();

  const canvasRef =
    useRef<HTMLCanvasElement | null>(
      null,
    );

  /* -------------------------------------------------------
     Build grid whenever data OR variable changes
  ------------------------------------------------------- */

  const grid = useMemo(
    () =>
      data
        ? buildGrid(
            data,
            variable,
          )
        : null,
    [data, variable],
  );

  /* -------------------------------------------------------
     Draw climate surface
  ------------------------------------------------------- */

  useEffect(() => {
    if (!grid) {
      return;
    }

    const canvas =
      L.DomUtil.create(
        "canvas",
        "climate-canvas-layer",
      ) as HTMLCanvasElement;

    canvas.style.pointerEvents =
      "none";

    canvas.style.position =
      "absolute";

    canvasRef.current =
      canvas;

    const pane =
      map.getPane(
        "overlayPane",
      );

    if (!pane) {
      return;
    }

    pane.appendChild(canvas);

    const draw = () => {
      const size =
        map.getSize();

      const devicePixelRatio =
        window.devicePixelRatio ||
        1;

      /* ---------------------------------------------------
         Canvas resolution
      --------------------------------------------------- */

      canvas.width =
        size.x *
        devicePixelRatio;

      canvas.height =
        size.y *
        devicePixelRatio;

      canvas.style.width =
        `${size.x}px`;

      canvas.style.height =
        `${size.y}px`;

      const ctx =
        canvas.getContext(
          "2d",
        );

      if (!ctx) {
        return;
      }

      ctx.setTransform(
        devicePixelRatio,
        0,
        0,
        devicePixelRatio,
        0,
        0,
      );

      ctx.clearRect(
        0,
        0,
        size.x,
        size.y,
      );

      /* ---------------------------------------------------
         India / ERA5 bounds

         ERA5 test dataset:
         Latitude 6 → 37
         Longitude 68 → 97.5
      --------------------------------------------------- */

      const bounds =
        map.getBounds();

      const north =
        Math.min(
          bounds.getNorth(),
          37,
        );

      const south =
        Math.max(
          bounds.getSouth(),
          6,
        );

      const west =
        Math.max(
          bounds.getWest(),
          68,
        );

      const east =
        Math.min(
          bounds.getEast(),
          97.5,
        );

      if (
        south >= north ||
        west >= east
      ) {
        return;
      }

      /* ---------------------------------------------------
         Render at reduced resolution.

         Browser interpolation creates the smooth
         continuous climate surface.
      --------------------------------------------------- */

      const resolution = 4;

      const startPoint =
        map.latLngToContainerPoint(
          [north, west],
        );

      const endPoint =
        map.latLngToContainerPoint(
          [south, east],
        );

      const xStart =
        Math.max(
          0,
          Math.floor(
            Math.min(
              startPoint.x,
              endPoint.x,
            ),
          ),
        );

      const yStart =
        Math.max(
          0,
          Math.floor(
            Math.min(
              startPoint.y,
              endPoint.y,
            ),
          ),
        );

      const xEnd =
        Math.min(
          size.x,
          Math.ceil(
            Math.max(
              startPoint.x,
              endPoint.x,
            ),
          ),
        );

      const yEnd =
        Math.min(
          size.y,
          Math.ceil(
            Math.max(
              startPoint.y,
              endPoint.y,
            ),
          ),
        );

      const imageWidth =
        Math.ceil(
          (xEnd - xStart) /
            resolution,
        );

      const imageHeight =
        Math.ceil(
          (yEnd - yStart) /
            resolution,
        );

      if (
        imageWidth <= 0 ||
        imageHeight <= 0
      ) {
        return;
      }

      const imageData =
        ctx.createImageData(
          imageWidth,
          imageHeight,
        );

      /* ---------------------------------------------------
         Variable-specific color configuration
      --------------------------------------------------- */

      const config =
        VARIABLE_CONFIG[
          variable
        ];

      /* ---------------------------------------------------
         Generate pixels
      --------------------------------------------------- */

      for (
        let py = 0;
        py < imageHeight;
        py++
      ) {
        for (
          let px = 0;
          px < imageWidth;
          px++
        ) {
          const screenX =
            xStart +
            px * resolution +
            resolution / 2;

          const screenY =
            yStart +
            py * resolution +
            resolution / 2;

          const latLng =
            map.containerPointToLatLng(
              [
                screenX,
                screenY,
              ],
            );

          const value =
            interpolateGrid(
              grid,
              latLng.lat,
              latLng.lng,
            );

          const pixelIndex =
            (py * imageWidth +
              px) *
            4;

          if (
            value === null
          ) {
            imageData.data[
              pixelIndex + 3
            ] = 0;

            continue;
          }

          const [
            r,
            g,
            b,
          ] =
            interpolateColor(
              value,
              config,
            );

          imageData.data[
            pixelIndex
          ] = r;

          imageData.data[
            pixelIndex + 1
          ] = g;

          imageData.data[
            pixelIndex + 2
          ] = b;

          imageData.data[
            pixelIndex + 3
          ] = 190;
        }
      }

      /* ---------------------------------------------------
         Temporary low-resolution canvas
      --------------------------------------------------- */

      const temporaryCanvas =
        document.createElement(
          "canvas",
        );

      temporaryCanvas.width =
        imageWidth;

      temporaryCanvas.height =
        imageHeight;

      const temporaryContext =
        temporaryCanvas.getContext(
          "2d",
        );

      if (
        !temporaryContext
      ) {
        return;
      }

      temporaryContext.putImageData(
        imageData,
        0,
        0,
      );

      /* ---------------------------------------------------
         Upscale smoothly
      --------------------------------------------------- */

      ctx.imageSmoothingEnabled =
        true;

      ctx.imageSmoothingQuality =
        "high";

      ctx.drawImage(
        temporaryCanvas,
        xStart,
        yStart,
        imageWidth *
          resolution,
        imageHeight *
          resolution,
      );
    };

    draw();

    map.on(
      "moveend zoomend resize",
      draw,
    );

    return () => {
      map.off(
        "moveend zoomend resize",
        draw,
      );

      canvas.remove();

      canvasRef.current =
        null;
    };
  }, [
    grid,
    map,
    variable,
  ]);

  return null;
}

/* =========================================================
   Map Click Handler
========================================================= */

function MapClickHandler({
  onLocationSelect,
}: {
  onLocationSelect: (
    latitude: number,
    longitude: number,
  ) => void;
}) {
  useMapEvents({
    click(event) {
      onLocationSelect(
        event.latlng.lat,
        event.latlng.lng,
      );
    },
  });

  return null;
}

/* =========================================================
   Dynamic Legend
========================================================= */

function ClimateLegend({
  variable,
}: {
  variable: ClimateVariable;
}) {
  const config =
    VARIABLE_CONFIG[
      variable
    ];

  const gradientStops =
    config.stops
      .map(
        (stop) =>
          `rgb(${stop.color[0]}, ${stop.color[1]}, ${stop.color[2]})`,
      )
      .join(", ");

  return (
    <div className="absolute bottom-6 left-6 z-[1000] w-80 rounded-2xl border border-white/10 bg-black/80 p-4 shadow-2xl backdrop-blur-xl">
      {/* -------------------------------------------------
         Header
      ------------------------------------------------- */}

      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-semibold text-white">
          {config.label}
        </span>

        <span className="text-xs text-white/60">
          {config.unit}
        </span>
      </div>

      {/* -------------------------------------------------
         Gradient
      ------------------------------------------------- */}

      <div
        className="h-3 w-full rounded-full"
        style={{
          background:
            `linear-gradient(to right, ${gradientStops})`,
        }}
      />

      {/* -------------------------------------------------
         Scale
      ------------------------------------------------- */}

      <div className="mt-1 flex justify-between text-[11px] text-white/60">
        <span>
          {config.min}
          {config.unit}
        </span>

        <span>
          {config.max}
          {config.unit}
        </span>
      </div>

      {/* -------------------------------------------------
         Dataset information
      ------------------------------------------------- */}

      <div className="mt-3 text-[11px] leading-relaxed text-white/50">
        ERA5 reanalysis • 0.25° grid
      </div>
    </div>
  );
}

/* =========================================================
   Layer Status
========================================================= */

function MapStatus({
  data,
  variable,
}: {
  data: GridResponse | null;
  variable: ClimateVariable;
}) {
  if (
    !data?.features?.length
  ) {
    return null;
  }

  const config =
    VARIABLE_CONFIG[
      variable
    ];

  const timestamp =
    data.metadata?.timestamp ??
    data.features[0]?.properties
      ?.timestamp;

  return (
    <div className="absolute right-6 top-6 z-[1000] rounded-2xl border border-white/10 bg-black/80 px-4 py-3 shadow-xl backdrop-blur-xl">
      {/* -------------------------------------------------
         Layer label
      ------------------------------------------------- */}

      <div className="text-[10px] uppercase tracking-[0.2em] text-cyan-400">
        Climate Layer
      </div>

      {/* -------------------------------------------------
         Variable
      ------------------------------------------------- */}

      <div className="mt-1 text-sm font-semibold text-white">
        {config.label}
      </div>

      {/* -------------------------------------------------
         Grid count
      ------------------------------------------------- */}

      <div className="mt-1 text-xs text-white/50">
        {data.features.length.toLocaleString()}{" "}
        grid cells
      </div>

      {/* -------------------------------------------------
         Dataset
      ------------------------------------------------- */}

      <div className="mt-1 text-xs text-white/40">
        {data.metadata?.source ??
          "ECMWF_CDS"}{" "}
        •{" "}
        {data.metadata?.dataset_id ??
          "era5_india_test"}
      </div>

      {/* -------------------------------------------------
         Timestamp
      ------------------------------------------------- */}

      {timestamp && (
        <div className="mt-1 text-xs text-white/40">
          {new Date(
            timestamp,
          ).toLocaleString()}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   Main Climate Map
========================================================= */

export default function ClimateMap({
  data,
  variable,
  onLocationSelect,
}: ClimateMapProps) {
  return (
    <div className="relative h-[650px] w-full overflow-hidden rounded-2xl border border-white/10">
      <MapContainer
        center={[22.5, 79]}
        zoom={6}
        minZoom={4}
        maxZoom={9}
        scrollWheelZoom
        className="h-full w-full"
      >
        {/* -------------------------------------------------
           Base Map
        ------------------------------------------------- */}

        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* -------------------------------------------------
           Continuous Climate Layer
        ------------------------------------------------- */}

        <ClimateCanvasLayer
          data={data}
          variable={variable}
        />

        {/* -------------------------------------------------
           Click Handler
        ------------------------------------------------- */}

        <MapClickHandler
          onLocationSelect={
            onLocationSelect
          }
        />
      </MapContainer>

      {/* ---------------------------------------------------
         Dynamic Legend
      --------------------------------------------------- */}

      <ClimateLegend
        variable={variable}
      />

      {/* ---------------------------------------------------
         Dynamic Layer Status
      --------------------------------------------------- */}

      <MapStatus
        data={data}
        variable={variable}
      />
    </div>
  );
}