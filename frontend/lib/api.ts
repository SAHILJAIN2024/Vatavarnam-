const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface GridFeature {
  type: "Feature";
  geometry: {
    type: "Point";
    coordinates: [number, number];
  };
  properties: {
    id: number;
    latitude: number;
    longitude: number;
    variable: string;
    value: number;
    unit: string;
    source: string;
    dataset_id: string;
    quality_flag: string | null;
    spatial_resolution: string | null;
    temporal_resolution: string | null;
  };
}

export interface GridResponse {
  type: "FeatureCollection";
  metadata: {
    timestamp: string;
    variable: string | null;
    feature_count: number;
    source: string;
    dataset_id: string;
    spatial_resolution: string | null;
    temporal_resolution: string | null;
  };
  features: GridFeature[];
}

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

export async function getClimateGrid(
  variable: string,
): Promise<GridResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/map/grid?variable=${encodeURIComponent(variable)}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to load climate grid.");
  }

  return response.json();
}

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
    throw new Error("Failed to load climate metrics.");
  }

  return response.json();
}

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
    throw new Error("Failed to load climate time series.");
  }

  return response.json();
}