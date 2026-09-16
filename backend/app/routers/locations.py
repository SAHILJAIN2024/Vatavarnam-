from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Locations"],
)


@router.get("/{latitude}/{longitude}")
def get_location_climate(
    latitude: float,
    longitude: float,
    timestamp: datetime | None = Query(
        default=None,
        description="Optional UTC timestamp. If omitted, the latest available timestamp is used.",
    ),
    db: Session = Depends(get_db),
):
    """
    Find the nearest ERA5 grid point to the requested location
    and return all available climate variables at that point.
    """

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

    # Find the nearest spatial point using PostGIS.
    nearest_point_query = text(
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
        nearest_point_query,
        {
            "latitude": latitude,
            "longitude": longitude,
        },
    ).mappings().first()

    if nearest is None:
        raise HTTPException(
            status_code=404,
            detail="No spatial climate observations found.",
        )

    nearest_latitude = nearest["latitude"]
    nearest_longitude = nearest["longitude"]
    distance_meters = float(nearest["distance_meters"])

    # Retrieve climate variables from the nearest grid point.
    if timestamp is None:
        observations_query = text(
            """
            SELECT
                timestamp,
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
              AND timestamp = (
                  SELECT MAX(timestamp)
                  FROM climate_observations
                  WHERE latitude = :latitude
                    AND longitude = :longitude
              )
            ORDER BY variable
            """
        )

        params = {
            "latitude": nearest_latitude,
            "longitude": nearest_longitude,
        }

    else:
        observations_query = text(
            """
            SELECT
                timestamp,
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

        params = {
            "latitude": nearest_latitude,
            "longitude": nearest_longitude,
            "timestamp": timestamp,
        }

    observations = db.execute(
        observations_query,
        params,
    ).mappings().all()

    if not observations:
        raise HTTPException(
            status_code=404,
            detail="No climate observations found for the nearest grid point.",
        )

    variables = {}

    for observation in observations:
        variables[observation["variable"]] = {
            "value": observation["value"],
            "unit": observation["unit"],
            "quality_flag": observation["quality_flag"],
            "spatial_resolution": observation["spatial_resolution"],
            "temporal_resolution": observation["temporal_resolution"],
        }

    return {
        "requested_location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "nearest_grid_point": {
            "latitude": nearest_latitude,
            "longitude": nearest_longitude,
            "distance_meters": round(distance_meters, 2),
        },
        "timestamp": observations[0]["timestamp"],
        "source": observations[0]["source"],
        "dataset_id": observations[0]["dataset_id"],
        "variables": variables,
    }