const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

/* ======================================================
   Climate Variables
====================================================== */

export type ClimateVariable =
  | "temperature_2m"
  | "surface_pressure"
  | "wind_speed"
  | "wind_u_10m"
  | "wind_v_10m"
  | "boundary_layer_height";

/* ======================================================
   Climate Grid
====================================================== */

export interface GridFeature {
  type: "Feature";

  geometry: {
    type: "Point";
    coordinates: [number, number];
  };

  properties: {
    id?: number;
    latitude: number;
    longitude: number;
    variable: string;
    value: number;
    unit: string;
    source: string;
    dataset_id: string;
    timestamp?: string;
    quality_flag: string | null;
    spatial_resolution: string | null;
    temporal_resolution: string | null;
  };
}

export interface GridResponse {
  type: "FeatureCollection";

  metadata: {
    timestamp: string | null;
    variable: string | null;
    feature_count?: number;
    source: string;
    dataset_id: string;
    spatial_resolution?: string | null;
    temporal_resolution?: string | null;
    derived?: boolean;
    unit?: string | null;
  };

  features: GridFeature[];
}

/* ======================================================
   Climate Metrics
====================================================== */

export interface ClimateMetric {
  value: number;
  unit: string;
  source_variable?: string;
}

export interface WindMetric {
  speed: {
    value: number;
    unit: string;
  };

  direction: {
    value: number;
    unit: string;
  };

  components: {
    u: {
      value: number;
      unit: string;
    };

    v: {
      value: number;
      unit: string;
    };
  };
}

export interface MetricsResponse {
  location: {
    requested: {
      latitude: number;
      longitude: number;
    };

    nearest_grid_point: {
      latitude: number;
      longitude: number;
      distance_meters: number;
    };
  };

  timestamp: string;

  source: string;

  dataset_id: string;

  derived_metrics: {
    temperature_2m?: ClimateMetric;
    surface_pressure?: ClimateMetric;
    wind_10m?: WindMetric;
    boundary_layer_height?: ClimateMetric;
  };

  raw_observations: Record<
    string,
    {
      value: number;
      unit: string;
      quality_flag: string | null;
      spatial_resolution: string | null;
      temporal_resolution: string | null;
    }
  >;
}

/* ======================================================
   Time Series
====================================================== */

export interface TimeSeriesObservation {
  value: number;
  unit: string;
  quality_flag: string | null;
  spatial_resolution: string | null;
  temporal_resolution: string | null;
}

export interface TimeSeriesResponse {
  requested_location: {
    latitude: number;
    longitude: number;
  };

  nearest_grid_point: {
    latitude: number;
    longitude: number;
    distance_meters: number;
  };

  source: string;

  dataset_id: string;

  start_time: string;

  end_time: string;

  observation_count: number;

  time_points: number;

  variables: string[];

  time_series: Record<
    string,
    Record<string, TimeSeriesObservation>
  >;
}

/* ======================================================
   API Error Helper
====================================================== */

async function getErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data = await response.json();

    if (
      data?.detail?.message
    ) {
      return data.detail.message;
    }

    if (
      typeof data?.detail === "string"
    ) {
      return data.detail;
    }

    return fallback;
  } catch {
    return fallback;
  }
}

/* ======================================================
   Climate Grid API
====================================================== */

export async function getClimateGrid(
  variable: ClimateVariable = "temperature_2m",
): Promise<GridResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/map/grid?variable=${encodeURIComponent(
      variable,
    )}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(
        response,
        "Failed to load climate grid.",
      );

    throw new Error(message);
  }

  return response.json();
}

/* ======================================================
   Climate Metrics API
====================================================== */

export async function getClimateMetrics(
  latitude: number,
  longitude: number,
): Promise<MetricsResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/locations/${latitude}/${longitude}/metrics`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(
        response,
        "Failed to load climate metrics.",
      );

    throw new Error(message);
  }

  return response.json();
}

/* ======================================================
   Climate Time Series API
====================================================== */

export async function getClimateTimeSeries(
  latitude: number,
  longitude: number,
): Promise<TimeSeriesResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/locations/${latitude}/${longitude}/timeseries`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(
        response,
        "Failed to load climate time series.",
      );

    throw new Error(message);
  }

  return response.json();
}