import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Climate Metrics"],
)


# ---------------------------------------------------------
# Unit conversions
# ---------------------------------------------------------

def kelvin_to_celsius(value: float) -> float:
    return value - 273.15


def pascal_to_hpa(value: float) -> float:
    return value / 100.0


def calculate_wind_speed(u: float, v: float) -> float:
    return math.sqrt(u**2 + v**2)


def calculate_wind_direction(u: float, v: float) -> float:
    """
    Meteorological wind direction:
    direction FROM which the wind is coming.

    0°   = North
    90°  = East
    180° = South
    270° = West
    """

    direction = (math.degrees(math.atan2(-u, -v)) + 360) % 360
    return direction


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@router.get("/{latitude}/{longitude}/metrics")
def get_location_metrics(
    latitude: float,
    longitude: float,
    timestamp: datetime | None = Query(
        default=None,
        description="UTC timestamp. If omitted, latest available timestamp is used.",
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve raw climate observations and calculate
    user-friendly derived climate metrics.
    """

    # -----------------------------------------------------
    # 1. Validate coordinates
    # -----------------------------------------------------

    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90.",
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180.",
        )

    # -----------------------------------------------------
    # 2. Find nearest spatial grid point
    # -----------------------------------------------------

    nearest_query = text(
        """
        SELECT
            latitude,
            longitude,
            ST_Distance(
                geometry::geography,
                ST_SetSRID(
                    ST_MakePoint(:longitude, :latitude),
                    4326
                )::geography
            ) AS distance_meters
        FROM climate_observations
        WHERE geometry IS NOT NULL
        ORDER BY geometry <-> ST_SetSRID(
            ST_MakePoint(:longitude, :latitude),
            4326
        )
        LIMIT 1
        """
    )

    nearest = db.execute(
        nearest_query,
        {
            "latitude": latitude,
            "longitude": longitude,
        },
    ).mappings().first()

    if nearest is None:
        raise HTTPException(
            status_code=404,
            detail="No climate grid point found.",
        )

    nearest_latitude = nearest["latitude"]
    nearest_longitude = nearest["longitude"]
    distance_meters = float(nearest["distance_meters"])

    # -----------------------------------------------------
    # 3. Determine timestamp
    # -----------------------------------------------------

    if timestamp is None:

        timestamp_query = text(
            """
            SELECT MAX(timestamp)
            FROM climate_observations
            WHERE latitude = :latitude
              AND longitude = :longitude
            """
        )

        selected_timestamp = db.execute(
            timestamp_query,
            {
                "latitude": nearest_latitude,
                "longitude": nearest_longitude,
            },
        ).scalar()

    else:
        selected_timestamp = timestamp

    if selected_timestamp is None:
        raise HTTPException(
            status_code=404,
            detail="No timestamp available for this location.",
        )

    # -----------------------------------------------------
    # 4. Retrieve observations
    # -----------------------------------------------------

    observations_query = text(
        """
        SELECT
            variable,
            value,
            unit,
            source,
            dataset_id,
            quality_flag,
            spatial_resolution,
            temporal_resolution
        FROM climate_observations
        WHERE latitude = :latitude
          AND longitude = :longitude
          AND timestamp = :timestamp
        ORDER BY variable
        """
    )

    observations = (
        db.execute(
            observations_query,
            {
                "latitude": nearest_latitude,
                "longitude": nearest_longitude,
                "timestamp": selected_timestamp,
            },
        )
        .mappings()
        .all()
    )

    if not observations:
        raise HTTPException(
            status_code=404,
            detail="No observations found for the requested timestamp.",
        )

    raw = {}

    for observation in observations:
        raw[observation["variable"]] = {
            "value": observation["value"],
            "unit": observation["unit"],
            "quality_flag": observation["quality_flag"],
            "spatial_resolution": observation["spatial_resolution"],
            "temporal_resolution": observation["temporal_resolution"],
        }

    # -----------------------------------------------------
    # 5. Calculate derived metrics
    # -----------------------------------------------------

    derived = {}

    # Temperature
    if "temperature_2m" in raw:
        temperature_k = raw["temperature_2m"]["value"]

        derived["temperature_2m"] = {
            "value": round(
                kelvin_to_celsius(temperature_k),
                2,
            ),
            "unit": "°C",
            "source_variable": "temperature_2m",
        }

    # Surface pressure
    if "surface_pressure" in raw:
        pressure_pa = raw["surface_pressure"]["value"]

        derived["surface_pressure"] = {
            "value": round(
                pascal_to_hpa(pressure_pa),
                2,
            ),
            "unit": "hPa",
            "source_variable": "surface_pressure",
        }

    # Wind
    if (
        "wind_u_10m" in raw
        and "wind_v_10m" in raw
    ):
        u = raw["wind_u_10m"]["value"]
        v = raw["wind_v_10m"]["value"]

        speed = calculate_wind_speed(u, v)
        direction = calculate_wind_direction(u, v)

        derived["wind_10m"] = {
            "speed": {
                "value": round(speed, 2),
                "unit": "m/s",
            },
            "direction": {
                "value": round(direction, 2),
                "unit": "degrees",
            },
            "components": {
                "u": {
                    "value": u,
                    "unit": "m/s",
                },
                "v": {
                    "value": v,
                    "unit": "m/s",
                },
            },
        }

    # Boundary layer
    if "boundary_layer_height" in raw:
        derived["boundary_layer_height"] = {
            "value": round(
                raw["boundary_layer_height"]["value"],
                2,
            ),
            "unit": "m",
            "source_variable": "boundary_layer_height",
        }

    # -----------------------------------------------------
    # 6. Return response
    # -----------------------------------------------------

    return {
        "location": {
            "requested": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "nearest_grid_point": {
                "latitude": nearest_latitude,
                "longitude": nearest_longitude,
                "distance_meters": round(
                    distance_meters,
                    2,
                ),
            },
        },
        "timestamp": selected_timestamp,
        "source": observations[0]["source"],
        "dataset_id": observations[0]["dataset_id"],
        "derived_metrics": derived,
        "raw_observations": raw,
    }